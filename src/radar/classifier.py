from __future__ import annotations

from .models import PainPoint

CATEGORY_KEYWORDS = {
    "价格与付费": ("price", "pricing", "expensive", "cost", "付费", "价格", "贵", "预算"),
    "可靠性与质量": ("bug", "broken", "error", "reliable", "hallucination", "崩溃", "错误", "不稳定"),
    "易用性与流程": ("confusing", "hard to use", "workflow", "onboarding", "复杂", "不会用", "麻烦", "流程"),
    "集成与兼容": ("integration", "api", "export", "import", "compatibility", "集成", "兼容", "接口"),
    "隐私与合规": ("privacy", "security", "compliance", "data", "隐私", "安全", "合规", "数据"),
    "需求缺口": ("wish", "missing", "need a", "feature request", "希望", "缺少", "需要", "功能"),
}


def classify(title: str, text: str, source: str, url: str, score: float = 0) -> PainPoint:
    corpus = f"{title} {text}".lower()
    category, hits = "其他", 0
    for label, words in CATEGORY_KEYWORDS.items():
        count = sum(word.lower() in corpus for word in words)
        if count > hits:
            category, hits = label, count
    urgency = "高" if any(w in corpus for w in ("urgent", "blocking", "cannot", "broken", "崩溃", "无法")) else "中" if hits else "低"
    audience = "开发者" if any(w in corpus for w in ("api", "developer", "code", "sdk", "开发")) else "团队/企业" if any(w in corpus for w in ("team", "company", "enterprise", "客户")) else "个人用户"
    return PainPoint(title=title, summary=text[:500], source=source, url=url, score=score, category=category, urgency=urgency, audience=audience, evidence=f"关键词命中 {hits} 项")
