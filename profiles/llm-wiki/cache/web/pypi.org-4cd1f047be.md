[Skip to main content](https://pypi.org/project/mkdocs-obsidian-bridge/#content) Switch to mobile version

Search PyPISearch

# mkdocs-obsidian-bridge 1.3.1

pip install mkdocs-obsidian-bridgeCopy PIP instructions

[Latest release](https://pypi.org/project/mkdocs-obsidian-bridge/)

Released: Aug 13, 2025

An MkDocs plugin that helps exporting your Obsidian vault as an MkDocs site.

### Navigation

### Verified details

_These details have been [verified by PyPI](https://docs.pypi.org/project_metadata/#verified-details)_

###### Project links

- [Homepage](https://github.com/GooRoo/mkdocs-obsidian-bridge)
- [Issues](https://github.com/GooRoo/mkdocs-obsidian-bridge/issues)
- [Repository](https://github.com/GooRoo/mkdocs-obsidian-bridge.git)

###### GitHub Statistics

- [**Repository**](https://github.com/GooRoo/mkdocs-obsidian-bridge)
- [**Stars:** 84](https://github.com/GooRoo/mkdocs-obsidian-bridge/stargazers)
- [**Forks:** 3](https://github.com/GooRoo/mkdocs-obsidian-bridge/network/members)
- [**Open issues:** 3](https://github.com/GooRoo/mkdocs-obsidian-bridge/issues)
- [**Open PRs:** 0](https://github.com/GooRoo/mkdocs-obsidian-bridge/pulls)

###### Maintainers

[![Avatar for GooRoo from gravatar.com](https://pypi-camo.freetls.fastly.net/a1c01e0a554289c59517dc32a6b9a78ab41d18d1/68747470733a2f2f7365637572652e67726176617461722e636f6d2f6176617461722f31323637616138343033666238333466636162386639373735323030386338363f73697a653d3530)GooRoo](https://pypi.org/user/GooRoo/)

### Unverified details

_These details have **not** been verified by PyPI_

###### Meta

- **License Expression:** BSD-3-Clause


_[SPDX](https://spdx.org/licenses/) [License Expression](https://spdx.github.io/spdx-spec/v3.0.1/annexes/spdx-license-expressions/)_
- **Author:** [GooRoo](mailto:sergey.olendarenko@gmail.com)
- **Requires:** Python <4, >=3.10


###### Classifiers

- **Development Status**  - [5 - Production/Stable](https://pypi.org/search/?c=Development+Status+%3A%3A+5+-+Production%2FStable)
- **Environment**  - [Plugins](https://pypi.org/search/?c=Environment+%3A%3A+Plugins)
- **Framework**  - [MkDocs](https://pypi.org/search/?c=Framework+%3A%3A+MkDocs)
- **License**  - [OSI Approved :: BSD License](https://pypi.org/search/?c=License+%3A%3A+OSI+Approved+%3A%3A+BSD+License)
- **Programming Language**  - [Python :: 3](https://pypi.org/search/?c=Programming+Language+%3A%3A+Python+%3A%3A+3)
  - [Python :: 3.10](https://pypi.org/search/?c=Programming+Language+%3A%3A+Python+%3A%3A+3.10)
- **Topic**  - [Documentation](https://pypi.org/search/?c=Topic+%3A%3A+Documentation)
  - [Software Development :: Documentation](https://pypi.org/search/?c=Topic+%3A%3A+Software+Development+%3A%3A+Documentation)
  - [Text Processing :: Markup :: HTML](https://pypi.org/search/?c=Topic+%3A%3A+Text+Processing+%3A%3A+Markup+%3A%3A+HTML)
  - [Text Processing :: Markup :: Markdown](https://pypi.org/search/?c=Topic+%3A%3A+Text+Processing+%3A%3A+Markup+%3A%3A+Markdown)

[Report project as malware](https://pypi.org/project/mkdocs-obsidian-bridge/submit-malware-report/)

## Project description

# [Obsidian](https://obsidian.md/) ➡️ [MkDocs](https://www.mkdocs.org/) Bridge

[![Made by Ukrainian](https://pypi-camo.freetls.fastly.net/1e05c2ddb82e1718c37c7221c582221341a8c2a0/68747470733a2f2f696d672e736869656c64732e696f2f7374617469632f76313f6c6162656c3d4d6164652532306279266d6573736167653d556b7261696e69616e266c6162656c436f6c6f723d31663566623226636f6c6f723d666164323437267374796c653d666c61742d737175617265)](https://savelife.in.ua/en/donate-en/#donate-army-card-once)[![License](https://pypi-camo.freetls.fastly.net/2956e6d1cfe6b25a393a24c61aaf34a773e5d1ca/68747470733a2f2f696d672e736869656c64732e696f2f6769746875622f6c6963656e73652f476f6f526f6f2f6d6b646f63732d6f6273696469616e2d6272696467653f7374796c653d666c61742d737175617265)](https://pypi.org/project/mkdocs-obsidian-bridge/LICENSE)![REUSE Compliance](https://pypi-camo.freetls.fastly.net/a8723a61599f90ca67f8cdf56323027cdbdbf394/68747470733a2f2f696d672e736869656c64732e696f2f72657573652f636f6d706c69616e63652f6769746875622e636f6d253246476f6f526f6f2532466d6b646f63732d6f6273696469616e2d6272696467653f7374796c653d666c61742d737175617265)![GitHub branch check runs](https://pypi-camo.freetls.fastly.net/69e71133454aa91f775466c61a53928151fba489/68747470733a2f2f696d672e736869656c64732e696f2f6769746875622f636865636b2d72756e732f476f6f526f6f2f6d6b646f63732d6f6273696469616e2d6272696467652f6d61696e3f7374796c653d666c61742d737175617265)

An MkDocs plugin that helps exporting your [Obsidian](https://obsidian.md/) vault as an MkDocs site.

## What it does

I began writing this plugin to simplify exporting my Obsidian vault to GitHub Pages using MkDocs. The plugin is still in development since there are a lot more features that could possibly be implemented, however, currently it has the following features:

- Auto-expand incomplete [Markdown links](https://help.obsidian.md/How+to/Format+your+notes#Links)
- Auto-expand incomplete [Obsidian's internal links](https://help.obsidian.md/How+to/Internal+link)
- Detect and mark invalid links (to style them differently)

### Auto-expanding incomplete links

By auto-expanding I mean that you don't need to write a full path to the page you are linking to (exactly like in [Obsidian](https://obsidian.md/)). Consider the following folder structure:

```
docs/
├── 2021/
│   ├── Books.md
│   └── Games.md
└── 2022/
    └── Sport.md
```

If you are editing `Sport.md`, you could write:

```
[Books](../2021/Books.md)
```

but with this plugin you can just drop the path:

```
[Books](Books.md)
```

or even write the [Obsidian](https://obsidian.md/) way:

```
[[Books]]
```

#### Name clashes

What if you have `Books.md` in both 2021 and 2022?

```
docs/
├── 2021/
│   ├── Books.md
│   └── Games.md
└── 2022/
    ├── Books.md
    └── Sport.md
```

By default, the plugin tried to find the shortest relative path (again, like [Obsidian](https://obsidian.md/)), e.g.

```
[[Books]]
```

is translated into:

```
[Books](./Books.md)
```

But you can also give the resolver _a hint_ by specifying the path **partially:**

```
[[2021/Books]]
```

or

```
[Books](2021/Books.md)
```

Both variants work equivalently.

## How to enable

Install the plugin with:

```
pip install mkdocs-obsidian-bridge
```

The plugin depends on some features of Python 3.10, so this is the minimum required version.

Then you can enable it in your `mkdocs.yml` config:

```
plugins:
  - obsidian-bridge
```

### Embedding of media files

If you want to have Obsidian-like embedding of audio and video files or even YouTube videos, enable it in your `mkdocs.yml` like this:

```
markdown_extensions:
  - obsidian_media_mkdocs
```

More information on this feature can be found here: [**GooRoo/obsidian-media**](https://github.com/GooRoo/obsidian-media).

### Using callouts

Looking for Obsidian-style callouts? Enable them in your `mkdocs.yml` like this:

```
markdown_extensions:
  - obsidian_callouts
```

More information on this feature can be found here: [**GooRoo/obsidian-callouts**](https://github.com/GooRoo/obsidian-callouts).

## Why one more plugin?

I wouldn't ever write this one if I could achieve what I need with other ones. Maybe, I just couldn't find the solution, but here we are.

Comparison to others (possibly, outdated)

### Differences to [Autolinks Plugin](https://github.com/zachhannum/mkdocs-autolinks-plugin)

1. **Autolinks Plugin** doesn't try to resolve the shortest path out of the list of potential candidates.
2. It also doesn't support incomplete relative paths. In other words, it works only with file names.

### Differences to [Roamlinks Plugin](https://github.com/Jackiexiao/mkdocs-roamlinks-plugin)

This one, actually, was the reason why I started developing my own plugin in the first place. However, it had the following drawbacks for my use-case:

1. As well as **Autolinks Plugin**, the **Roamlinks Plugin** does not try to match the best path if there several of those, does it?
2. Also, in case it can't resolve the `[[Roam link]]`, it leaves it as a text, while [**Obsidian Bridge**](https://github.com/GooRoo/mkdocs-obsidian-bridge) still transforms it into the Markdown link although invalid one.

### Differences to [EZLinks Plugin](https://github.com/orbikm/mkdocs-ezlinks-plugin)

This one looked like a perfect choice for my needs, however:

1. I didn't spent much time playing with it, but **EZLinks Plugin** generated incorrect links for me. Probably because it doesn't resolve any incomplete paths as well as two previous plugins.
2. At the same time, it **does** convert the `[[internal links]]` into actual links.
3. It has no ability to distinguish between valid and invalid `[[internal links]]`. Maybe it could be solved by another plugin, but I haven't searched for it.

### Differences to [WikiLinks](https://python-markdown.github.io/extensions/wikilinks/) extension for [Python-Markdown](https://github.com/Python-Markdown/markdown/)

1. I haven't tried this one, but it looks like **WikiLinks** is unable to automatically resolve paths at all without an additional (and a bit cumbersome) config.
2. Also, not sure if it supports all the [Obsidian](https://obsidian.md/)'s features.

* * *

## Advanced topics

### Warnings for invalid links

Optionally, you can ask plugin to warn you when the resulting link still leads to an invalid target. This will prevent your site from building in “strict” mode.

Enable it like this

```
plugins:
  - obsidian-bridge:
      warn_on_invalid_links: true
```

### Styling of invalid links

See for yourself!

The plugin translates [Obsidian](https://obsidian.md/)-style `[[internal links]]` to markdown `[internal links](internal%20links)` even if the resulting link is invalid. If you want to distinguish such links from the rest, you can assign them a custom CSS style.

In order to do that, you should add an `invalid_link_attributes` config option to your `mkdocs.yml` **AND** enable the `attr_list` Markdown extension:

```
markdown_extensions:
  - attr_list

plugins:
  - obsidian-bridge:
      invalid_link_attributes:
        - '.invalid'

extra_css:
  - stylesheets/extra.css
```

The `.invalid` in this example translates to `class="invalid"` HTML attribute accordingly to the rules of [**Attribute Lists**](https://python-markdown.github.io/extensions/attr_list/) extension.

After that, you can extend `extra.css` with some style (just don't forget to add `extra_css` property to your `mkdocs.yml` too as above):

```
a.invalid {
  color: red;
}
```

Alternatively, if your style is going to be simple, you can just write it in the attribute itself as following:

```
markdown_extensions:
  - attr_list

plugins:
  - obsidian-bridge:
      invalid_link_attributes:
        - 'style="color: red"'
```

* * *

## What's next

My current preliminary roadmap is the following:

- [x] [**Embedding of audio/video**](https://help.obsidian.md/Linking+notes+and+files/Embed+files)
- [x]  Obsidian's [**callouts**](https://help.obsidian.md/Editing+and+formatting/Callouts)
- [ ]  Support for Obsidian's [**nested tags**](https://help.obsidian.md/Editing+and+formatting/Tags#Nested+tags)
- [ ]  Obsidian's [**comments**](https://help.obsidian.md/Editing+and+formatting/Basic+formatting+syntax#Comments)`%% ... %%` ➡️ HTML comments `<!-- ... -->`

I give no guarantees about the deadlines or whether I implement anything at all. I do it for myself and currently I do see a need, so probably I'll continue.

### Feedback

I do appreciate any kind of constructive feedback.

- If you found a bug, please, [report it](https://github.com/GooRoo/mkdocs-obsidian-bridge/issues/new).
- If you want to request a feature, please, [post an idea](https://github.com/GooRoo/mkdocs-obsidian-bridge/discussions/new?category=Ideas).
- In all other cases, don't hesitate to [start a discussion](https://github.com/GooRoo/mkdocs-obsidian-bridge/discussions/new).

## Project details

### Verified details

_These details have been [verified by PyPI](https://docs.pypi.org/project_metadata/#verified-details)_

###### Project links

- [Homepage](https://github.com/GooRoo/mkdocs-obsidian-bridge)
- [Issues](https://github.com/GooRoo/mkdocs-obsidian-bridge/issues)
- [Repository](https://github.com/GooRoo/mkdocs-obsidian-bridge.git)

###### GitHub Statistics

- [**Repository**](https://github.com/GooRoo/mkdocs-obsidian-bridge)
- [**Stars:** 84](https://github.com/GooRoo/mkdocs-obsidian-bridge/stargazers)
- [**Forks:** 3](https://github.com/GooRoo/mkdocs-obsidian-bridge/network/members)
- [**Open issues:** 3](https://github.com/GooRoo/mkdocs-obsidian-bridge/issues)
- [**Open PRs:** 0](https://github.com/GooRoo/mkdocs-obsidian-bridge/pulls)

###### Maintainers

[![Avatar for GooRoo from gravatar.com](https://pypi-camo.freetls.fastly.net/a1c01e0a554289c59517dc32a6b9a78ab41d18d1/68747470733a2f2f7365637572652e67726176617461722e636f6d2f6176617461722f31323637616138343033666238333466636162386639373735323030386338363f73697a653d3530)GooRoo](https://pypi.org/user/GooRoo/)

### Unverified details

_These details have **not** been verified by PyPI_

###### Meta

- **License Expression:** BSD-3-Clause


_[SPDX](https://spdx.org/licenses/) [License Expression](https://spdx.github.io/spdx-spec/v3.0.1/annexes/spdx-license-expressions/)_
- **Author:** [GooRoo](mailto:sergey.olendarenko@gmail.com)
- **Requires:** Python <4, >=3.10


###### Classifiers

- **Development Status**  - [5 - Production/Stable](https://pypi.org/search/?c=Development+Status+%3A%3A+5+-+Production%2FStable)
- **Environment**  - [Plugins](https://pypi.org/search/?c=Environment+%3A%3A+Plugins)
- **Framework**  - [MkDocs](https://pypi.org/search/?c=Framework+%3A%3A+MkDocs)
- **License**  - [OSI Approved :: BSD License](https://pypi.org/search/?c=License+%3A%3A+OSI+Approved+%3A%3A+BSD+License)
- **Programming Language**  - [Python :: 3](https://pypi.org/search/?c=Programming+Language+%3A%3A+Python+%3A%3A+3)
  - [Python :: 3.10](https://pypi.org/search/?c=Programming+Language+%3A%3A+Python+%3A%3A+3.10)
- **Topic**  - [Documentation](https://pypi.org/search/?c=Topic+%3A%3A+Documentation)
  - [Software Development :: Documentation](https://pypi.org/search/?c=Topic+%3A%3A+Software+Development+%3A%3A+Documentation)
  - [Text Processing :: Markup :: HTML](https://pypi.org/search/?c=Topic+%3A%3A+Text+Processing+%3A%3A+Markup+%3A%3A+HTML)
  - [Text Processing :: Markup :: Markdown](https://pypi.org/search/?c=Topic+%3A%3A+Text+Processing+%3A%3A+Markup+%3A%3A+Markdown)

## Release history[Release notifications](https://pypi.org/help/\#project-release-notifications) \|  [RSS feed](https://pypi.org/rss/project/mkdocs-obsidian-bridge/releases.xml)

This version

![](https://pypi.org/static/images/blue-cube.572a5bfb.svg)

[1.3.1\\
\\
\\
Aug 13, 2025](https://pypi.org/project/mkdocs-obsidian-bridge/1.3.1/)

![](https://pypi.org/static/images/white-cube.2351a86c.svg)

[1.3.0\\
\\
\\
Aug 13, 2025](https://pypi.org/project/mkdocs-obsidian-bridge/1.3.0/)

![](https://pypi.org/static/images/white-cube.2351a86c.svg)

[1.2.0\\
\\
\\
Jan 12, 2025](https://pypi.org/project/mkdocs-obsidian-bridge/1.2.0/)

![](https://pypi.org/static/images/white-cube.2351a86c.svg)

[1.1.1\\
\\
\\
Sep 23, 2024](https://pypi.org/project/mkdocs-obsidian-bridge/1.1.1/)

![](https://pypi.org/static/images/white-cube.2351a86c.svg)

[1.1.0\\
\\
\\
Sep 23, 2024](https://pypi.org/project/mkdocs-obsidian-bridge/1.1.0/)

![](https://pypi.org/static/images/white-cube.2351a86c.svg)

[1.0.4\\
\\
\\
Jul 21, 2024](https://pypi.org/project/mkdocs-obsidian-bridge/1.0.4/)

![](https://pypi.org/static/images/white-cube.2351a86c.svg)

[1.0.3\\
\\
\\
Jul 21, 2024](https://pypi.org/project/mkdocs-obsidian-bridge/1.0.3/)

![](https://pypi.org/static/images/white-cube.2351a86c.svg)

[1.0.2\\
\\
\\
Jan 6, 2024](https://pypi.org/project/mkdocs-obsidian-bridge/1.0.2/)

![](https://pypi.org/static/images/white-cube.2351a86c.svg)

[1.0.1\\
\\
\\
Mar 11, 2023](https://pypi.org/project/mkdocs-obsidian-bridge/1.0.1/)

![](https://pypi.org/static/images/white-cube.2351a86c.svg)

[1.0.0\\
\\
\\
Dec 29, 2022](https://pypi.org/project/mkdocs-obsidian-bridge/1.0.0/)

## Download files

Download the file for your platform. If you're not sure which to choose, learn more about [installing packages](https://packaging.python.org/tutorials/installing-packages/ "External link").

### Source Distribution

[mkdocs\_obsidian\_bridge-1.3.1.tar.gz](https://files.pythonhosted.org/packages/ee/93/d0dda71bacfcbdeb522a16e895311669a75eda3e7872e6182a5957520877/mkdocs_obsidian_bridge-1.3.1.tar.gz)
(65.1 kB
[view details](https://pypi.org/project/mkdocs-obsidian-bridge/#mkdocs_obsidian_bridge-1.3.1.tar.gz))


Uploaded Aug 13, 2025`Source`

### Built Distribution

Filter files by name, interpreter, ABI, and platform.

If you're not sure about the file name format, learn more about [wheel file names](https://packaging.python.org/en/latest/specifications/binary-distribution-format/ "External link").

Copy a direct link to the current filters [https://pypi.org/project/mkdocs-obsidian-bridge/#files](https://pypi.org/project/mkdocs-obsidian-bridge/#files)
Copy

Showing 1 of 1 file.

File name

InterpreterInterpreterpy3

ABIABInone

PlatformPlatformany

[mkdocs\_obsidian\_bridge-1.3.1-py3-none-any.whl](https://files.pythonhosted.org/packages/25/3f/b250670f6a960186f556a49b6ab8714867065a0d03565cb678a3d0313216/mkdocs_obsidian_bridge-1.3.1-py3-none-any.whl)
(10.1 kB
[view details](https://pypi.org/project/mkdocs-obsidian-bridge/#mkdocs_obsidian_bridge-1.3.1-py3-none-any.whl))


Uploaded Aug 13, 2025`Python 3`

## File details

Details for the file `mkdocs_obsidian_bridge-1.3.1.tar.gz`.


### File metadata

- Download URL: [mkdocs\_obsidian\_bridge-1.3.1.tar.gz](https://files.pythonhosted.org/packages/ee/93/d0dda71bacfcbdeb522a16e895311669a75eda3e7872e6182a5957520877/mkdocs_obsidian_bridge-1.3.1.tar.gz)
- Upload date: Aug 13, 2025
- Size: 65.1 kB
- Tags: Source
- Uploaded using Trusted Publishing? Yes
- Uploaded via: twine/6.1.0 CPython/3.12.9

### File hashes

| Algorithm | Hash digest |  |
| --- | --- | --- |
| SHA256 | `92d7cee4dc857a45818b912c0091452a22976250513ee63fb4c1f64bb06d2ab8` | Copy |
| MD5 | `36a5201a1a5c8b7e9dc23b5839776ef0` | Copy |
| BLAKE2b-256 | `ee93d0dda71bacfcbdeb522a16e895311669a75eda3e7872e6182a5957520877` | Copy |

Hashes for mkdocs\_obsidian\_bridge-1.3.1.tar.gz

[See more details on using hashes here.](https://pip.pypa.io/en/stable/topics/secure-installs/#hash-checking-mode "External link")

### Provenance

The following attestation bundles were made for `mkdocs_obsidian_bridge-1.3.1.tar.gz`:


Publisher: [`build-deploy.yml` on GooRoo/mkdocs-obsidian-bridge](https://github.com/GooRoo/mkdocs-obsidian-bridge/blob/HEAD/.github/workflows/build-deploy.yml)

Attestations:
_Values shown here reflect the state when the release was signed and may no longer be current._

- Statement:


  - Statement type: [`https://in-toto.io/Statement/v1`](https://in-toto.io/Statement/v1)
  - Predicate type: [`https://docs.pypi.org/attestations/publish/v1`](https://docs.pypi.org/attestations/publish/v1)
  - Subject name: `mkdocs_obsidian_bridge-1.3.1.tar.gz`
  - Subject digest: `92d7cee4dc857a45818b912c0091452a22976250513ee63fb4c1f64bb06d2ab8`
  - Sigstore transparency entry: [389397472](https://search.sigstore.dev/?logIndex=389397472)
  - Sigstore integration time: Aug 13, 2025, 9:30:24 AM

Source repository:


  - Permalink: [`GooRoo/mkdocs-obsidian-bridge@fe645285b07b89c513ebe31ee38a30110b429901`](https://github.com/GooRoo/mkdocs-obsidian-bridge/tree/fe645285b07b89c513ebe31ee38a30110b429901)
  - Branch / Tag: [`refs/tags/v1.3.1`](https://github.com/GooRoo/mkdocs-obsidian-bridge/tree/refs/tags/v1.3.1)
  - Owner: [https://github.com/GooRoo](https://github.com/GooRoo)
  - Access: `public`

Publication detail:
   - Token Issuer: `https://token.actions.githubusercontent.com`
  - Runner Environment: `github-hosted`
  - Publication workflow:
     [`build-deploy.yml@fe645285b07b89c513ebe31ee38a30110b429901`](https://github.com/GooRoo/mkdocs-obsidian-bridge/blob/fe645285b07b89c513ebe31ee38a30110b429901/.github/workflows/build-deploy.yml)
  - Trigger Event: `push`

## File details

Details for the file `mkdocs_obsidian_bridge-1.3.1-py3-none-any.whl`.


### File metadata

- Download URL: [mkdocs\_obsidian\_bridge-1.3.1-py3-none-any.whl](https://files.pythonhosted.org/packages/25/3f/b250670f6a960186f556a49b6ab8714867065a0d03565cb678a3d0313216/mkdocs_obsidian_bridge-1.3.1-py3-none-any.whl)
- Upload date: Aug 13, 2025
- Size: 10.1 kB
- Tags: Python 3
- Uploaded using Trusted Publishing? Yes
- Uploaded via: twine/6.1.0 CPython/3.12.9

### File hashes

| Algorithm | Hash digest |  |
| --- | --- | --- |
| SHA256 | `8653c49f970ad1e6c08983e5c9d0cfc2be4af0d432e415a5e601b9be00696126` | Copy |
| MD5 | `d40fa7810d50d8d5e5491f6b5a2fc699` | Copy |
| BLAKE2b-256 | `253fb250670f6a960186f556a49b6ab8714867065a0d03565cb678a3d0313216` | Copy |

Hashes for mkdocs\_obsidian\_bridge-1.3.1-py3-none-any.whl

[See more details on using hashes here.](https://pip.pypa.io/en/stable/topics/secure-installs/#hash-checking-mode "External link")

### Provenance

The following attestation bundles were made for `mkdocs_obsidian_bridge-1.3.1-py3-none-any.whl`:


Publisher: [`build-deploy.yml` on GooRoo/mkdocs-obsidian-bridge](https://github.com/GooRoo/mkdocs-obsidian-bridge/blob/HEAD/.github/workflows/build-deploy.yml)

Attestations:
_Values shown here reflect the state when the release was signed and may no longer be current._

- Statement:


  - Statement type: [`https://in-toto.io/Statement/v1`](https://in-toto.io/Statement/v1)
  - Predicate type: [`https://docs.pypi.org/attestations/publish/v1`](https://docs.pypi.org/attestations/publish/v1)
  - Subject name: `mkdocs_obsidian_bridge-1.3.1-py3-none-any.whl`
  - Subject digest: `8653c49f970ad1e6c08983e5c9d0cfc2be4af0d432e415a5e601b9be00696126`
  - Sigstore transparency entry: [389397485](https://search.sigstore.dev/?logIndex=389397485)
  - Sigstore integration time: Aug 13, 2025, 9:30:24 AM

Source repository:


  - Permalink: [`GooRoo/mkdocs-obsidian-bridge@fe645285b07b89c513ebe31ee38a30110b429901`](https://github.com/GooRoo/mkdocs-obsidian-bridge/tree/fe645285b07b89c513ebe31ee38a30110b429901)
  - Branch / Tag: [`refs/tags/v1.3.1`](https://github.com/GooRoo/mkdocs-obsidian-bridge/tree/refs/tags/v1.3.1)
  - Owner: [https://github.com/GooRoo](https://github.com/GooRoo)
  - Access: `public`

Publication detail:
   - Token Issuer: `https://token.actions.githubusercontent.com`
  - Runner Environment: `github-hosted`
  - Publication workflow:
     [`build-deploy.yml@fe645285b07b89c513ebe31ee38a30110b429901`](https://github.com/GooRoo/mkdocs-obsidian-bridge/blob/fe645285b07b89c513ebe31ee38a30110b429901/.github/workflows/build-deploy.yml)
  - Trigger Event: `push`

- English
- español
- français
- 日本語
- português (Brasil)
- українська
- Ελληνικά
- Deutsch
- 中文 (简体)
- 中文 (繁體)
- русский
- עברית
- Esperanto
- 한국어

Supported by

[![](https://pypi-camo.freetls.fastly.net/ed7074cadad1a06f56bc520ad9bd3e00d0704c5b/68747470733a2f2f73746f726167652e676f6f676c65617069732e636f6d2f707970692d6173736574732f73706f6e736f726c6f676f732f6177732d77686974652d6c6f676f2d7443615473387a432e706e67)AWS\\
Cloud computing and Security Sponsor](https://aws.amazon.com/) [![](https://pypi-camo.freetls.fastly.net/8855f7c063a3bdb5b0ce8d91bfc50cf851cc5c51/68747470733a2f2f73746f726167652e676f6f676c65617069732e636f6d2f707970692d6173736574732f73706f6e736f726c6f676f732f64617461646f672d77686974652d6c6f676f2d6668644c4e666c6f2e706e67)Datadog\\
Monitoring](https://www.datadoghq.com/) [![](https://pypi-camo.freetls.fastly.net/60f709d24f3e4d469f9adc77c65e2f5291a3d165/68747470733a2f2f73746f726167652e676f6f676c65617069732e636f6d2f707970692d6173736574732f73706f6e736f726c6f676f732f6465706f742d77686974652d6c6f676f2d7038506f476831302e706e67)Depot\\
Continuous Integration](https://depot.dev/) [![](https://pypi-camo.freetls.fastly.net/df6fe8829cbff2d7f668d98571df1fd011f36192/68747470733a2f2f73746f726167652e676f6f676c65617069732e636f6d2f707970692d6173736574732f73706f6e736f726c6f676f732f666173746c792d77686974652d6c6f676f2d65684d3077735f6f2e706e67)Fastly\\
CDN](https://www.fastly.com/) [![](https://pypi-camo.freetls.fastly.net/420cc8cf360bac879e24c923b2f50ba7d1314fb0/68747470733a2f2f73746f726167652e676f6f676c65617069732e636f6d2f707970692d6173736574732f73706f6e736f726c6f676f732f676f6f676c652d77686974652d6c6f676f2d616734424e3774332e706e67)Google\\
Download Analytics](https://careers.google.com/) [![](https://pypi-camo.freetls.fastly.net/d01053c02f3a626b73ffcb06b96367fdbbf9e230/68747470733a2f2f73746f726167652e676f6f676c65617069732e636f6d2f707970692d6173736574732f73706f6e736f726c6f676f732f70696e67646f6d2d77686974652d6c6f676f2d67355831547546362e706e67)Pingdom\\
Monitoring](https://www.pingdom.com/) [![](https://pypi-camo.freetls.fastly.net/67af7117035e2345bacb5a82e9aa8b5b3e70701d/68747470733a2f2f73746f726167652e676f6f676c65617069732e636f6d2f707970692d6173736574732f73706f6e736f726c6f676f732f73656e7472792d77686974652d6c6f676f2d4a2d6b64742d706e2e706e67)Sentry\\
Error logging](https://sentry.io/for/python/?utm_source=pypi&utm_medium=paid-community&utm_campaign=python-na-evergreen&utm_content=static-ad-pypi-sponsor-learnmore) [![](https://pypi-camo.freetls.fastly.net/b611884ff90435a0575dbab7d9b0d3e60f136466/68747470733a2f2f73746f726167652e676f6f676c65617069732e636f6d2f707970692d6173736574732f73706f6e736f726c6f676f732f737461747573706167652d77686974652d6c6f676f2d5467476c6a4a2d502e706e67)StatusPage\\
Status page](https://statuspage.io/)