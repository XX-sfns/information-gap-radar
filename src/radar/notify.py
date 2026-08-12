from __future__ import annotations

import os
import requests


def message(report: dict) -> str:
    gap = report["information_gap"]
    top = "、".join(f"{name} {count}" for name, count in gap["category_counts"].items()) or "暂无"
    return f"【每日信息差雷达】{report['generated_at']}\nAI/科技 {len(report['ai_news'])} 条｜GitHub {len(report['github_trending'])} 个｜股票 {len(report['stocks'])} 只｜用户痛点 {len(gap['items'])} 条\n痛点分布：{top}\n打开 GitHub Pages 查看原文与分类。"


def notify(report: dict, config: dict) -> list[str]:
    settings = config.get("notifications", {})
    text, sent = message(report), []
    feishu = os.getenv(settings.get("feishu_webhook_env", "FEISHU_WEBHOOK"))
    if feishu:
        requests.post(feishu, json={"msg_type": "text", "content": {"text": text}}, timeout=20).raise_for_status(); sent.append("Feishu")
    token, chat_id = os.getenv(settings.get("telegram_bot_token_env", "TELEGRAM_BOT_TOKEN")), os.getenv(settings.get("telegram_chat_id_env", "TELEGRAM_CHAT_ID"))
    if token and chat_id:
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={"chat_id": chat_id, "text": text}, timeout=20).raise_for_status(); sent.append("Telegram")
    webhook = os.getenv(settings.get("webhook_env", "NOTIFY_WEBHOOK"))
    if webhook:
        requests.post(webhook, json={"text": text, "report": report}, timeout=20).raise_for_status(); sent.append("Webhook")
    return sent
