from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class Item:
    title: str
    url: str
    source: str
    summary: str = ""
    score: float = 0.0
    tags: list[str] = field(default_factory=list)
    published: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PainPoint(Item):
    category: str = "其他"
    urgency: str = "中"
    audience: str = "未识别"
    evidence: str = ""


@dataclass
class Stock:
    symbol: str
    name: str
    price: float | None = None
    change_percent: float | None = None
    signal: str = "观望"
    rationale: str = "数据源未返回有效行情"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
