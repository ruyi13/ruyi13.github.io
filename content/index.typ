#import "../config.typ": template, tufted
#show: template.with(
  title: "如一｜人工智能安全与网络安全",
  website-title: "如一 · 研究与笔记",
  author: "如一",
  description: "如一的个人主页。关注人工智能安全与网络安全，记录学习、研究与实践中的思考。",
  website-url: "https://ruyi13.github.io/",
  image-path: "/imgs/ruyi-ink-landscape.png",
  css: ("/assets/custom.css", "/assets/home.css"),
  header-links: (
    "/": "首页",
    "/Blog/": "笔记",
    "https://github.com/ruyi13": "GitHub",
  ),
  header-elements: (
    html.a(class: "home-brand", href: "/", [如一 #html.span[研究与笔记]]),
  ),
  footer-elements: (
    [© 2026 如一 · #link("https://github.com/ruyi13")[ruyi13]],
  ),
)

#html.div(class: "ruyi-home", [
  #html.div(class: "home-opening", [
    #html.div(class: "home-intro", [
      #html.p(class: "home-eyebrow", [人工智能安全 / 网络安全])

      #html.h1[如一]

      #html.p(class: "home-lead", [在复杂系统中，\ 寻找可信的边界。])

      你好，我是如一。我的研究方向是人工智能安全与网络安全。这里用来记录学习中的问题、研究中的思考，以及动手实践的过程。

      #html.p(class: "home-actions", [
        #link("/Blog/")[阅读笔记 →]
        #link("https://github.com/ruyi13")[访问 GitHub ↗]
      ])
    ])
    #html.div(class: "home-art", [
      #image("imgs/ruyi-ink-landscape.png", alt: "宣纸底色上的淡墨山水，远山与水面之间留有大片空白，细微连接点融入山线。")
      #html.p(class: "home-art-caption", [山水有留白，思考有余地。])
    ])
  ])

  #html.div(class: "home-research", [
    #html.p(class: "home-section-label", [所思 · 研究方向])
    #html.div(class: "home-research-grid", [
      #html.div(class: "home-research-item", [
        #html.p(class: "home-number", [01])
        #html.h2[人工智能安全]

        当模型能力不断增长，如何理解它的局限、评估它的风险，并让它在真实场景中可靠运行？我希望围绕这些问题，逐步积累理解与实践。
      ])
      #html.div(class: "home-research-item", [
        #html.p(class: "home-number", [02])
        #html.h2[网络安全]

        从系统、网络到应用，安全往往藏在具体的边界与细节中。我关注这些边界如何被建立、被检验，以及如何在持续变化的环境中得到维护。
      ])
    ])
  ])

  #html.div(class: "home-notebook", [
    #html.p(class: "home-section-label", [所记 · 个人笔记])
    #html.h2[把问题写下来，把理解留下来。]

    学习与研究总会留下值得回看的片段：一个概念的来龙去脉，一次实验的观察，或一个暂时没有答案的问题。我想把它们整理在这里，让零散的思考慢慢连成线。

    #html.p(class: "home-notebook-link", [#link("/Blog/")[前往笔记 →]])
  ])
])
