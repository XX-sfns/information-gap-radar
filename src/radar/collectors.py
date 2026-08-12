from __future__ import annotations

import datetime as dt
from typing import Any

import feedparser
import requests

from .classifier import classify
from .models import Item, Stock

HEADERS = {"User-Agent": "information-gap-radar/1.0 (public research dashboard)"}


def _get(url: str, params: dict[str, Any] | None = None) -> requests.Response:
    response = requests.get(url, params=params, headers=HEADERS, timeout=25)
    response.raise_for_status()
    return response


def collect_rss(sources: list[dict[str, str]], limit: int) -> list[Item]:
    items: list[Item] = []
    for source in sources:
        try:
            feed = feedparser.parse(_get(source["url"]).content)
            for entry in feed.entries[:limit]:
                items.append(Item(title=entry.get("title", "Untitled"), url=entry.get("link", ""), source=source["name"], summary=entry.get("summary", "")[:500], published=entry.get("published", ""), tags=["AI/科技"]))
        except Exception as error:  # a single feed must never break the daily report
            items.append(Item(title=f"采集失败：{source['name']}", url=source["url"], source="系统", summary=str(error), tags=["采集状态"]))
    return items


def collect_reddit(sources: list[dict[str, str]], limit: int) -> list:
    points = []
    for source in sources:
        try:
            subreddit, query = source["subreddit"], source.get("query", "")
            endpoint = f"https://www.reddit.com/r/{subreddit}/search.json" if query else f"https://www.reddit.com/r/{subreddit}/hot.json"
            params = {"q": query, "restrict_sr": "on", "sort": "new", "limit": limit} if query else {"limit": limit}
            for child in _get(endpoint, params).json()["data"]["children"]:
                post = child["data"]
                body = post.get("selftext", "")
                points.append(classify(post.get("title", ""), body, f"Reddit r/{subreddit}", f"https://www.reddit.com{post.get('permalink', '')}", float(post.get("score", 0))))
        except Exception:
            continue
    return points


def collect_hackernews(queries: list[str], limit: int) -> list:
    points = []
    for query in queries:
        try:
            hits = _get("https://hn.algolia.com/api/v1/search_by_date", {"query": query, "tags": "comment", "hitsPerPage": limit}).json()["hits"]
            for hit in hits:
                text = hit.get("comment_text", "").replace("<p>", " ").replace("</p>", " ")
                points.append(classify(hit.get("story_title") or query, text, "Hacker News", f"https://news.ycombinator.com/item?id={hit.get('objectID')}", float(hit.get("points") or 0)))
        except Exception:
            continue
    return points


def collect_github(queries: list[str], limit: int) -> list[Item]:
    items = []
    for query in queries:
        try:
            repos = _get("https://api.github.com/search/repositories", {"q": query, "sort": "stars", "order": "desc", "per_page": limit}).json().get("items", [])
            for repo in repos:
                items.append(Item(title=repo["full_name"], url=repo["html_url"], source="GitHub", summary=repo.get("description") or "", score=repo.get("stargazers_count", 0), tags=["AI/Agent", *repo.get("topics", [])[:3]], published=repo.get("updated_at", "")))
        except Exception:
            continue
    return sorted(items, key=lambda item: item.score, reverse=True)[:limit]


def collect_github_issues(queries: list[str], limit: int) -> list:
    """Public GitHub issues are direct feedback from developers and users."""
    points = []
    for query in queries:
        try:
            issues = _get("https://api.github.com/search/issues", {"q": query, "sort": "updated", "order": "desc", "per_page": limit}).json().get("items", [])
            for issue in issues:
                points.append(classify(issue.get("title", ""), issue.get("body") or "", "GitHub Issues", issue.get("html_url", ""), float(issue.get("comments", 0))))
        except Exception:
            continue
    return points


def collect_stackexchange(tags: list[str], limit: int) -> list:
    """The unauthenticated Stack Exchange API is used conservatively and only for public questions."""
    points = []
    for tag in tags:
        try:
            questions = _get("https://api.stackexchange.com/2.3/questions", {"site": "stackoverflow", "tagged": tag, "pagesize": limit, "sort": "activity", "order": "desc", "filter": "withbody"}).json().get("items", [])
            for question in questions:
                points.append(classify(question.get("title", ""), question.get("body", ""), "Stack Overflow", question.get("link", ""), float(question.get("score", 0))))
        except Exception:
            continue
    return points


def collect_stocks(stocks: list[dict[str, str]]) -> list[Stock]:
    # Yahoo's public chart endpoint avoids a commercial key; data is informational, not investment advice.
    result = []
    for entry in stocks:
        stock = Stock(symbol=entry["symbol"], name=entry.get("name", entry["symbol"]))
        try:
            quote = _get(f"https://query1.finance.yahoo.com/v8/finance/chart/{stock.symbol}", {"range": "5d", "interval": "1d"}).json()["chart"]["result"][0]
            closes = [v for v in quote["indicators"]["quote"][0]["close"] if v is not None]
            stock.price = round(closes[-1], 2)
            stock.change_percent = round((closes[-1] / closes[-2] - 1) * 100, 2) if len(closes) > 1 else 0
            stock.signal = "关注" if stock.change_percent > 2 else "谨慎" if stock.change_percent < -2 else "观望"
            stock.rationale = f"近一交易日涨跌 {stock.change_percent:+.2f}%；只作信息展示，不构成投资建议。"
        except Exception as error:
            stock.rationale = f"行情采集失败：{error}"
        result.append(stock)
    return result


def today() -> str:
    return dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).strftime("%Y-%m-%d %H:%M CST")
