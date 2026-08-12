from radar.report import _actions, markdown
from radar.classifier import classify


def test_actions_prioritize_detected_category():
    pain = classify("Bug blocks workflow", "The API is broken", "HN", "https://example.com")
    assert "可靠性与质量" in _actions([pain])[0]


def test_markdown_contains_fixed_issue_summary_data():
    report = {
        "generated_at": "2026-08-12 17:30 CST", "ai_news": [1], "github_trending": [1], "stocks": [1],
        "information_gap": {"llm_status": "规则分类", "next_actions": ["验证需求"], "items": [classify("Need cheaper pricing", "too expensive", "Reddit", "https://example.com").to_dict()]},
    }
    text = markdown(report)
    assert "每日信息差雷达" in text
    assert "https://example.com" in text
