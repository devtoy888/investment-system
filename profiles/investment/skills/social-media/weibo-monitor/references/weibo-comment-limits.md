# 微博评论拉取限制与根因（2026-07实测）

## 现象
用 `fund_tools.get_weibo_comments(post_id)`（内部走 `weibo.com/aj/v6/comment/big`，`ajwvr=6`, `from=singleWeiBo`）拉评论时：
- 单条微博原评数 95 / 321 条，实测只返回 **3 + 7 条**样本。
- 翻页（page=2,3…）从第2页开始稳定为空（`html=''`），不是偶发限流。

## 根因（关键）
**不是请求太快/限流**——加重试(5次)+指数退避(2s)+长间隔(1-2s)翻页后，第2页依然稳定空。
这是**网页端 cookie 的评论读取权限被限制在"热门评论前几条"**：`aj/v6/comment/big` 对单条微博只放出第一页。

**全量评论在移动端接口** `m.weibo.cn/comments/hotflow`，但移动端需要**单独的登录态**：
- 网页端 cookie 不能跨端复用（实测 `m.weibo.cn/api/config` 返回 `"login": false`）。
- 要拉全量必须登录移动端（改登录 entry 为 `wapsso`，或用 `kabi-weibo-cli` 移动端登录流）拿到 m.weibo.cn cookie。

## 已实测失败的接口（不要再浪费时间试）
| 接口 | 结果 |
|------|------|
| `weibo.com/ajax/statuses/buildComments` (任意 flow/st/page 组合) | 始终 `{"ok":0,"message":"参数错误"}`（HTTP 400），需登录后CORS令牌 |
| `weibo.com/comments/hotflow` | HTTP 200 但返回 HTML 登录页 |
| `m.weibo.cn/comments/hotflow`（用网页cookie） | 返回"新浪通行证"登录页（`login:false`） |
| `m.weibo.cn/api/config`（用网页cookie） | `{"login":false}` 确认跨端不通用 |

## 正确做法
1. **接受样本限制**：用 `fund_tools.get_weibo_comments(post_id)` 拿热门样本（前几条），分析时明确标注"评论区样本显示…（非全量N条）"，绝不声称穷尽。
2. **要全量**：先登录移动端拿 m.weibo.cn cookie，再用 `m.weibo.cn/comments/hotflow?id=&mid=&max_id_type=0&page=` 翻页（移动端UA + Referer m.weibo.cn）。
3. 参数用 `post['id']`（数字ID，非 mblogid）。

## 当天微博+评论分析流程（已验证）
```
1. myblog feature=1 遍历 page=1..3 → 按 datetime.strptime(s,'%a %b %d %H:%M:%S %z %Y') 过滤当日
2. 逐条 get_weibo_comments(id) 拿样本
3. 开放词库统计（见 SKILL.md 开放提取铁律）+ 公司/框架词提取
4. 输出时标注样本量限制
```
