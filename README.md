# 每日信息差雷达

一个可免费部署在 GitHub Pages 的每日仪表盘。它在每天下午收盘后统一生成并提交报告，并写入 GitHub 上一个固定的日报 Issue：

- **科技 / AI**：RSS 新闻源；可在配置中继续加入行业媒体。
- **GitHub 热榜**：按 AI、LLM、Agent 主题检索近期活跃仓库。
- **股票决策**：自选股收盘价、单日涨跌与说明（仅信息展示，不构成投资建议）。
- **信息差**：Reddit 公开帖子、Hacker News 评论、GitHub Issues、Stack Overflow 公开提问；按价格、可靠性、流程、集成、隐私、需求缺口归类，保留原文链接和证据关键词。

## 先在 GitHub 新建仓库

在 GitHub 点击 **New repository**，建议命名为 `information-gap-radar`，选择 **Public**，不要勾选 README。随后在本地项目目录执行：

```powershell
git init
git add .
git commit -m "feat: initial daily radar"
git branch -M main
git remote add origin https://github.com/<你的用户名>/information-gap-radar.git
git push -u origin main
```

## 配置每日运行与消息

1. 进入仓库 **Settings → Actions → General → Workflow permissions**，选择 **Read and write permissions**。
2. 进入 **Settings → Secrets and variables → Actions**，按要使用的推送渠道添加密钥：
   - `FEISHU_WEBHOOK`：飞书群机器人 Webhook 完整地址；
   - 或 `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID`；
   - 或 `NOTIFY_WEBHOOK`：你自己的 Webhook 端点。
3. 打开 **Actions → Daily Information Gap Radar → Run workflow**，手动执行一次。之后自动在每天北京时间 17:30 运行、提交 `data/latest.json`，并发送消息。
4. 在 **Settings → Pages**，选择 **Deploy from a branch** → `main` → `/(root)`。仪表盘地址为 `https://<你的用户名>.github.io/information-gap-radar/`。
5. Actions 首次成功后，会自动创建一个名为 **📡 Daily Radar｜每日信息差报告（固定日报）** 的 Issue。打开它并点击 **Subscribe**；以后每日报告会作为该 Issue 的新评论出现，GitHub 的网页、手机 App、邮件通知都会指向这一个固定位置。每条评论还含有在线仪表盘链接和当天 Markdown 报告链接。

> 截图里的 Copilot Chat 是你发起问题的互动窗口，GitHub Actions 无法每天主动把内容写进该会话。固定日报 Issue 是 GitHub 原生可订阅、可长期追溯的替代方案；你的自由问答可继续在 Copilot Chat 中进行。

GitHub 的定时调度会有少量延迟；如果需要分钟级严格准点，应换用独立定时服务或 VPS。

## LLM 在哪里配置

LLM **只用于复核“信息差”模块的痛点类别、紧急度和目标人群**；没有 LLM 也会照常采集，并使用本地规则分类。

1. 直接编辑仓库根目录的 `config.yaml`；将其中 `llm.enabled` 改为 `true`，并填写 `model`、`base_url`。例如 DeepSeek：`model: deepseek-chat`、`base_url: https://api.deepseek.com/v1`。
2. 本地运行时，在 PowerShell 执行：`$env:LLM_API_KEY = '你的密钥'`。密钥不写入 YAML。
3. GitHub 上运行时，打开仓库 **Settings → Secrets and variables → Actions → New repository secret**，名称填 `LLM_API_KEY`，值填你的 API Key。工作流已自动读取它。
4. 提交 `config.yaml` 的变更即可生效；这个文件不能放密钥，密钥只放 GitHub Secrets。

推荐先用 DeepSeek、通义千问或 OpenAI 等任意 OpenAI 兼容接口；切换服务只需改 `model` 与 `base_url`。

## 本地验证

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:PYTHONPATH='src'
python -m pytest -q
python -m radar.cli --no-notify
python -m http.server 8000
```

然后打开 `http://localhost:8000`。不要直接双击 `index.html`：浏览器会限制 `file://` 页面读取 JSON；现在即使直接打开也可以切换标签，但只会展示演示数据。

也可以直接运行 `./run-once.ps1 -NoNotify`：它会首次复制配置模板、安装依赖并生成报告。配置通知密钥后，去掉 `-NoNotify` 即可发送消息。

## 扩展建议

- 将目标产品名与细分行业追加到 `reddit` 和 `hackernews_queries`，提高“用户痛点”命中率。
- `github_issue_queries` 与 `stackexchange_tags` 也是可配置的用户反馈入口；更大范围的站点应通过合规的官方 API / RSS 适配器接入，而不是绕过登录、付费墙或反爬机制。
- 只采集公开内容，遵守源站 ToS、速率限制与隐私规则；不要绕过登录、付费墙或反爬机制。
- 可在 `config.yaml` 中加入更多 RSS；生产配置不应提交到仓库。
