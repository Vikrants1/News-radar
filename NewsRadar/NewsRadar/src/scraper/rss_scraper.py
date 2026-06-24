"""
src/scraper/rss_scraper.py
---------------------------
Fetches and parses RSS feeds, filters articles by keywords.

Flow:
  fetch_feed(url) → parse entries → filter_by_keywords() → list[Article]
"""

import re
import hashlib
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import feedparser
import requests

logger = logging.getLogger(__name__)


@dataclass
class Article:
    title: str
    url: str
    source: str
    description: str
    published_at: str
    url_hash: str = field(init=False)
    matched_keywords: list[str] = field(default_factory=list)

    def __post_init__(self):
        # SHA256 of URL — used for deduplication
        self.url_hash = hashlib.sha256(self.url.strip().encode()).hexdigest()

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "url": self.url,
            "source": self.source,
            "description": self.description,
            "published_at": self.published_at,
            "url_hash": self.url_hash,
            "matched_keywords": ",".join(self.matched_keywords),
        }


class RssScraper:

    def __init__(self, keywords: list[str], timeout: int = 10):
        self.keywords = keywords
        self.timeout = timeout
        # Compile keyword patterns for fast matching (case-insensitive)
        self._patterns = [
            re.compile(rf"\b{re.escape(kw)}\b", re.IGNORECASE)
            for kw in keywords
        ]

    # ─────────────── PUBLIC API ──────────────────────────

    def scrape_feeds(self, feed_urls: list[str]) -> list[Article]:
        """Scrape all feeds and return filtered articles."""
        all_articles = []
        for url in feed_urls:
            try:
                articles = self._fetch_and_parse(url)
                all_articles.extend(articles)
                logger.info(f"  ✓ {url} → {len(articles)} articles matched")
            except Exception as e:
                logger.warning(f"  ✗ Failed to fetch {url}: {e}")
        return all_articles

    # ─────────────── INTERNAL ────────────────────────────

    def _fetch_and_parse(self, feed_url: str) -> list[Article]:
        """Fetch one RSS feed and filter entries by keywords."""
        # Use requests for timeout control, then pass to feedparser
        try:
            response = requests.get(feed_url, timeout=self.timeout, headers={
                "User-Agent": "NewsRadar-Bot/1.0"
            })
            response.raise_for_status()
            feed = feedparser.parse(response.text)
        except requests.RequestException:
            # Fallback: let feedparser handle it directly
            feed = feedparser.parse(feed_url)

        source = feed.feed.get("title", feed_url)
        articles = []

        for entry in feed.entries:
            title       = entry.get("title", "").strip()
            url         = entry.get("link", "").strip()
            description = self._clean_html(entry.get("summary", ""))
            published   = self._parse_date(entry)

            if not title or not url:
                continue

            matched = self._match_keywords(title + " " + description)
            if matched:
                articles.append(Article(
                    title=title,
                    url=url,
                    source=source,
                    description=description[:400],
                    published_at=published,
                    matched_keywords=matched,
                ))

        return articles

    def _match_keywords(self, text: str) -> list[str]:
        """Return list of keywords found in text."""
        return [
            kw for kw, pattern in zip(self.keywords, self._patterns)
            if pattern.search(text)
        ]

    @staticmethod
    def _clean_html(text: str) -> str:
        """Strip HTML tags from description."""
        return re.sub(r"<[^>]+>", "", text).strip()

    @staticmethod
    def _parse_date(entry) -> str:
        """Extract publish date, fallback to now."""
        for field in ("published", "updated", "created"):
            if hasattr(entry, field):
                return str(getattr(entry, field))
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
