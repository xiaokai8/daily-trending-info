#!/usr/bin/env python3
"""Canonical source catalog shared by collectors, health checks, and metadata."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


DEFAULT_BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

HEADER_PROFILES: Dict[str, Dict[str, str]] = {
    "default": {},
    "reddit": {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 "
            "DailyTrendingBot/1.0"
        ),
        "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8",
    },
    "cmmc_reddit": {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 "
            "CMMCWatch/1.0"
        ),
        "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8",
    },
    # Breaking Defense blocks some automated user agents but allows simple browser-like strings.
    "breaking_defense": {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8",
    },
}

# Transport tuning used by both runtime collection and health checks.
DOMAIN_FETCH_PROFILES: Dict[str, Dict[str, object]] = {
    "feeds.washingtonpost.com": {
        "attempts": 3,
        "retry_delay": 0.8,
        "timeout": 20.0,
    },
    "breakingdefense.com": {
        "attempts": 2,
        "retry_delay": 0.6,
        "headers_profile": "breaking_defense",
        "timeout": 15.0,
    },
}


@dataclass(frozen=True)
class SourceSpec:
    key: str
    name: str
    url: str
    category: str
    kind: str  # rss | json | html
    source_key: Optional[str] = None  # Trend.source key
    collector: Optional[str] = None
    selector: Optional[str] = None
    json_count_path: Optional[str] = None
    timeout_seconds: Optional[float] = None
    headers_profile: str = "default"
    fallback_url: Optional[str] = None
    tier: int = 4
    source_type: str = "other"
    risk: str = "medium"
    language: str = "en"
    parser: str = "rss"
    healthcheck: bool = True


def _rss(
    key: str,
    name: str,
    url: str,
    category: str,
    collector: str,
    *,
    source_key: Optional[str] = None,
    timeout_seconds: Optional[float] = None,
    headers_profile: str = "default",
    fallback_url: Optional[str] = None,
    tier: int = 2,
    source_type: str = "news",
    risk: str = "low",
    parser: str = "rss",
) -> SourceSpec:
    return SourceSpec(
        key=key,
        name=name,
        url=url,
        category=category,
        kind="rss",
        source_key=source_key or key,
        collector=collector,
        timeout_seconds=timeout_seconds,
        headers_profile=headers_profile,
        fallback_url=fallback_url,
        tier=tier,
        source_type=source_type,
        risk=risk,
        parser=parser,
    )


def _json(
    key: str,
    name: str,
    url: str,
    category: str,
    *,
    source_key: Optional[str] = None,
    collector: Optional[str] = None,
    json_count_path: Optional[str] = None,
    tier: int = 3,
    source_type: str = "community",
    risk: str = "low",
    fallback_url: Optional[str] = None,
) -> SourceSpec:
    return SourceSpec(
        key=key,
        name=name,
        url=url,
        category=category,
        kind="json",
        source_key=source_key,
        collector=collector,
        json_count_path=json_count_path,
        fallback_url=fallback_url,
        tier=tier,
        source_type=source_type,
        risk=risk,
        parser="json_api",
    )


def _html(
    key: str,
    name: str,
    url: str,
    category: str,
    *,
    source_key: Optional[str] = None,
    collector: Optional[str] = None,
    selector: Optional[str] = None,
    tier: int = 3,
    source_type: str = "reference",
    risk: str = "low",
    fallback_url: Optional[str] = None,
) -> SourceSpec:
    return SourceSpec(
        key=key,
        name=name,
        url=url,
        category=category,
        kind="html",
        source_key=source_key,
        collector=collector,
        selector=selector,
        fallback_url=fallback_url,
        tier=tier,
        source_type=source_type,
        risk=risk,
        parser="html_scrape",
    )


# Canonical collector inputs.
COLLECTOR_SOURCES: List[SourceSpec] = [
    # -----------------------------------------------------------------------
    # 中文内容源（替换原英文RSS）
    # -----------------------------------------------------------------------
    _json(
        "baidu_hot",
        "百度热搜",
        "https://top.baidu.com/api/board?keyword=&tab=realtime",
        "news",
        source_key="baidu_hot",
        collector="baidu_hot",
        json_count_path="items",
        fallback_url="https://top.baidu.com/api/board?keyword=&tab=hot",
        tier=1,
        source_type="news",
    ),
    _json(
        "toutiao_hot",
        "今日头条热榜",
        "https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc",
        "news",
        source_key="toutiao_hot",
        collector="toutiao_hot",
        json_count_path="items",
        fallback_url="https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc",
        tier=1,
        source_type="news",
    ),
    _rss(
        "gnews_china",
        "Google News 中国",
        "https://news.google.com/rss/search?q=%E4%B8%AD%E5%9B%BD&hl=zh-CN&gl=CN&ceid=CN:zh-Hans",
        "news",
        "gnews_cn_rss",
        tier=1,
        source_type="news",
    ),
    _rss(
        "gnews_tech_cn",
        "Google News 科技",
        "https://news.google.com/rss/search?q=%E7%A7%91%E6%8A%80&hl=zh-CN&gl=CN&ceid=CN:zh-Hans",
        "tech",
        "gnews_tech_cn",
        tier=1,
        source_type="tech",
    ),
    _rss(
        "gnews_finance_cn",
        "Google News 财经",
        "https://news.google.com/rss/search?q=%E8%B4%A2%E7%BB%8F&hl=zh-CN&gl=CN&ceid=CN:zh-Hans",
        "finance",
        "gnews_finance_cn",
        tier=1,
        source_type="finance",
    ),
    _rss(
        "gnews_intl_cn",
        "Google News 国际",
        "https://news.google.com/rss/search?q=%E5%9B%BD%E9%99%85&hl=zh-CN&gl=CN&ceid=CN:zh-Hans",
        "news",
        "gnews_intl_cn",
        tier=2,
        source_type="news",
    ),
    # Hacker News, Dev.to, GitHub (英文社区，保留)
    _json(
        "hackernews_topstories",
        "Hacker News Top Stories",
        "https://hacker-news.firebaseio.com/v0/topstories.json",
        "community",
        source_key="hackernews",
        collector="hackernews",
        json_count_path="",
        fallback_url="https://hnrss.org/frontpage",
        tier=2,
        source_type="community",
    ),
    _json(
        "devto_api",
        "Dev.to API",
        "https://dev.to/api/articles?top=1&per_page=15",
        "community",
        source_key="devto",
        collector="devto",
        json_count_path="",
        fallback_url="https://dev.to/api/articles?top=1&per_page=15",
        tier=3,
        source_type="community",
    ),
    _json(
        "github_search_api",
        "GitHub Search API",
        "https://api.github.com/search/repositories?q=created:%3E2026-01-01&sort=stars&order=desc&per_page=10",
        "community",
        source_key="github_trending",
        json_count_path="items",
        fallback_url="https://github.com/trending?since=daily&spoken_language_code=en",
        tier=3,
        source_type="community",
    ),
    _json(
        "wikipedia_parse_api",
        "Wikipedia Parse API",
        "https://en.wikipedia.org/w/api.php?action=parse&page=Portal:Current_events&prop=text&format=json&formatversion=2",
        "reference",
        source_key="wikipedia_current",
        json_count_path="parse",
        fallback_url="https://en.wikipedia.org/wiki/Portal:Current_events",
        tier=3,
        source_type="reference",
    ),
    _html(
        "github_trending_html",
        "GitHub Trending HTML",
        "https://github.com/trending?since=daily&spoken_language_code=en",
        "community",
        source_key="github_trending",
        collector="github_trending",
        selector="article.Box-row",
        fallback_url="https://api.github.com/search/repositories?q=created:%3E2026-01-01&sort=stars&order=desc&per_page=10",
        tier=3,
        source_type="community",
    ),
    _json(
        "github_agent_top",
        "GitHub Agent Top Stars",
        "https://api.github.com/search/repositories?q=agent+llm+stars:%3E1000&sort=stars&order=desc&per_page=15",
        "community",
        source_key="github_agent",
        collector="github_agent",
        json_count_path="items",
        fallback_url="https://api.github.com/search/repositories?q=agent+llm+stars:%3E500&sort=stars&order=desc&per_page=10",
        tier=2,
        source_type="community",
    ),
    _json(
        "github_agent_fast",
        "GitHub Agent Fast-Growing",
        "https://api.github.com/search/repositories?q=agent+llm+created:>=2026-05-18+stars:%3E100&sort=stars&order=desc&per_page=15",
        "community",
        source_key="github_agent",
        collector="github_agent_fast",
        json_count_path="items",
        fallback_url="https://api.github.com/search/repositories?q=agent+framework+stars:%3E200&sort=stars&order=desc&per_page=10",
        tier=2,
        source_type="community",
    ),
    _html(
        "wikipedia_current_html",
        "Wikipedia Current Events HTML",
        "https://en.wikipedia.org/wiki/Portal:Current_events",
        "reference",
        source_key="wikipedia_current",
        collector="wikipedia_current",
        selector=".current-events-content li, .vevent li",
        fallback_url="https://en.wikipedia.org/w/api.php?action=parse&page=Portal:Current_events&prop=text&format=json&formatversion=2",
        tier=3,
        source_type="reference",
    ),
]


COLLECTOR_SOURCES_BY_GROUP: Dict[str, List[SourceSpec]] = {}
SOURCE_BY_KEY: Dict[str, SourceSpec] = {}

for source in COLLECTOR_SOURCES:
    SOURCE_BY_KEY[source.key] = source
    if source.collector:
        COLLECTOR_SOURCES_BY_GROUP.setdefault(source.collector, []).append(source)


def get_collector_sources(group: str) -> List[SourceSpec]:
    """Return sources used by a collector group."""
    return list(COLLECTOR_SOURCES_BY_GROUP.get(group, []))


def get_health_sources() -> List[SourceSpec]:
    """Return all sources included in health checks."""
    return [source for source in COLLECTOR_SOURCES if source.healthcheck]


def get_source_by_key(key: str) -> Optional[SourceSpec]:
    return SOURCE_BY_KEY.get(key)
