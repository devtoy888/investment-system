# R2 上传规范

> 用户多次纠正R2上传问题（2026-07-20），根因是content-type缺少charset=utf-8 → 浏览器打开显示乱码。**本文件记录了所有上传规则。**

## 上传铁律

### 1. content-type 必须带 charset=utf-8

```python
# ❌ 错误（浏览器打开乱码）
u.upload_file(path, key, 'text/markdown')

# ✅ 正确
u.upload_file(path, key, 'text/markdown; charset=utf-8')
u.upload_file(path, key, 'text/html; charset=utf-8')
u.upload_file(path, key, 'text/csv; charset=utf-8')
```

### 2. MD 和 HTML 必须成对上传

每个分析报告至少两个文件：
- `xxx.md` — 原始markdown（数据源）
- `xxx.html` — 用marked.js动态渲染MD的预览页

HTML页面必须使用 `fetch('xxx.md?v=' + Date.now())` 来引用MD文件（加时间戳防缓存），而不是硬编码内容。

### 3. R2文件路径约定

| 内容 | 路径前缀 |
|:-----|:---------|
| 系统设计文档 | `fund-system/strategy/` |
| 进化/路线图 | `fund-system/evolution/` |
| 分析报告 | `fund-system/reports/` |
| 持仓快照 | `fund-system/data/portfolio/` |
| KOL档案 | `fund-system/data/kol_profiles/` |

### 4. 操作记录必须同步到本地

操作记录存在R2的 `fund-system/operations/operation_YYYY-MM-DD.md`，但本地 `/opt/data/fund_system_data/operations/` 目录也必须同步，因为 cron 脚本的 `parse_ops()` 读的是本地文件而不是R2。

## 常见错误检查清单

```python
# 上传前检查
checks = []
if 'charset=' not in content_type:
    checks.append('❌ content-type缺少charset=utf-8')
if not has_html:
    checks.append('❌ 只有MD没有HTML')
if not has_local_copy:
    checks.append('❌ 操作记录未同步到本地')
if checks:
    print(f"R2上传检查失败: {checks}")
```
