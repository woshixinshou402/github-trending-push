# GitHub Trending Daily Push

每日自动抓取 GitHub Trending 高星仓库，按编程语言分类，AI 智能总结，推送到微信。

## 特性

- **按语言分类** — 覆盖 20+ 主流编程语言，每种语言 TOP 5
- **微信推送** — 通过 WxPusher 推送到个人微信，免费 2000 条/天
- **AI 总结** — 可选的 LLM 摘要，提炼当日趋势主题和精选推荐
- **零成本运维** — GitHub Actions 驱动，Fork 即可用，无需服务器
- **智能去重** — 30 天历史记录，避免重复推送

## 快速开始

### 1. Fork 仓库

点击右上角 Fork，将仓库复制到你的账号下。

### 2. 获取 WxPusher Token

1. 打开 [wxpusher.zjiecode.com](https://wxpusher.zjiecode.com)
2. 微信扫码关注公众号
3. 获取 **Simple Push Token (SPT)**，格式为 `SPT_xxxx`

### 3. 配置 Secrets

在 Fork 后的仓库中：Settings → Secrets and variables → Actions → New repository secret

| Secret | 说明 | 必填 |
|--------|------|------|
| `WXPUSHER_SPT` | 简单模式：扫码即得的 Simple Push Token（`SPT_xxx`） | 二选一 |
| `WXPUSHER_APP_TOKEN` + `WXPUSHER_UID` | 标准模式：管理后台创建应用获取 | 二选一 |
| `LLM_API_KEY` | OpenAI 兼容 API Key | ❌ 可选 |
| `LLM_API_BASE` | API 地址，默认 `https://api.openai.com/v1` | ❌ 可选 |
| `LLM_MODEL` | 模型名，默认 `gpt-4o-mini` | ❌ 可选 |

### 4. 启用 Actions

进入 Actions 标签页，启用 workflows，然后手动触发 `GitHub Trending Daily Push` 测试。

### 5. 完成

每天北京时间 09:00 自动推送，你会在微信收到一条消息。

## 自定义配置

编辑 `config.py` 可以修改：

- `LANGUAGES` — 要抓取的语言列表
- `TOP_PER_LANGUAGE` — 每种语言展示几个仓库
- `TOP_OVERALL` — 全语言 TOP 几
- `MIN_TOTAL_STARS` — 最低 Star 门槛
- `TRENDING_PERIOD` — `"daily"` 或 `"weekly"`

## 推送效果示例

```
GitHub Trending 日报 | 2026-06-06

 今日总览
 今日趋势集中在 AI Agent 工具链与自托管替代方案，
 多个高星仓库聚焦于 LLM 推理优化...

 精选推荐：
  openclaw/openclaw — 本周增长最快的个人 AI 助手框架
  twentyhq/twenty — 开源 Salesforce 替代，已获 4.6 万星

 全语言 TOP 10
1. owner/awesome-repo — ⭐12,345 (+1,234)
   The best curated list of awesome things

 按语言分类
  Python
  1. ...
```

## 技术栈

- Python 3.12
- [gtrending](https://github.com/hedyhli/gtrending) — GitHub Trending 抓取
- [WxPusher](https://wxpusher.zjiecode.com) — 微信消息推送
- GitHub Actions — 定时任务

## License

MIT
