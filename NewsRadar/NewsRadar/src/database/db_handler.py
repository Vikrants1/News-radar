"""
src/database/db_handler.py
---------------------------
SQLite handler for storing and querying articles.

Schema:
  articles(id, title, url, source, description, published_at,
           url_hash UNIQUE, matched_keywords, saved_at)
"""

import sqlite3
import csv
import logging
import os
from datetime import datetime
from typing import Optional

from src.scraper.rss_scraper import Article

logger = logging.getLogger(__name__)


class DatabaseHandler:

    def __init__(self, db_path: str = "outputs/newsradar.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()

    # ─────────────── SETUP ───────────────────────────────

    def _init_db(self):
        """Create tables if they don't exist."""
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS articles (
                    id               INTEGER PRIMARY KEY AUTOINCREMENT,
                    title            TEXT NOT NULL,
                    url              TEXT NOT NULL,
                    source           TEXT,
                    description      TEXT,
                    published_at     TEXT,
                    url_hash         TEXT UNIQUE NOT NULL,
                    matched_keywords TEXT,
                    saved_at         TEXT NOT NULL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_saved_at ON articles(saved_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_source   ON articles(source)")

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # ─────────────── WRITE ───────────────────────────────

    def save_articles(self, articles: list[Article]) -> tuple[int, int]:
        """
        Insert articles, skip duplicates (by url_hash).
        Returns (saved_count, duplicate_count).
        """
        saved = 0
        duplicates = 0
        with self._connect() as conn:
            for article in articles:
                try:
                    conn.execute("""
                        INSERT INTO articles
                          (title, url, source, description, published_at,
                           url_hash, matched_keywords, saved_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        article.title,
                        article.url,
                        article.source,
                        article.description,
                        article.published_at,
                        article.url_hash,
                        ",".join(article.matched_keywords),
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    ))
                    saved += 1
                except sqlite3.IntegrityError:
                    duplicates += 1
        logger.info(f"DB: saved={saved}, duplicates_skipped={duplicates}")
        return saved, duplicates

    # ─────────────── READ ────────────────────────────────

    def get_recent_articles(self, limit: int = 20, since_hours: int = 24) -> list[dict]:
        """Get articles saved in the last N hours."""
        with self._connect() as conn:
            rows = conn.execute("""
                SELECT * FROM articles
                WHERE saved_at >= datetime('now', ?)
                ORDER BY saved_at DESC
                LIMIT ?
            """, (f"-{since_hours} hours", limit)).fetchall()
        return [dict(row) for row in rows]

    def get_all_articles(self) -> list[dict]:
        """Fetch all articles for export."""
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM articles ORDER BY saved_at DESC").fetchall()
        return [dict(row) for row in rows]

    def get_stats(self) -> dict:
        """Return summary statistics."""
        with self._connect() as conn:
            total   = conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
            sources = conn.execute("SELECT COUNT(DISTINCT source) FROM articles").fetchone()[0]
            latest  = conn.execute("SELECT MAX(saved_at) FROM articles").fetchone()[0]
        return {"total_articles": total, "unique_sources": sources, "latest_saved": latest}

    def article_exists(self, url_hash: str) -> bool:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM articles WHERE url_hash = ?", (url_hash,)
            ).fetchone()
        return row is not None

    # ─────────────── EXPORT ──────────────────────────────

    def export_to_csv(self, output_path: str = "outputs/articles.csv") -> str:
        """Export all articles to CSV."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        articles = self.get_all_articles()
        if not articles:
            logger.warning("No articles to export.")
            return output_path

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=articles[0].keys())
            writer.writeheader()
            writer.writerows(articles)

        logger.info(f"Exported {len(articles)} articles to {output_path}")
        return output_path
