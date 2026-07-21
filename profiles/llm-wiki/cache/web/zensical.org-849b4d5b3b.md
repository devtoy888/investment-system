[Skip to content](https://zensical.org/about/roadmap/#roadmap)

# Roadmap [¶](https://zensical.org/about/roadmap/\#roadmap "Permanent link")

We are building Zensical as a _vertically integrated set of systems_, which
allows us to rethink all aspects of the authoring (AX), developer (DX) and
user experience (UX), as we aim to deliver a comprehensive, coherent and
expanding set of well-integrated solutions.

Our roadmap serves to make the overall trajectory of the project transparent to
our users, and to help us prioritize high-value items to work on. Rather than
promising concrete dates, we prefer to make our work visible so you can track
progress. As a member of [Zensical Spark](https://zensical.org/spark/), you can directly influence our
priorities and roadmap as an integral partner in [our design process](https://zensical.org/docs/community/how-we-work/).

_The items on this roadmap do not have a strict ordering or implied dates of_
_completion._

Zensical Studio Roadmap

With the release of [Zensical Studio](https://zensical.org/studio/), we are delivering on our
promise of a best-in-class authoring exprience. It allows you
to catch broken links instantly as you edit your content, keeps
references up-to-date as you make changes, provides convenient
navigation, auto-completion, and more. See the [roadmap for\\
Zensical Studio](https://zensical.org/studio/about/roadmap/) for details on the functionality we are planning.

Want to stay in the loop?

Join **Zensical Monthly**, [our newsletter](https://zensical.org/about/newsletter/) – every month, we share what we've shipped, what we're working on, and what's happening in the ecosystem. Honest updates, straight from the team.

## Foundation [¶](https://zensical.org/about/roadmap/\#foundation "Permanent link")

This section explores the core principles that are the foundation of Zensical.
These aspects are crucial to understanding its characteristics and underlying
philosophy.

_Zensical is currently alpha software and we are iterating rapidly. In the first_
_months, we will be weeding out any remaining bugs in the initial implementation_
_and work towards [feature parity](https://zensical.org/about/roadmap/#feature-parity) with Material for MkDocs. We invite you to_
_review our [feature parity table](https://zensical.org/compatibility/features/) for a detailed breakdown._

### Rust runtime [¶](https://zensical.org/about/roadmap/\#rust-runtime "Permanent link")

The most important but least visible feature of Zensical is our _next-generation_
_architecture and runtime_ [ZRX](https://github.com/zensical/zrx), that fundamentally redefines how static sites
are built.

Rather than going the easy route of just porting MkDocs to Rust, we've invested
thousands of hours, building a robust and efficient system from the ground up to
address core limitations that have severely limited the progress we could make
with Material for MkDocs' in the past years.

**Key goals**

- **Differential builds** \- Unlike traditional incremental builds that
rebuild entire dependency chains when any file changes and sometimes
yield incorrect results, our differential
runtime precisely tracks content changes and rebuilds only the specific
artifacts that are truly affected. This will enable us to achieve our
goal of rapid rebuilds even for huge documentation sites.

- **Dynamic task orchestration** \- Our scheduler uses a workflow-based
approach, breaking down the entire build process into discrete tasks with
explicit dependencies. It replaces the implicit dependencies of MkDocs'
plugin system – where plugins can mysteriously interfere with each other –
with a transparent network of tasks that can be understood, debugged, and
optimized.

- **Automatic parallelization** \- Build processes are optimally
distributed across available CPU cores without manual configuration, with
both I/O and CPU-bound tasks running in parallel. Everything that can be
parallelized is automatically parallelized, determined by the scheduler
by analyzing the topology of the network of tasks.

- **Written in Rust** – Built entirely in Rust, our new runtime represents
a significant infrastructure investment that strives to balance
performance, modularity and reliability. This positions Zensical to
deliver capabilities that are impossible to achieve with conventional
static site generators (SSGs) at scale, laying the foundation for all
other features in the pipeline.


### Modern design [¶](https://zensical.org/about/roadmap/\#modern-design "Permanent link")

A new, modern design is available alongside the classic Material for MkDocs look,
breaking free from the Material aesthetic to create a more brandable
foundation – _you're looking at it right now_. This makes it significantly easier
for organizations to customize the looks while giving a more contemporary feel
without breaking existing projects or user expectations.

_You can keep the original look of Material for MkDocs, or opt into the new,_
_modern design._

**Key goals**

- **Identical layout** – We continue to use the battle-tested layout of
Material for MkDocs, so there are no big surprises when switching to
Zensical. Additionally, we are working on a [component system](https://zensical.org/about/roadmap/#component-system) to add
support for alternative and even completely custom layouts.

- **Identical HTML output** – The HTML output generated by Zensical is
identical to that of Material for MkDocs, ensuring that existing content
and customizations continue to work seamlessly. This means you can
continue to use your existing JavaScript and CSS overrides.

- **New mobile navigation** – In the modern design, mobile navigation has
been redesigned to be closer to the desktop version, improving usability
and consistency.

- **New icon set** – Shipping all icons that Material for MkDocs provides,
we are also introducing the [Lucide](https://lucide.dev/) icon set that is designed to be more
modern and visually appealing.


### Compatibility [¶](https://zensical.org/about/roadmap/\#compatibility "Permanent link")

Zensical is compatible with Material for MkDocs – when you run `zensical build`
in your Material for MkDocs project, it will build your project as if it were an
MkDocs project, as Zensical natively understands the `mkdocs.yml` configuration
format.

_All our work is guided by this principle: compatibility is key to a smooth_
_transition._

**Key goals**

- **Identical Markdown dialect** – Zensical uses Python Markdown and
Python Markdown Extensions to provide the same dialect that MkDocs uses,
ensuring compatibility of your existing content. While this requires Python
interop for Markdown rendering (rather than native Rust), it enables
seamless migration from Material for MkDocs without any content changes.

_We view this as a pragmatic bridge solution that prioritizes immediate_
_usability, and currently explore switching to [CommonMark](https://commonmark.org/) in the near_
_future. Of course, switching will be seamless for users, as we will_
_provide automatic translation between both dialects._

- **Identical template structure** – We haven't changed the template
structure, so your existing template overrides should work without
modification.[1](https://zensical.org/about/roadmap/#fn:2) Additionally, we switched the template engine from
Jinja2 to [MiniJinja](https://github.com/mitsuhiko/MiniJinja), a Jinja implementation in pure Rust, which allows
for templates to be rendered in parallel within our new [Rust runtime](https://zensical.org/about/roadmap/#rust-runtime).

_As mentioned above, we built an experimental prototype of a [component\_\
_system](https://zensical.org/about/roadmap/#component-system), which will provide much more flexibility than common template_
_and partial-based systems._

- **Integrated web server** – Zensical includes a high-performance web server
built in Rust that replaces MkDocs' rather basic HTTP server for previews.
The server features an extensible easy-to-use middleware architecture,
making it seamlessly compatible with our upcoming [module system](https://zensical.org/about/roadmap/#module-system),
enabling authors to add middlewares and routes with minimal effort.


## Feature parity [¶](https://zensical.org/about/roadmap/\#feature-parity "Permanent link")

Zensical will support all features that Material for MkDocs supports, including
support for blogging, tagging, downloading of external assets for GDPR
compliance, generation of social cards, search, plus a whole lot more.

_Check out the [feature parity table](https://zensical.org/compatibility/features/) in the [compatibility section](https://zensical.org/compatibility/) for_
_more information about the state of feature parity with Material for MkDocs and_
_the section on [third-party plugins](https://zensical.org/compatibility/plugins/) to learn which functionality we aim to_
_provide in Zensical natively._

## Next up [¶](https://zensical.org/about/roadmap/\#next-up "Permanent link")

This section outlines the upcoming topics that are on our roadmap – it's
where our vision starts coming to life. Now, we're developing the transformative
features that were the initial motivation for Zensical, redefining the future
of how documentation is created.

_These features will be developed in close collaboration with all [Zensical\_\
_Spark](https://zensical.org/spark/) members. Note that the following features are not just in the ideation_
_stage – we've already invested significant resources into architecture, design,_
_and prototyping, but they're not yet ready for release. This means that we have_
_already addressed feasibility and viability risks. Within Zensical Spark we are_
_focusing on maximizing desirability and usability. Before releasing features,_
_we will also ensure the code is robust and maintainable._

### Module system [¶](https://zensical.org/about/roadmap/\#module-system "Permanent link")

_It's modules all the way down_ \- We aim to build Zensical entirely from
composable modules that implement functionality against a simple API, making
every part of the build pipeline customizable, extensible, and even replaceable.
Modules define the structure of the task graph through a stream-like API,
stitching together a coherent build pipeline.

**Zensical Advancement Proposals ( [ZAPs](https://zensical.org/spark/proposals/)) in progress**

- [ZAP 007 - Module system](https://zensical.org/spark/proposals/zap-007-module-system/)

**Key goals**

- **Unlimited extensibility** – Traditional plugin systems constrain
developers to a handful of predefined extension points with semi-manual
ordering, leading to fragile configurations and unexpected interactions.
With Zensical, modules can inject, extend, or completely redefine
functionality at any point in the processing pipeline.

- **Module interdependencies** – Modules define explicit contracts specified
through the types of artifacts they consume and produce, which ensures that
interdependencies are always explicit. Tied modules can be automatically
detected and resolved, reducing bugs related to ordering. Module
priorities can be dynamically adjusted to resolve those conflicts.

- **Standard library** – We're building a comprehensive standard library
that eliminates boilerplate for module authors. Common operations, such as
file I/O and HTTP requests, are hoisted into a clean provider
architecture, allowing developers to focus on their unique transformation
logic rather than reimplementing basic functionality.

- **Intelligent build caching** – Build artifact caching becomes completely
transparent to module authors through automatic dependency tracking in the
task graph. Our [Rust runtime](https://zensical.org/about/roadmap/#rust-runtime) caches intermediate results
and reuses them when inputs remain unchanged, enabling instant previews
even for massive documentation sites with tens of thousands of pages.

- **Non-destructive editing** – Zensical will enable non-destructive editing
of content, allowing authors to make changes without losing the original
context or formatting. For instance, this allows Zensical to render proper
HTML within navigation elements, something that MkDocs does not support,
as it strips out markup too early.

- **Python API** – Language bindings to Python (using [PyO3](https://pyo3.rs/)), and
possibly other languages, allow for creating extensions in those languages
while leveraging the entirety of Zensical's module system. You won't need
to learn Rust to extend Zensical in other languages, but you can always
move parts of extensions to Rust at any time, if it becomes necessary.

- **Native modules** – Zensical will include a growing library of native
modules that the Zensical team maintains, including [search](https://zensical.org/about/roadmap/#search-and-discovery),
[API documentation](https://zensical.org/about/roadmap/#api-documentation), [modular navigation](https://zensical.org/about/roadmap/#modular-navigation), [versioning](https://zensical.org/about/roadmap/#versioning),
[internationalization](https://zensical.org/about/roadmap/#internationalization), [subprojects](https://zensical.org/about/roadmap/#subprojects), and much more.


### Search and discovery [¶](https://zensical.org/about/roadmap/\#search-and-discovery "Permanent link")

_Disco_, our new modular and blazing fast search engine, is purpose-built
for Zensical, and works in browsers, on servers, or at the edge, with robust
offline capabilities, allowing for easy hosting, even in air-gapped environments.
Of course, it's fully Open Source, so it can be integrated into a wide range
of applications far beyond Zensical itself.

Release date

Right now, Disco is exclusively available in Zensical.

We'll be releasing Disco as a standalone Open Source project at a later time. With the feedback of our professional users in [Zensical Spark](https://zensical.org/spark/), we're going to evolve the search experience, turning Disco into a highly configurable and customizable search engine that adapts to your needs.

**Key goals**

- **Modular engine architecture** \- Disco's core architecture supports multiple
specialized search engines operating simultaneously: inverted indexes for
traditional text search, hierarchical filters for structured navigation,
and vector search for semantic matching. Each engine can be configured
independently while contributing to unified search results.

The following functionality will be provided by built-in engines:
  - Inverted index for traditional text search
  - Hierarchical filtering support
  - Vector search for semantic matching
  - Router to federate multiple search indexes
  - Integration of local and remote indexes
- **Plugin-first design** – Engines provide the core search infrastructure,
but plugins deliver the advanced functionality through well-defined
extension points, enabling dynamic capabilities like intelligent
filtering, pagination, wildcard and fuzzy matching, custom ranking, and
result transformation. Plugins are also dead-simple to write.

The following functionality will be provided by built-in plugins:
  - Wildcard expansion
  - Highlighting of search terms
  - Ranking with tie-breaking and BM-25
  - Pagination of search results
  - Caching of search results
  - Aggregations and faceting
  - Fuzzy-search and auto-correct
  - Stemming and segmentation
  - Search suggestions and completions
- **Flexible ranking methods** – Disco employs a completely customizable
tie-breaking strategy that delivers consistent and flexible results for
documentation search. It also includes classic BM25 as a built-in ranking
method, which additionally supports proximity-based ranking for multi-word
queries. However, for type-ahead search, tie-breaking proved to be
unbeatable.

- **Federated search** – Search can be unified across multiple documentation
projects by aggregating results from disparate indexes, which breaks down
information silos to create a single, coherent body of knowledge for
organizations with multiple products or services.


### Component system [¶](https://zensical.org/about/roadmap/\#component-system "Permanent link")

Moving from a templating system to a component architecture allows for much
greater flexibility and reusability in documentation authoring. Zensical aims
to replace Python Markdown and Jinja with a unified component system, which
is then used to render templates, as well as to implement custom components
that can be used in Markdown files.

_We already have a working prototype for the component system, and plan to roll_
_it out gradually, by first moving all templates into components, and then_
_replacing the components inherited from Material for MkDocs one after another._

**Key goals**

- **Markdown and HTML AST** – Zensical aims to provide both, a Markdown and
HTML AST, which will allow for much simpler creation of extensions, as
well as custom components.

The Markdown AST allows content to be cleanly rendered into any format –
including HTML, EPUB, PDF, and man pages – from a single source. This
method is far superior to the regular-expression-based parsing used by
many existing parsers, which is often brittle and limited.

- **Self-contained components** – Components will be at the heart of
Zensical's presentational system. Each component is a self-contained
artifact that can be used in Markdown and templates, and can touch the
following layers:
  - **Retrieval** – Components can instruct how to fetch or load data, which
     can be used to render the component. Component attributes and children can
     be used to define the presentation of the data. They can define workflows
     for data processing, or use data from prior actions to render the
     component.

  - **Rendering** – Components specify how data is rendered. They are only
     re-rendered when their inputs change. Components may have arbitrary
     children, which are all tracked as individual components. This allows to
     dedupe rendering common elements like headers or footers that are mostly
     identical across pages.

  - **Styling** – Components can define their own styles, which can be scoped
     to the component itself, and reuse and tap into variables from the theme
     to provide a consistent look and feel across the application. Business
     logic can be decoupled from styling, so components can be reused across
     different themes much more easily.

  - **Interactivity** – Components can be interactive, implemented through a
     so called island architecture. They are rendered via SSR by design, and
     can be rehydrated on the client if JavaScript is available. Interactivity
     allows us to provide different implementations with different trade-offs,
     e.g., for accessible navigation.
- **Native runtime** – Components won't require the installation of an
additional runtime – the component runtime will be natively implemented
as part of Zensical's [module system](https://zensical.org/about/roadmap/#module-system), and will leverage it to provide
differential updates, and blazing fast rendering. This allows Zensical
to provide a stable and performant component system.

- **Asset compilation** – We will incorporate an asset compiler into
Zensical that will compile the assets and minify the result _at the time_
_your project is built_, giving you a much improved experience as a
designer. Any changes will be immediately visible in the browser.[2](https://zensical.org/about/roadmap/#fn:3)


### Configuration [¶](https://zensical.org/about/roadmap/\#configuration "Permanent link")

We're completely rethinking configuration management. Zensical scales to fit
your needs, from zero configuration with intelligent defaults to advanced
control for multi-environment setups, feature flags, and complex project
variants.

_Effortlessly build for offline use, manage a portfolio of subprojects, or_
_compile projects individually. Use presets to reduce boilerplate. Only configure_
_what you need, as you can rely on sane defaults._

**Key goals**

- **Zero configuration mode** – Zensical automatically infers your site
structure, navigation, and build settings from your content organization.
Simply point it at a folder of Markdown files and get a fully functional
documentation site with sensible defaults for theming, navigation
generation, with no configuration at all.

- **Complex folder structures** – Native support for sophisticated project
layouts including monorepos, multi-language documentation, versioned
content trees, and nested subprojects. Zensical allows to handle complex
hierarchies that would require extensive manual configuration in
traditional static site generators.

- **Programmatic configuration** – Define your build pipeline through code
rather than static files. Use functions, conditionals, and dynamic
logic to configure different builds for development, staging, and
production environments. This enables advanced scenarios like feature
flags, environment-specific content, and complex build variants.

- **Use and create presets** – Leverage community presets for common
documentation patterns – API documentation, user guides, blogs and much
more – or create your own reusable presets. Presets encapsulate best
practices and complex setups into simple, shareable packages that
eliminate repetitive configuration across projects.

_Our goal is that presets can be ejected into a detailed configuration at_
_any point in time, and contracted back into a preset with your overrides_
_remaining in place._


### API documentation [¶](https://zensical.org/about/roadmap/\#api-documentation "Permanent link")

Most API documentation systems are limited to the language they're written in,
including Rustdoc, TypeDoc, and GoDoc. Zensical eliminates this barrier by
providing a unified and extensible system that supports multiple modes of
operation and seamlessly integrates across any technology stack.

**Key goals**

- **Multi-modal documentation support**: API documentation can either be
standalone, and live in its own dedicated space as part of your
documentation project, or be injected into existing content, mixing it
with prose to create tutorials and step-by-step guides.

- **Cross-language and cross-technology integration**: Modern applications
rarely exist in isolation. A typical web application might involve Python
backend services, TypeScript frontend code, OpenAPI specifications, and
GraphQL schemas. Zensical understands these relationships and provides
automatic linking between components.

- **Extensibility for domain-specific tools**: Different ecosystems have
their own conventions and tools, e.g., FastAPI routes have specific
metadata, Pydantic models have validation logic, and GraphQL schemas have
their own structure. The system can be extended to handle these
domain-specific requirements through customizable output generation.

- **Component system integration**: Built on Zensical's shared [component\\
system](https://zensical.org/about/roadmap/#component-system), the API documentation tools let you create modular, reusable
elements. Customize the provided standard components or override them to
create your own.


### Modular navigation [¶](https://zensical.org/about/roadmap/\#modular-navigation "Permanent link")

Navigation is an integral part of any documentation site, and Zensical aims to
provide a flexible and powerful navigation system. With Zensical, we want to
significantly improve the degrees of freedom that authors have in designing an
information architecture and navigation structure that best suits their project.

**Zensical Advancement Proposals ( [ZAPs](https://zensical.org/spark/proposals/)) in progress**

- [ZAP 005 - Navigation authoring experience](https://zensical.org/spark/proposals/zap-005-navigation-authoring-experience/)
- [ZAP 004 - Modular navigation](https://zensical.org/spark/proposals/zap-004-modular-navigation/)
- [ZAP 002 - Metadata](https://zensical.org/spark/proposals/zap-002-metadata/)
- [ZAP 003 - Navigation as content](https://zensical.org/spark/proposals/zap-003-navigation-as-content/)
- [ZAP 001 - Page titles](https://zensical.org/spark/proposals/zap-001-page-titles/)

**Key goals**

- **Flexible architecture** – We're moving away from MkDocs' monolithic
navigation architecture, where there's only a single navigation hierarchy
for site-wide navigation. Zensical aims to allow templates and themes to
define arbitrary navigation elements, which authors can then configure,
customize and extend.

_Of course, Zensical also provides a set of default navigation elements_
_that template authors can use as a starting point for creating more_
_complex navigation structures._

- **Scalability** – Rendering of navigation partials is one of the main
factors of slow build times, since MkDocs' monolithic navigation implies
quadratic runtime, with every page potentially linking to every other
page. Zensical aims to improve the situation with intelligent caching and
deduplication of the computation necessary, allowing to scale from 1 to
100k pages.

- **Navigation as content** – Whether your team manages navigation as
configuration or content is up to you, as Zensical supports both modes.
You can compose all navigation elements in section-specific configuration
files, allowing to override navigation elements on a per-section basis,
or use a central configuration file for global settings.

- **Lifecycle transitions** \- The shape of your documentation will likely
change over time as its size grows and your users' needs evolve. To ensure that
your users can always find the information they need, you need to consider
the information architecture of your site on a regular basis. Making
changes to documentation at this level is not an easy task and
potentially error-prone.

_Zensical aims to make adapting your documentation much easier by offering_
_explicit support for typical changes - similar to refactoring_
_functionality offered in development environments._


### Subprojects [¶](https://zensical.org/about/roadmap/\#subprojects "Permanent link")

Complex documentation sites can be composed of multiple hierarchical
interconnected projects, spanning different technologies, teams, and deployment
requirements. Each subproject maintains its own build pipeline while sharing
resources and maintaining cross-project relationships.

**Key goals**

- **Hierarchical project trees** – You can structure your site as a tree of
interconnected projects instead of forcing everything into a single
monolithic build. This allows API references, tutorials, and usage
guides to live as separate projects with their own navigation, search
indexes, and deployment cycles, presented as a unified documentation
experience.

- **Flexible deployment modes** – Multiple projects can be deployed together
as a unified site, or selectively as individual projects to different
domains or paths. Both centralized and distributed deployment strategies
are supported, which means you can adapt to organizational constraints
while maintaining documentation quality and discoverability.

- **Cross-project integration** – Links between projects with automatic
resolution of references and paths will work seamlessly. Consolidated
search indexes that span multiple projects, merged sitemaps for SEO
optimization, and unified navigation experiences that hide the complexity
of the underlying project structure from your users will be supported.

- **Multi-language workflows** – Zensical aims to turn the problem of
internationalization into a straightforward project tree. Each
language can become its own subproject with fallback handling for
untranslated content, automatic redirection to available versions, and
clear indicators of translation status, maintaining a cohesive
multi-language experience.


### Internationalization [¶](https://zensical.org/about/roadmap/\#internationalization "Permanent link")

Multi-language support has been a source of frustration for users of almost all
static site generators. Zensical aims to address these challenges by providing
a robust framework for managing translations, language-specific content, and
fallback mechanisms.

**Key goals**

- **Flexible content organization** – Zensical aims to support multiple ways
of organizing content for different languages, including suffix-based and
folder-based approaches, and to provide tools that allow you to easily
switch between them.

- **AI-powered translation workflows** – Modern LLMs can be leveraged to
provide cost-effective translations and localization support, making it
easier to manage the evolution of multi-language content. Zensical tracks
the parts of your documentation that are removed or added, and generates
drafts for translations of these changes.

- **Localizing all parts** – Zensical aims to provide a comprehensive
solution for localizing all aspects of your documentation, including UI
elements, code snippets, and examples, ensuring a consistent experience
across languages. Localization workflows should be easy to configure and
manage, with clear guidelines for contributors.

- **Flexible deployment modes** – As with [subprojects](https://zensical.org/about/roadmap/#subprojects), Zensical will
support multiple deployment modes to accommodate different documentation
needs. This includes options for building all content together, as well as
selective builds for individual sections or languages.


### Versioning [¶](https://zensical.org/about/roadmap/\#versioning "Permanent link")

Deploy multiple versions of your documentation without being locked into
specific hosting platforms or Git workflows. Zensical's versioning system aims
to work with any branching strategy, deployment target, or organizational
structure while optimizing builds to only process changes.

**Key goals**

- **Flexible version management that adapts to your workflow** – Deploy
multiple versions of your documentation without being locked into specific
hosting platforms or Git workflows. Zensical's versioning system will work
with any branching strategy, deployment target, or organizational
structure while optimizing builds to only process what actually changed.

- **Workflow-agnostic version management** – Whether you use Git tags,
branch-based workflows, or custom versioning schemes, Zensical adapts to
your existing processes. Support for both Git-based versioning (leveraging
Git's efficient storage) and folder-based approaches for teams with
different deployment requirements or organizational constraints.

- **Differential rebuilds** – Only rebuild the versions that actually
changed. Update the latest version and only that version gets rebuilt. Fix
a typo in an older version and only that specific version is processed. Smart
change detection across the entire version tree minimizes build times and
resource usage, making it practical to maintain dozens of active versions.


### Topic-based authoring [¶](https://zensical.org/about/roadmap/\#topic-based-authoring "Permanent link")

Systematically structure your content to maximize reuse, publish via multiple
channels and produce multiple outputs from a single source. Ensure consistency
of content across these different deliverables, and achieve compliance
with regulatory requirements. Zensical aims to bring you the benefits of both
topic-based authoring and of Docs-as-Code workflows.

**Zensical Advancement Protosals ( [ZAPs](https://zensical.org/spark/proposals/)) in progress**

- [ZAP 006 - Topic-based authoring](https://zensical.org/spark/proposals/zap-006-topic-based-authoring/)

**Key goals**

- **Coherent concepts** – Define a clear conceptual model for topics
and a mapping/assembly mechanism so content can be authored as
independent, self-contained topics. Enable indirect addressing (keys) and
fine-grained reuse so authors can reference content by identifier rather
than file path, keeping topics portable across publications.

- **Batteries included and extensible** – Provide an out-of-the-box workflow
that supports gradual adoption: sensible defaults, tooling for migration,
and compatibility with common authoring formats so teams can adopt
topic-based practices incrementally without heavy upfront cost. At the
same time, leverage the module system to enable teams to adapt support
for topic-based authoring to their needs.

- **Interoperability with DITA and proprietary workflows** – Support
import/export to interoperate with existing DITA and proprietary workflows,
reducing vendor lock-in and easing migration for enterprise users.

- **Efficient variant builds** – Enable profiling, conditionals, and
variant management so a single source can produce multiple product,
locale, and channel outputs. Couple this with differential and
performance-oriented builds to make multi-variant publishing fast and
practical for large projects.

- **LLM & agent consumption** – Well-structured, self-contained topics are
inherently better inputs for LLMs and AI coding agents. When content is
modular and consistently typed, agents can retrieve precisely what they
need without being burdened by surrounding context that doesn't apply to
the task at hand.

- **Lean context files, always up to date** – Zensical will leverage the
topic model to generate lean, targeted context files (such as `AGENTS.md`
or `CLAUDE.md`) that surface only the non-obvious information agents
cannot infer on their own, keeping them focused and avoiding context
bloat. Because agent context files are maintained as part of the overall
documentation, they stay accurate as the product and its documentation
evolve.


* * *

1. We have made some changes to the templates of Material for MkDocs, in order
to make them 100% compatible with [MiniJinja](https://github.com/mitsuhiko/MiniJinja). These updates only involve
syntactical changes to Jinja flow constructs, not the underlying HTML. Please
make sure your overrides use the same syntax. Check out the releases [9.6.10](https://github.com/squidfunk/mkdocs-material/releases/tag/9.6.10)
and [9.6.18](https://github.com/squidfunk/mkdocs-material/releases/tag/9.6.18), which introduced these changes. [↩](https://zensical.org/about/roadmap/#fnref:2 "Jump back to footnote 1 in the text")

2. A common remark is that the styling provided by Material for MkDocs is
    compiled at the time when the theme is compiled. This means that teams can
    only override style rules but not modify them. Zensical will lift this
    requirement and make asset compilation part of the runtime. [↩](https://zensical.org/about/roadmap/#fnref:3 "Jump back to footnote 2 in the text")


Back to top

### Filters

#### Tags

1. Features38
2. Zensical Spark36
3. Company29
4. Subscription29
5. Compatibility28
6. Account11
7. Policies7
8. Transition4
9. License2