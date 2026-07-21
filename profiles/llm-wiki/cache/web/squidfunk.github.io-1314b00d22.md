[Skip to content](https://squidfunk.github.io/mkdocs-material/blog/2025/11/05/zensical/#zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team)

[Edit this page](https://github.com/squidfunk/mkdocs-material/edit/master/docs/blog/posts/zensical.md "Edit this page") [View source of this page](https://github.com/squidfunk/mkdocs-material/raw/master/docs/blog/posts/zensical.md "View source of this page")

# Zensical – A modern static site generator built by the Material for MkDocs team [¶](https://squidfunk.github.io/mkdocs-material/blog/2025/11/05/zensical/\#zensical-a-modern-static-site-generator-built-by-the-material-for-mkdocs-team "Permanent link")

**We are thrilled to announce [Zensical](https://zensical.org/), our next-gen static site generator designed to simplify the process of building documentation sites. Distilled from a decade of experience, Zensical is our effort to overcome the technical limitations of MkDocs, reaching far beyond its capabilities.**

Zensical is the result of thousands of hours of work – built from the ground up for a modern and comfortable authoring experience, while making it easy for developers to extend and customize Zensical through its upcoming module system. Our goal is to support docs-as-code workflows with tens of thousands of pages, without compromising performance or usability.

To make the transition seamless, [compatibility](https://squidfunk.github.io/mkdocs-material/blog/2025/11/05/zensical/#maximum-compatibility) comes first. We're putting significant effort into ensuring a smooth migration from Material for MkDocs for all users. Zensical can natively read `mkdocs.yml`, allowing you to build your existing project with minimal changes. As of now, a subset of plugins is supported, and we're working on feature parity in the coming months.

Zensical is fully Open Source, licensed under MIT, and can be used for any purpose, including for commercial use. We're also saying goodbye to our sponsorware model, replacing it with our new offering for professional users: [Zensical Spark](https://zensical.org/spark/). This allows us to stay independent, maximizing user value, as we shape the future of Zensical together with you.

_You can subscribe to [our newsletter](https://zensical.org/about/newsletter/) to stay in the loop_.

* * *

**This is the second article in a series:**

1. [Transforming Material for MkDocs](https://squidfunk.github.io/mkdocs-material/blog/2024/08/19/how-were-transforming-material-for-mkdocs/)
2. [Zensical – A modern static site generator built by the creators of Material for MkDocs](https://squidfunk.github.io/mkdocs-material/blog/2025/11/05/zensical/)
3. [Material for MkDocs Insiders – Now free for everyone](https://squidfunk.github.io/mkdocs-material/blog/2025/11/11/insiders-now-free-for-everyone/)
4. [Goodbye, GitHub Discussions](https://squidfunk.github.io/mkdocs-material/blog/2025/11/18/goodbye-github-discussions/)
5. [What MkDocs 2.0 means for your documentation projects](https://squidfunk.github.io/mkdocs-material/blog/2026/02/18/mkdocs-2.0/)

## Why Zensical? [¶](https://squidfunk.github.io/mkdocs-material/blog/2025/11/05/zensical/\#why-zensical "Permanent link")

Since its initial release in 2016, Material for MkDocs has helped tens of thousands of teams to publish and maintain reliable documentation. However, in recent years, it has become apparent that we were running up against limitations of our core dependency, MkDocs. These limitations proved impossible to overcome as they are deeply rooted in its architecture.

We also mentioned in our [update on our foundational work](https://github.com/squidfunk/mkdocs-material/discussions/8461) that MkDocs must be considered a supply chain risk, since it's unmaintained since August 2024. It has seen no releases in over a year and is accumulating unresolved issues and pull requests. These developments have forced us to cut our ties to MkDocs as a dependency.

In order to map out a path forward, we went back to the drawing board, talked to dozens of our professional users and thoroughly analyzed the MkDocs ecosystem. We didn't just want to create a fork or port of MkDocs, but decided to rethink static site generation from first principles.

With Zensical, we are creating a modern static site generator, which is compatible with your content and customizations, and addresses MkDocs' limitations. While Material for MkDocs is built on top of MkDocs, **Zensical consolidates both projects into one coherent stack**, covering static site generation, theming, and customization. What you can expect today:

- [5x faster rebuilds](https://squidfunk.github.io/mkdocs-material/blog/2025/11/05/zensical/#authoring-experience)
- [Modern design](https://squidfunk.github.io/mkdocs-material/blog/2025/11/05/zensical/#modern-design)
- [Blazing-fast search](https://squidfunk.github.io/mkdocs-material/blog/2025/11/05/zensical/#blazing-fast-search)

Although we haven't reached full feature parity yet, you can already use Zensical to build your existing Material for MkDocs projects with minimal changes.

_You can jump to the [compatibility](https://squidfunk.github.io/mkdocs-material/blog/2025/11/05/zensical/#maximum-compatibility) section to learn what is already supported._

## What you can expect [¶](https://squidfunk.github.io/mkdocs-material/blog/2025/11/05/zensical/\#what-you-can-expect "Permanent link")

### Solid foundation [¶](https://squidfunk.github.io/mkdocs-material/blog/2025/11/05/zensical/\#solid-foundation "Permanent link")

Our goal with Zensical is to create a coherent and modern stack, vertically integrating all parts of the authoring experience (AX), developer experience (DX), and user experience (UX). This gives us a significant competitive advantage over solutions that overly rely on third-party frameworks and dependencies, helping us to create much more robust Open Source software.

[ZRX](https://github.com/zensical/zrx/), our new differential build engine, creates a solid foundation for Zensical, and is an Open Source project of its own. It's a fresh take on making differential data flows easy to build and a joy to work with. Most engineering effort has gone into ZRX, as it forms the backbone of Zensical, and will allow us to ship features faster.

Following the principle of architectural hoisting, we moved essential, reusable functionality into ZRX, which allows us to keep Zensical's core simple and focused on static site generation. ZRX handles the heavy lifting – differential builds, caching, and data flow orchestration.

With the upcoming [module system](https://zensical.org/about/roadmap/#module-system) and [component system](https://zensical.org/about/roadmap/#component-system), both of which are on our public [roadmap](https://zensical.org/about/roadmap/), Zensical will gain more degrees of freedom in the coming months, allowing you to extend and customize Zensical in ways that were previously impossible with MkDocs.

### Modern design [¶](https://squidfunk.github.io/mkdocs-material/blog/2025/11/05/zensical/\#modern-design "Permanent link")

Zensical brings a fresh, modern design that breaks out of the Materal Design aesthetic, creating a visual foundation that is more easily brandable and adaptable to different use cases. The new design prioritizes clarity, simplicity, and usability, while having a more professional finish:

![Zensical](https://squidfunk.github.io/mkdocs-material/blog/zensical/screenshot.png#gh-light-mode-only)![Zensical](https://squidfunk.github.io/mkdocs-material/blog/zensical/screenshot-dark.png#gh-dark-mode-only)

Our public [roadmap](https://zensical.org/about/roadmap/), built with Zensical

Right now, the layout and site structure of Zensical match Material for MkDocs closely, as we're focusing on ensuring maximum compatibility. Once we finish work on our upcoming [component system](https://zensical.org/about/roadmap/#component-system), we'll provide an alternative that is much more flexible and adaptable, and can be tailored to different use cases and branding requirements more easily.

_You can also keep the Material for MkDocs look and feel with a single line of configuration._

### Blazing-fast search [¶](https://squidfunk.github.io/mkdocs-material/blog/2025/11/05/zensical/\#blazing-fast-search "Permanent link")

Client-side search isn't a compromise – for the vast majority of static sites, it's the best solution, since it's faster, involves zero maintenance, and doesn't require you to pay for a service.

As covered in depth in [the first part of this series](https://squidfunk.github.io/mkdocs-material/blog/2024/08/19/how-were-transforming-material-for-mkdocs/#search-and-discovery), the current search implementation in Material for MkDocs has severe limitations, and is based on a now unmaintained library, which is why we decided to build a new search engine from scratch. It's based on the same goals as Zensical itself: performance, flexibility, and extensibility.

Disco, our modular and blazing-fast client-side search engine, is exclusively available in Zensical. When you build your site with Zensical, your users will immediately benefit from Disco's improved ranking algorithm, as well as its filtering and aggregation capabilities:

![Zensical](https://squidfunk.github.io/mkdocs-material/blog/zensical/screenshot-search.png#gh-light-mode-only)![Zensical](https://squidfunk.github.io/mkdocs-material/blog/zensical/screenshot-search-dark.png#gh-dark-mode-only)

Disco on [zensical.org](https://zensical.org/)

We'll release Disco as an MIT-licensed standalone Open Source project soon. With the feedback of our professional users in [Zensical Spark](https://zensical.org/spark/), we're going to evolve the search experience, turning Disco into a highly configurable and customizable search engine that adapts to your needs.

_You can subscribe to [our newsletter](https://zensical.org/about/newsletter/) to receive news about Disco_.

### Authoring experience [¶](https://squidfunk.github.io/mkdocs-material/blog/2025/11/05/zensical/\#authoring-experience "Permanent link")

Slow feedback loops can be a major pain point when writing documentation. Almost all of us know the feeling of waiting for the static site generator to finish building the site, just to see a small change reflected in the output. With Zensical, we're finally addressing this issue.

It's important to understand that we're not yet utilizing the differential capabilities of [ZRX](https://github.com/zensical/zrx/) to the fullest extent, as we're forced to make several compromises to ensure maximum [compatibility](https://squidfunk.github.io/mkdocs-material/blog/2025/11/05/zensical/#maximum-compatibility) with Material for MkDocs at the moment. Markdown rendering needs to go through Python Markdown, which forces us to pay for extra marshalling costs.

While the initial build can sometimes be slower than with MkDocs, repeated builds – especially when serving the site – are already 4 to 5x faster, as only changed files need to be rebuilt.

We're also working on a new Markdown toolchain based on a CommonMark-compliant parser written in Rust, which will make Markdown processing significantly faster. We'll be tackling this as part of the upcoming [component system](https://zensical.org/about/roadmap/#component-system), which we'll start working on in early 2026. Once our new Markdown toolchain is ready, we'll provide automated tools to translate between Python Markdown and CommonMark, so you don't need to manually migrate your content.

### Maximum compatibility [¶](https://squidfunk.github.io/mkdocs-material/blog/2025/11/05/zensical/\#maximum-compatibility "Permanent link")

[Compatibility with Material for MkDocs](https://zensical.org/compatibility/) is our top priority. We understand that switching to a new static site generator can be challenging, especially for large projects with many customizations. Therefore, we've put significant effort into ensuring that Zensical understands `mkdocs.yml` configuration files, so that you can build your projects with minimal changes.

This means your existing Markdown files, template overrides, CSS and JavaScript extensions don't need to be touched, primarily because we did not change the generated HTML, and rely on Python Markdown for processing your content.

However, plugins are a different story. In MkDocs, practically all plugins have side effects, making it impossible to parallelize builds. We started from first principles and asked: what should extensibility look like in a modern static site generator? Our answer is the upcoming [module system](https://zensical.org/about/roadmap/#module-system), which takes a fundamentally different approach based on four core principles:

- Modules can inject, extend, and re-define functionality
- Modules are deterministic through topological ordering
- Modules foster reusability, with the possibility to remix them
- Modules can cooperate through well-defined contracts

We're working on shipping essential functionality as provided by MkDocs plugins as built-in modules. In early 2026, we will open the module system to third-party developers, so they can start building their own modules, as we see Zensical as the heart of a thriving ecosystem.

## Zensical Spark [¶](https://squidfunk.github.io/mkdocs-material/blog/2025/11/05/zensical/\#zensical-spark "Permanent link")

Material for MkDocs was originally built for individual developers and small teams, but over the years it found its way into the workflows of large organizations and professional documentation teams – far beyond what we ever anticipated. With that came a new set of requirements: scalability, dedicated support, and a direct line to the team behind the project.

[Zensical Spark](https://zensical.org/spark/) is our answer to that. Rather than building software that organizations need to adapt to, we built Zensical from the ground up around the needs of professional teams – handling documentation of any size, seamlessly, out of the box.

As a Spark member, you get [early access to new features](https://zensical.org/spark/tiers/#early-access-to-new-features), [hands-on migration support](https://zensical.org/spark/tiers/#hands-on-migration-support), and [direct access to the Zensical team](https://zensical.org/spark/tiers/#access-to-the-zensical-team). Your participation in Zensical Spark directly shapes the direction of the project, and your financial contribution ensures that we can continue to develop and maintain Zensical as a set of OSI-compliant Open Source projects.

[Learn more about Zensical Spark](https://zensical.org/spark/) or reach out to us at [members@zensical.org](mailto:members@zensical.org).

_Zensical is built for everyone – individual developers, small teams, and large organizations alike. Zensical Spark provides you with dedicated support from the team that built Material for MkDocs for the last decade, ensuring Zensical adapts to your organization as you grow._

## We're growing our team [¶](https://squidfunk.github.io/mkdocs-material/blog/2025/11/05/zensical/\#were-growing-our-team "Permanent link")

We're also excited to announce that we're growing [our team](https://zensical.org/about/team/):

**Timothée Mazzucotelli, also known as [@pawamoy](https://github.com/pawamoy "GitHub User: pawamoy"), is joining Zensical!**

At Zensical, Tim is focusing on providing the same seamless experience for generating API reference documentation from source code (via docstrings) as he has done with [mkdocstrings](https://mkdocstrings.github.io/), the second biggest project in the MkDocs ecosystem. With his expertise, and Zensical's new stack, we'll be pushing the boundaries of what's possible with API reference documentation.

## Goodbye, GitHub Sponsors [¶](https://squidfunk.github.io/mkdocs-material/blog/2025/11/05/zensical/\#goodbye-github-sponsors "Permanent link")

Thank you! To all of you who have supported us over the years through GitHub Sponsors – we are incredibly grateful for your support. It has been invaluable in helping us to build, maintain and evolve Material for MkDocs, and we couldn't have done it without you. **Seriously, thank you!**

Material for MkDocs gave us something invaluable: experience building for tens of thousands of users, and the opportunity to build a team around Open Source software. It showed us that making a living from Open Source isn't just possible – we grew it into one of the largest sponsorware projects on GitHub and inspired others to pursue similar paths.

Now we're breaking new ground. Zensical is our next chapter, and we're professionalizing how we approach Open Source development. Our vision is to make Zensical free for everyone to use while building a sustainable business around it through \[our new approach\].

This transition means saying goodbye to GitHub Sponsors. It has served us exceptionally well, but as we professionalize and scale, we're making the leap from personal project to company – building a business and team that can meet the growing demands of professional users while staying true to our values.

We're doubling down on Open Source, developing software for everyone.

_If you want to continue supporting our work, please subscribe to [our newsletter](https://zensical.org/about/newsletter/). We'll be providing new methods to support us in the coming months, with the possibility of getting exclusive goodies._

## Looking Ahead [¶](https://squidfunk.github.io/mkdocs-material/blog/2025/11/05/zensical/\#looking-ahead "Permanent link")

Material for MkDocs grew organically like a plant in a pot that eventually became too small. With Zensical, we're building on solid foundations designed to grow with us – and with you.

Material for MkDocs is in maintenance mode

We want to be transparent about the risks of staying on Material for MkDocs or on forks of both Material for MkDocs and MkDocs. With MkDocs 1.x unmaintained and facing fundamental supply chain concerns, its future is uncertain and we cannot guarantee Material for MkDocs will continue working reliably. MkDocs 2.0 will introduce breaking changes – something we [analyzed thoroughly in our MkDocs 2.0 article](https://squidfunk.github.io/mkdocs-material/blog/2026/02/18/mkdocs-2.0/).

We're aware that transitioning takes time, which is why we commit to supporting Material for MkDocs for at least the next 12 months, fixing critical bugs and security vulnerabilities as needed. If you have questions about your specific situation or need help planning a migration, don't hesitate to reach out at [hello@zensical.org](mailto:hello@zensical.org).

### Where we'll be in 12 months [¶](https://squidfunk.github.io/mkdocs-material/blog/2025/11/05/zensical/\#where-well-be-in-12-months "Permanent link")

Over the next 12 months, following our [phased transition strategy](https://zensical.org/compatibility/#phased-transition-strategy), we'll reach Phase 2 and 3 – introducing our [module system](https://zensical.org/about/roadmap/#module-system) and [component system](https://zensical.org/about/roadmap/#component-system), as well as CommonMark support. By replacing Python Markdown with a Rust-based Markdown parser, we'll unlock performance improvements and the modularity needed for flexible templating. This is where Zensical truly starts to unfold its capabilities.

Zensical is already powering real projects due to extensive [compatibility with Material for MkDocs](https://zensical.org/compatibility/). We're actively working on closing the gap to reach full [feature parity](https://zensical.org/compatibility/features/).

You can [install Zensical now](https://zensical.org/docs/get-started/), and build your existing Material for MkDocs projects with it. If you run into a bug, please don't hesitate to [open an issue](https://zensical.org/docs/community/get-involved/) – we're here to help.

### Connect with us [¶](https://squidfunk.github.io/mkdocs-material/blog/2025/11/05/zensical/\#connect-with-us "Permanent link")

If you have questions we haven't addressed, please reach out to us at [hello@zensical.org](mailto:hello@zensical.org). We're currently collecting questions from the community about Zensical, and will address them in an FAQ section as part of our documentation in the coming weeks.

We're incredibly thankful that you have been part of our journey so far. With Zensical, we're embarking on a new chapter, and we couldn't be more excited to have you with us.

_You can subscribe to [our newsletter](https://zensical.org/about/newsletter/) to stay in the loop_.

Back to top