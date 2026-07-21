[跳转至](https://wiki.devtoy.xyz/concepts/knowledge-graph/#_1)

# 知识图谱 [¶](https://wiki.devtoy.xyz/concepts/knowledge-graph/\#_1 "Permanent link")

> LLM Wiki 知识图谱由 Graphify 自动生成，使用 Leiden 算法进行社区发现和自动分类。

* * *

## 图谱概览 [¶](https://wiki.devtoy.xyz/concepts/knowledge-graph/\#_2 "Permanent link")

| 指标 | 值 |
| --- | --- |
| 节点数 | 593 |
| 边数 | 571 |
| 社区数 | 41 |

![知识图谱可视化](https://wiki.devtoy.xyz/images/knowledge-graph.svg?v=3)

+−↺

463%

🖲️ 滚轮缩放 · 拖拽平移 · 双击放大 · Ctrl+0 重置

_图谱说明：每个节点代表一个概念/实体，连线代表关联关系，颜色代表社区分类。_

## 社区分类 [¶](https://wiki.devtoy.xyz/concepts/knowledge-graph/\#_3 "Permanent link")

| # | 社区名称 | 节点数 | 说明 |
| --- | --- | --- | --- |
| 0 | 知识图谱（自引用） | 46 | 图谱页面自身、可视化文件 |
| 1 | Wiki 搭建方案 | 36 | setup-guide 配置、架构决策 |
| 2 | 等保测评过程 | 29 | GB/T 28449-2018 测评过程指南 |
| 3 | 数据安全基本要求 | 29 | 5级×11维度要求概要 |
| 4 | 等保测评要求 | 27 | GB/T 28448-2019 测评要求 |
| 5 | Vibe-Trading 总览 | 26 | 项目概览、核心能力 |
| 6 | 站点首页与查询 | 21 | index.md、query 页面 |
| 7 | 等保报告编制 | 21 | 测评报告编制活动 |
| 8 | Vibe-Trading MCP | 17 | MCP 插件与生态集成 |
| 9 | Shadow Account | 17 | 多智能体与交易诊断 |
| 10 | 现场测评活动 | 17 | 现场测评流程 |
| 11 | Alpha 因子库 | 16 | 460 个预构建因子 |
| 12 | Vibe 安装使用 | 15 | 安装与基础使用 |
| 13 | 数据源与回测 | 15 | 19 数据源、7 回测引擎 |
| 14 | 测评机构能力 | 14 | 机构分级和能力规范 |

## 🌟 高连接度节点（God Nodes） [¶](https://wiki.devtoy.xyz/concepts/knowledge-graph/\#god-nodes "Permanent link")

由 Graphify 社区检测算法自动发现的知识网络枢纽节点：

| 节点 | 连接数 | 所属社区 | 典型关联 |
| --- | --- | --- | --- |
| index.md | 28 | 首页导航 | 等保标准对比、6维分析框架 |
| setup-guide（搭建方案） | 15 | 搭建方案 | 架构决策、Obsidian同步、Graphify集成 |
| 十三、Graphify 集成 | 12 | 图谱构建 | 字体配置、安装脚本 |
| GB/T 28448-2019 测评要求 | 11 | 等保测评 | 标准体系、安全维度 |
| GB/T 28449-2018 过程指南 | 12 | 等保测评 | 测评流程、评估方法 |
| 网络安全等级保护概述 | 8 | 等保总览 | 分级体系、安全维度、起草单位 |
| 数据安全基本要求 | 8 | 数据安全 | 5级×11维度、关键要求 |
| 测评机构能力要求 | 8 | 机构资质 | 2018 vs 2026版变化 |
| Wiki Log（变更日志） | 10 | 日志 | 全部历史变更记录 |
| Vibe-Trading 项目总览 | 7 | Vibe-Trading | 四大核心能力、生态项目 |

> God Nodes 表示在图谱中连接最多的节点，反映知识网络的枢纽和热点区域。

## 可视化文件 [¶](https://wiki.devtoy.xyz/concepts/knowledge-graph/\#_4 "Permanent link")

| 文件 | 路径 | 用途 |
| --- | --- | --- |
| graph.svg | graphify-out/graph.svg | 静态图谱图片 |
| graph.json | graphify-out/graph.json | 结构化图数据（供查询） |
| graph.canvas | graphify-out/graph.canvas | Obsidian Canvas 画布 |

## 自动分类机制 [¶](https://wiki.devtoy.xyz/concepts/knowledge-graph/\#_5 "Permanent link")

1. **提取**：分析每个 Markdown 文件的标题结构、frontmatter、内容
2. **建图**：构建节点（概念）-边（关系）的知识图谱
3. **聚类**：Leiden 算法自动检测社区结构
4. **标注**：为每个社区自动分类

## 重建图谱 [¶](https://wiki.devtoy.xyz/concepts/knowledge-graph/\#_6 "Permanent link")

每日 04:00 自动重建。

* * *

## 交互式浏览 [¶](https://wiki.devtoy.xyz/concepts/knowledge-graph/\#_7 "Permanent link")

[打开交互式图谱浏览器 →](https://wiki.devtoy.xyz/concepts/graph-viewer/)

> 支持拖拽、缩放、悬停高亮、按社区着色。

* * *

## 查看图谱 [¶](https://wiki.devtoy.xyz/concepts/knowledge-graph/\#_8 "Permanent link")

- 🖥️ **交互式图谱**（拖拽/缩放）：（页面待创建）
- 🖼️ **静态图**（嵌入）：见上方 SVG
- 📁 **Obsidian Canvas**：`graphify-out/graph.canvas`

* * *

## 📊 图谱关联 [¶](https://wiki.devtoy.xyz/concepts/knowledge-graph/\#_9 "Permanent link")

由 Graphify 知识图谱自动计算的相关页面：

- [index](https://wiki.devtoy.xyz/concepts/knowledge-graph/index)
- [graph viewer](https://wiki.devtoy.xyz/concepts/knowledge-graph/concepts/graph-viewer)
- [index](https://wiki.devtoy.xyz/concepts/knowledge-graph/concepts/index)

回到页面顶部