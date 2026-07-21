[Skip to content](https://github.com/peddamat/mkdocs-roamlinks-plugin#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/peddamat/mkdocs-roamlinks-plugin) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/peddamat/mkdocs-roamlinks-plugin) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/peddamat/mkdocs-roamlinks-plugin) to refresh your session.Dismiss alert

{{ message }}

[peddamat](https://github.com/peddamat)/ **[mkdocs-roamlinks-plugin](https://github.com/peddamat/mkdocs-roamlinks-plugin)** Public

forked from [makerjackie/mkdocs-roamlinks-plugin](https://github.com/makerjackie/mkdocs-roamlinks-plugin)

- [Notifications](https://github.com/login?return_to=%2Fpeddamat%2Fmkdocs-roamlinks-plugin) You must be signed in to change notification settings
- [Fork\\
1](https://github.com/login?return_to=%2Fpeddamat%2Fmkdocs-roamlinks-plugin)
- [Star\\
0](https://github.com/login?return_to=%2Fpeddamat%2Fmkdocs-roamlinks-plugin)


master

[**1** Branch](https://github.com/peddamat/mkdocs-roamlinks-plugin/branches) [**0** Tags](https://github.com/peddamat/mkdocs-roamlinks-plugin/tags)

[Go to Branches page](https://github.com/peddamat/mkdocs-roamlinks-plugin/branches)[Go to Tags page](https://github.com/peddamat/mkdocs-roamlinks-plugin/tags)

Go to file

Code

Open more actions menu

This branch is [1 commit ahead of](https://github.com/peddamat/mkdocs-roamlinks-plugin/compare/makerjackie%3Amkdocs-roamlinks-plugin%3Amaster...master) and [6 commits behind](https://github.com/peddamat/mkdocs-roamlinks-plugin/compare/master...makerjackie%3Amkdocs-roamlinks-plugin%3Amaster) makerjackie/mkdocs-roamlinks-plugin:master.

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![peddamat](https://avatars.githubusercontent.com/u/869300?v=4&size=40)](https://github.com/peddamat)[peddamat](https://github.com/peddamat/mkdocs-roamlinks-plugin/commits?author=peddamat)<br>[Fixed strange bug in ROAMLINK\_RE which breaks 'alias' match group.](https://github.com/peddamat/mkdocs-roamlinks-plugin/commit/c25ea9b774d18494108d12bb46626ca4f5506fa9)<br>Open commit details<br>3 years agoApr 4, 2023<br>[c25ea9b](https://github.com/peddamat/mkdocs-roamlinks-plugin/commit/c25ea9b774d18494108d12bb46626ca4f5506fa9) · 3 years agoApr 4, 2023<br>## History<br>[31 Commits](https://github.com/peddamat/mkdocs-roamlinks-plugin/commits/master/) <br>Open commit details<br>[View commit history for this file.](https://github.com/peddamat/mkdocs-roamlinks-plugin/commits/master/) 31 Commits |
| [mkdocs\_roamlinks\_plugin](https://github.com/peddamat/mkdocs-roamlinks-plugin/tree/master/mkdocs_roamlinks_plugin "mkdocs_roamlinks_plugin") | [mkdocs\_roamlinks\_plugin](https://github.com/peddamat/mkdocs-roamlinks-plugin/tree/master/mkdocs_roamlinks_plugin "mkdocs_roamlinks_plugin") | [Fixed strange bug in ROAMLINK\_RE which breaks 'alias' match group.](https://github.com/peddamat/mkdocs-roamlinks-plugin/commit/c25ea9b774d18494108d12bb46626ca4f5506fa9 "Fixed strange bug in ROAMLINK_RE which breaks 'alias' match group.  I was experiencing a strange bug on my blog where the first few wikilinks were converted properly, but the last wikilink would be broken.  For example: `on Part 1, Part 2, and [Part 3]] and come back here...`  Adding `print` statements to `plugin.py` starting at line 147, I saw:  ``` alias1: Part 1 alias1: Part 2 alias1: Part]] and come back here ```  Updating `ROAMLINK_RE` so the third matchgroup also excludes right brackets \"]\" fixed the issue.  However, it breaks the `test_converts_link_with_square_brackets_in_text` test case, which was a worthwhile tradeoff for me.") | 3 years agoApr 4, 2023 |
| [tests](https://github.com/peddamat/mkdocs-roamlinks-plugin/tree/master/tests "tests") | [tests](https://github.com/peddamat/mkdocs-roamlinks-plugin/tree/master/tests "tests") | [Added "crazy\_image\_link" test case and cleaned up regex.](https://github.com/peddamat/mkdocs-roamlinks-plugin/commit/b820e0e461fd267f5476089447190d76543cc5c1 "Added \"crazy_image_link\" test case and cleaned up regex.") | 3 years agoMar 29, 2023 |
| [.gitignore](https://github.com/peddamat/mkdocs-roamlinks-plugin/blob/master/.gitignore ".gitignore") | [.gitignore](https://github.com/peddamat/mkdocs-roamlinks-plugin/blob/master/.gitignore ".gitignore") | [from autolink to roamlink](https://github.com/peddamat/mkdocs-roamlinks-plugin/commit/666b1621c81a2e38a91d4547f11ba98ad68cfcdb "from autolink to roamlink") | 6 years agoSep 5, 2020 |
| [CHANGELOG.md](https://github.com/peddamat/mkdocs-roamlinks-plugin/blob/master/CHANGELOG.md "CHANGELOG.md") | [CHANGELOG.md](https://github.com/peddamat/mkdocs-roamlinks-plugin/blob/master/CHANGELOG.md "CHANGELOG.md") | [release: v0.3.0](https://github.com/peddamat/mkdocs-roamlinks-plugin/commit/20d8cd3a30562dc24f60a21fdaf4a8d134aa7a88 "release: v0.3.0") | 3 years agoMar 29, 2023 |
| [LICENSE](https://github.com/peddamat/mkdocs-roamlinks-plugin/blob/master/LICENSE "LICENSE") | [LICENSE](https://github.com/peddamat/mkdocs-roamlinks-plugin/blob/master/LICENSE "LICENSE") | [Initial commit](https://github.com/peddamat/mkdocs-roamlinks-plugin/commit/d1121bb9e24c46e634c1ffeaeba136ea21ec0f30 "Initial commit") | 7 years agoJan 14, 2020 |
| [README.md](https://github.com/peddamat/mkdocs-roamlinks-plugin/blob/master/README.md "README.md") | [README.md](https://github.com/peddamat/mkdocs-roamlinks-plugin/blob/master/README.md "README.md") | [Update README.md](https://github.com/peddamat/mkdocs-roamlinks-plugin/commit/5bce77a445ad930cbcf4a3f5ad7f7c80aca60ee3 "Update README.md") | 3 years agoMar 29, 2023 |
| [deploy.sh](https://github.com/peddamat/mkdocs-roamlinks-plugin/blob/master/deploy.sh "deploy.sh") | [deploy.sh](https://github.com/peddamat/mkdocs-roamlinks-plugin/blob/master/deploy.sh "deploy.sh") | [v0.2.0](https://github.com/peddamat/mkdocs-roamlinks-plugin/commit/ab8f9976be38b40f140125a0ecd8a00254e35e1b "v0.2.0") | 4 years agoAug 16, 2022 |
| [requirements.txt](https://github.com/peddamat/mkdocs-roamlinks-plugin/blob/master/requirements.txt "requirements.txt") | [requirements.txt](https://github.com/peddamat/mkdocs-roamlinks-plugin/blob/master/requirements.txt "requirements.txt") | [Initial commit](https://github.com/peddamat/mkdocs-roamlinks-plugin/commit/d1121bb9e24c46e634c1ffeaeba136ea21ec0f30 "Initial commit") | 7 years agoJan 14, 2020 |
| [setup.cfg](https://github.com/peddamat/mkdocs-roamlinks-plugin/blob/master/setup.cfg "setup.cfg") | [setup.cfg](https://github.com/peddamat/mkdocs-roamlinks-plugin/blob/master/setup.cfg "setup.cfg") | [Initial commit](https://github.com/peddamat/mkdocs-roamlinks-plugin/commit/d1121bb9e24c46e634c1ffeaeba136ea21ec0f30 "Initial commit") | 7 years agoJan 14, 2020 |
| [setup.py](https://github.com/peddamat/mkdocs-roamlinks-plugin/blob/master/setup.py "setup.py") | [setup.py](https://github.com/peddamat/mkdocs-roamlinks-plugin/blob/master/setup.py "setup.py") | [release: v0.3.0](https://github.com/peddamat/mkdocs-roamlinks-plugin/commit/20d8cd3a30562dc24f60a21fdaf4a8d134aa7a88 "release: v0.3.0") | 3 years agoMar 29, 2023 |
| View all files |

## Repository files navigation

# MkDocs Roamlinks Plugin

[Permalink: MkDocs Roamlinks Plugin](https://github.com/peddamat/mkdocs-roamlinks-plugin#mkdocs-roamlinks-plugin)

An MkDocs plugin that simplifies relative linking between documents and convert \[\[roamlinks\]\] for [vscode-foam](https://github.com/foambubble/foam) & [obsidian](https://obsidian.md/)

## Setup

[Permalink: Setup](https://github.com/peddamat/mkdocs-roamlinks-plugin#setup)

Install the plugin using pip:

`pip install mkdocs-roamlinks-plugin`

Activate the plugin in `mkdocs.yml`:

```
plugins:
  - search
  - roamlinks
```

## Usage

[Permalink: Usage](https://github.com/peddamat/mkdocs-roamlinks-plugin#usage)

To use this plugin, simply create a link that only contains the filename of file you wish to link to.

| origin | convert |
| --- | --- |
| `[Git Flow](git_flow.md)` | `[Git Flow](../software/git_flow.md)` |
| `[[Git Flow]]` | `[Git Flow](../software/git_flow.md)` |
| `[[software/Git Flow]]` | `[software/Git Flow](../software/git_flow.md)` |
| `![[image.png]]` | `![image.png](../image/imag.png)` |
| `[[#Heading identifiers]]` | `[Heading identifiers in HTML](#heading-identifiers-in-html)` |
| `[[Git Flow#Heading]]` | `[Git Flow](../software/git_flow.md#heading)` |
| `![[image.png|Description|800x600]]` | `![Description](image.png){ width="600"; height="800" }` |

## TODO

[Permalink: TODO](https://github.com/peddamat/mkdocs-roamlinks-plugin#todo)

- [ ]  convert admonition, for example

[obsidian style admonition](https://help.obsidian.md/How+to/Use+callouts)

```
> [!info]
> something
```

to [mkdoc material style](https://squidfunk.github.io/mkdocs-material/reference/admonitions/)

```
!!! note

    something
```

- [ ] `%% comment %%` to `<!-- comment -->`

## About

An MkDocs plugin that automagically generates relative links between markdown pages


### Resources

[Readme](https://github.com/peddamat/mkdocs-roamlinks-plugin#readme-ov-file)

### License

[MIT license](https://github.com/peddamat/mkdocs-roamlinks-plugin#MIT-1-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/peddamat/mkdocs-roamlinks-plugin).

[Activity](https://github.com/peddamat/mkdocs-roamlinks-plugin/activity)

### Stars

**0**
stars


### Watchers

**0**
watching


### Forks

[**1**\\
fork](https://github.com/peddamat/mkdocs-roamlinks-plugin/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fpeddamat%2Fmkdocs-roamlinks-plugin&report=peddamat+%28user%29)

## [Releases](https://github.com/peddamat/mkdocs-roamlinks-plugin/releases)

No releases published

## [Packages\  0](https://github.com/users/peddamat/packages?repo_name=mkdocs-roamlinks-plugin)

No packages published

## [Contributors\  0](https://github.com/peddamat/mkdocs-roamlinks-plugin/graphs/contributors)

No contributors


## Languages

- Python99.2%
- Shell0.8%

You can’t perform that action at this time.