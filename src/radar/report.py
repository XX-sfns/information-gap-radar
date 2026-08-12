from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from .llm import enrich_pain_points


def build(config: dict) -> dict:
    # Keep the small planning helpers importable for unit tests without collectors installed.
    from .collectors import collect_github, collect_github_issues, collect_hackernews, collect_reddit, collect_rss, collect_stackexchange, collect_stocks, today
    limit = config.get("project", {}).get("report_limit", 12)
    sources = config.get("sources", {})
    pains = (
        collect_reddit(sources.get("reddit", []), limit)
        + collect_hackernews(sources.get("hackernews_queries", []), max(3, limit // 3))
        + collect_github_issues(sources.get("github_issue_queries", []), max(3, limit // 3))
        + collect_stackexchange(sources.get("stackexchange_tags", []), max(3, limit // 3))
    )
    pains = sorted(pains, key=lambda item: (item.urgency == "高", item.score), reverse=True)[:limit]
    pains, llm_status = enrich_pain_points(pains, config.get("llm", {}))
    categories = Counter(item.category for item in pains)
    return {
        "generated_at": today(),
        "disclaimer": "股票模块仅供信息参考，不构成任何投资建议。用户内容会保留来源链接，分类是自动初筛，使用前请回看原文。",
        "ai_news": [x.to_dict() for x in collect_rss(sources.get("ai_rss", []), limit)],
        "github_trending": [x.to_dict() for x in collect_github(sources.get("github_queries", []), limit)],
        "stocks": [x.to_dict() for x in collect_stocks(config.get("stocks", []))],
        "information_gap": {"items": [x.to_dict() for x in pains], "category_counts": dict(categories), "next_actions": _actions(pains), "llm_status": llm_status or "规则分类（LLM 未启用）"},
    }


def _actions(pains: list) -> list[str]:
    if not pains:
        return ["今天未抓到可归类的公开评论；请检查源站可用性或扩展关键词。"]
    by_category = Counter(item.category for item in pains)
    return [f"优先验证「{label}」：今天出现 {count} 条公开用户信号，打开来源链接复核原话并判断是否值得访谈。" for label, count in by_category.most_common(3)]


def write(report: dict, root: Path) -> Path:
    data_dir = root / "data"
    history = data_dir / "history"
    reports = root / "reports"
    history.mkdir(parents=True, exist_ok=True)
    reports.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    (data_dir / "latest.json").write_text(payload, encoding="utf-8")
    dated = history / f"{report['generated_at'][:10]}.json"
    dated.write_text(payload, encoding="utf-8")
    (reports / f"{report['generated_at'][:10]}.md").write_text(markdown(report), encoding="utf-8")
    return dated


def markdown(report: dict) -> str:
    """The durable daily summary shown in the fixed GitHub Issue thread."""
    gap = report["information_gap"]
    lines = [
        f"# 每日信息差雷达 · {report['generated_at']}",
        "",
        f"- 科技 / AI：{len(report['ai_news'])} 条",
        f"- GitHub 热榜：{len(report['github_trending'])} 个项目",
        f"- 股票：{len(report['stocks'])} 只自选股",
        f"- 信息差：{len(gap['items'])} 条公开用户信号",
        f"- 分类方式：{gap.get('llm_status', '规则分类')}",
        "",
        "## 今日优先核验",
        *[f"- {action}" for action in gap["next_actions"]],
        "",
        "## 信息差 Top 信号",
    ]
    for item in gap["items"][:5]:
        lines.append(f"- **[{item['category']} / 紧急度 {item['urgency']}] [{item['title']}]({item['url']})** — {item['summary'][:180]}")
    lines.extend(["", "> 股票内容仅供信息参考，不构成投资建议。所有用户信号请回看原始链接。"])
    return "\n".join(lines)
