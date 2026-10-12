"""Exercise live preview with the real compiler and HTTP server in isolation."""
import json
from contextlib import contextmanager
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys
import time
import unittest
import uuid
from urllib.error import URLError
from urllib.request import urlopen


@contextmanager
def isolated_workspace(workspace):
    root = workspace / "target" / f"live-preview-{uuid.uuid4().hex}"
    root.mkdir(parents=True)
    try:
        yield root
    finally:
        assert root.resolve().is_relative_to((workspace / "target").resolve())
        shutil.rmtree(root)


@unittest.skipUnless(shutil.which("typst"), "Typst CLI is required")
class LivePreviewTest(unittest.TestCase):
    def test_saved_files_and_error_recovery(self):
        workspace = Path(__file__).resolve().parents[1]
        temporary_root = workspace / "target"
        temporary_root.mkdir(exist_ok=True)
        with isolated_workspace(workspace) as root:
            assert root.resolve().is_relative_to(workspace)
            shutil.copy2(workspace / "build.py", root / "build.py")
            for name in ("content", "assets", "tufted-lib"):
                (root / name).mkdir()
            (root / "config.typ").write_text("", encoding="utf-8")
            shared = root / "tufted-lib/shared.typ"
            shared.write_text('#let message = [Shared original.]', encoding="utf-8")
            source = root / "content/index.typ"
            initial = '#import "../tufted-lib/shared.typ": message\n#message\nOriginal page. @entry\n#bibliography("refs.bib")'
            source.write_text(initial, encoding="utf-8")
            bib = root / "content/refs.bib"
            bib.write_text('@book{entry, title={Original Book}, author={Tester, Example}, year={2025}}', encoding="utf-8")
            css = root / "assets/test.css"
            css.write_text("body { color: black; }", encoding="utf-8")
            with socket.socket() as port_probe:
                port_probe.bind(("127.0.0.1", 0))
                port = port_probe.getsockname()[1]
            url = f"http://127.0.0.1:{port}"
            with (root / "server.log").open("w", encoding="utf-8") as log:
                process = subprocess.Popen(
                    [sys.executable, "-u", str(root / "build.py"), "watch", "--no-open", "-p", str(port)],
                    stdout=log, stderr=log, env={**os.environ, "PYTHONIOENCODING": "utf-8"},
                )
                try:
                    def get(path):
                        with urlopen(url + path, timeout=2) as response:
                            return response.read().decode("utf-8")

                    def wait_for(predicate):
                        deadline = time.monotonic() + 30
                        while time.monotonic() < deadline:
                            try:
                                value = predicate()
                                if value:
                                    return value
                            except (URLError, TimeoutError):
                                pass
                            if process.poll() is not None:
                                break
                            time.sleep(0.1)
                        self.fail((root / "server.log").read_text(encoding="utf-8"))

                    def status():
                        return json.loads(get("/__preview__/status"))

                    def save_and_wait(path, text, error=False):
                        previous = status()["revision"]
                        path.write_text(text, encoding="utf-8")
                        def changed_status():
                            data = status()
                            return data if data["revision"] != previous else None
                        updated = wait_for(changed_status)
                        self.assertEqual(updated["error"], error)

                    wait_for(lambda: "Original page." in get("/"))
                    html = get("/")
                    self.assertIn("data-typst-live-preview", html)
                    self.assertNotIn("data-typst-live-preview", (root / "_site/index.html").read_text(encoding="utf-8"))
                    if shutil.which("node"):
                        script = re.search(r'<script data-typst-live-preview>(.*?)</script>', html, re.S).group(1)
                        node_check = """
const assert = require('node:assert/strict');
const vm = require('node:vm');
const source = require('node:fs').readFileSync(0, 'utf8');
const revision = source.match(/const revision = "([^"]+)"/)[1];
const timers = [], notices = [];
let reloads = 0, status = { revision, error: false };
vm.runInNewContext(source, {
  fetch: async (path) => {
    assert.equal(path, '/__preview__/status');
    return {ok: true, json: async () => status};
  },
  setTimeout: fn => timers.push(fn),
  location: {reload: () => reloads++},
  document: {getElementById: () => null, createElement: () => ({setAttribute() {}, style: {}}),
             body: {appendChild: element => notices.push(element)}},
});
(async () => {
  await new Promise(setImmediate);
  assert.equal(reloads, 0);
  status = {revision, error: true};
  await timers.shift()();
  assert.equal(notices.length, 1);
  status = {revision: 'updated', error: false};
  await timers.shift()();
  assert.equal(reloads, 1);
})().catch(error => {console.error(error); process.exitCode = 1;});
"""
                        result = subprocess.run(["node", "-e", node_check], input=script,
                                                text=True, encoding="utf-8", capture_output=True)
                        self.assertEqual(result.returncode, 0, result.stderr)

                    save_and_wait(source, initial.replace("Original page.", "Updated page."))
                    self.assertIn("Updated page.", get("/"))
                    save_and_wait(shared, '#let message = [Shared updated.]')
                    self.assertIn("Shared updated.", get("/"))
                    save_and_wait(bib, '@book{entry, title={Updated Book}, author={Tester, Example}, year={2025}}')
                    self.assertIn("Updated Book", get("/"))
                    save_and_wait(css, "body { color: green; }")
                    self.assertIn("green", get("/assets/test.css"))
                    new_page = root / "content/Blog/new/index.typ"
                    new_page.parent.mkdir(parents=True)
                    save_and_wait(new_page, "New blog page.")
                    self.assertIn("New blog page.", get("/Blog/new/"))
                    image = root / "content/test.svg"
                    save_and_wait(image, '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10"></svg>')
                    self.assertIn("<svg", get("/test.svg"))
                    save_and_wait(source, "#missing_function()", error=True)
                    self.assertIn("Updated page.", get("/"))
                    save_and_wait(source, initial.replace("Original page.", "Recovered page."))
                    self.assertIn("Recovered page.", get("/"))
                finally:
                    process.terminate()
                    process.wait(timeout=10)


if __name__ == "__main__":
    unittest.main()
