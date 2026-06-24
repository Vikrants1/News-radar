"""
tests/test_newsradar.py
------------------------
Unit tests for NewsRadar — run with: pytest tests/ -v
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import tempfile
import json

from src.scraper.rss_scraper import RssScraper, Article
from src.database.db_handler import DatabaseHandler
from src.notifier.email_notifier import EmailNotifier
from src.config_loader import load_config


# ══════════════════════════════════════════════
#  FIXTURES
# ══════════════════════════════════════════════

@pytest.fixture
def sample_articles():
    scraper = RssScraper(keywords=["AI", "Python"])
    articles = [
        Article(
            title="AI Revolution in 2025",
            url="https://example.com/ai-revolution",
            source="TechNews",
            description="Artificial Intelligence is transforming everything.",
            published_at="2025-06-01 08:00:00",
            matched_keywords=["AI"],
        ),
        Article(
            title="Python 4.0 Released",
            url="https://example.com/python-4",
            source="DevBlog",
            description="Python version 4 ships with exciting new features.",
            published_at="2025-06-01 09:00:00",
            matched_keywords=["Python"],
        ),
    ]
    return articles

@pytest.fixture
def temp_db(tmp_path):
    db_path = str(tmp_path / "test.db")
    return DatabaseHandler(db_path=db_path)

@pytest.fixture
def email_config():
    return {
        "sender": "test@example.com",
        "password": "testpass",
        "recipients": ["recipient@example.com"],
        "smtp_host": "smtp.gmail.com",
        "smtp_port": 587,
    }


# ══════════════════════════════════════════════
#  ARTICLE TESTS
# ══════════════════════════════════════════════

class TestArticle:

    def test_url_hash_generated(self):
        a = Article("Title", "https://example.com", "Source", "Desc", "2025-01-01")
        assert len(a.url_hash) == 64  # SHA256 hex length

    def test_url_hash_is_deterministic(self):
        a1 = Article("T", "https://example.com/same", "S", "D", "2025-01-01")
        a2 = Article("T", "https://example.com/same", "S", "D", "2025-01-01")
        assert a1.url_hash == a2.url_hash

    def test_different_urls_different_hashes(self):
        a1 = Article("T", "https://example.com/one", "S", "D", "2025-01-01")
        a2 = Article("T", "https://example.com/two", "S", "D", "2025-01-01")
        assert a1.url_hash != a2.url_hash

    def test_to_dict_keys(self):
        a = Article("Title", "https://x.com", "Src", "Desc", "2025-01-01", matched_keywords=["AI"])
        d = a.to_dict()
        assert "title" in d
        assert "url_hash" in d
        assert "matched_keywords" in d


# ══════════════════════════════════════════════
#  SCRAPER TESTS
# ══════════════════════════════════════════════

class TestRssScraper:

    def test_keyword_match(self):
        scraper = RssScraper(keywords=["Python", "AI"])
        matched = scraper._match_keywords("Python is great for AI development")
        assert "Python" in matched
        assert "AI" in matched

    def test_keyword_no_match(self):
        scraper = RssScraper(keywords=["Java", "Kotlin"])
        matched = scraper._match_keywords("This article is about Python and Go")
        assert matched == []

    def test_keyword_case_insensitive(self):
        scraper = RssScraper(keywords=["machine learning"])
        matched = scraper._match_keywords("Machine Learning is evolving fast")
        assert "machine learning" in matched

    def test_clean_html(self):
        raw  = "<p>Hello <b>World</b></p>"
        clean = RssScraper._clean_html(raw)
        assert "<" not in clean
        assert "Hello" in clean
        assert "World" in clean

    def test_empty_keywords(self):
        scraper = RssScraper(keywords=[])
        matched = scraper._match_keywords("AI Python Java")
        assert matched == []


# ══════════════════════════════════════════════
#  DATABASE TESTS
# ══════════════════════════════════════════════

class TestDatabaseHandler:

    def test_save_and_retrieve(self, temp_db, sample_articles):
        saved, dupes = temp_db.save_articles(sample_articles)
        assert saved == 2
        assert dupes == 0

    def test_duplicate_detection(self, temp_db, sample_articles):
        temp_db.save_articles(sample_articles)
        saved, dupes = temp_db.save_articles(sample_articles)
        assert saved == 0
        assert dupes == 2

    def test_article_exists(self, temp_db, sample_articles):
        temp_db.save_articles(sample_articles)
        assert temp_db.article_exists(sample_articles[0].url_hash) is True

    def test_article_not_exists(self, temp_db):
        assert temp_db.article_exists("nonexistanthash") is False

    def test_get_all_articles(self, temp_db, sample_articles):
        temp_db.save_articles(sample_articles)
        all_articles = temp_db.get_all_articles()
        assert len(all_articles) == 2

    def test_get_stats(self, temp_db, sample_articles):
        temp_db.save_articles(sample_articles)
        stats = temp_db.get_stats()
        assert stats["total_articles"] == 2
        assert stats["unique_sources"] == 2

    def test_export_to_csv(self, temp_db, sample_articles, tmp_path):
        temp_db.save_articles(sample_articles)
        csv_path = str(tmp_path / "export.csv")
        result = temp_db.export_to_csv(output_path=csv_path)
        assert os.path.exists(result)
        with open(result) as f:
            content = f.read()
        assert "AI Revolution" in content
        assert "Python 4.0" in content

    def test_empty_db_stats(self, temp_db):
        stats = temp_db.get_stats()
        assert stats["total_articles"] == 0


# ══════════════════════════════════════════════
#  NOTIFIER TESTS
# ══════════════════════════════════════════════

class TestEmailNotifier:

    def test_build_html_contains_title(self, email_config, sample_articles):
        notifier = EmailNotifier(email_config)
        article_dicts = [a.to_dict() for a in sample_articles]
        html = notifier._build_html(article_dicts)
        assert "AI Revolution in 2025" in html
        assert "Python 4.0 Released" in html

    def test_build_html_contains_links(self, email_config, sample_articles):
        notifier = EmailNotifier(email_config)
        article_dicts = [a.to_dict() for a in sample_articles]
        html = notifier._build_html(article_dicts)
        assert "https://example.com/ai-revolution" in html

    def test_dry_run_saves_html(self, email_config, sample_articles, tmp_path):
        notifier = EmailNotifier(email_config)
        article_dicts = [a.to_dict() for a in sample_articles]
        # Patch save path
        orig = EmailNotifier._save_html
        EmailNotifier._save_html = staticmethod(lambda html: str(tmp_path / "digest.html"))
        result = notifier.send_digest(article_dicts, dry_run=True)
        EmailNotifier._save_html = staticmethod(orig)
        assert result is True

    def test_empty_articles_returns_false(self, email_config):
        notifier = EmailNotifier(email_config)
        result = notifier.send_digest([], dry_run=True)
        assert result is False

    def test_article_card_html(self, email_config):
        notifier = EmailNotifier(email_config)
        card = notifier._article_card({
            "title": "Test Article",
            "url": "https://test.com",
            "source": "TestSource",
            "description": "A test description.",
            "published_at": "2025-06-01 08:00:00",
            "matched_keywords": "AI,Python",
        })
        assert "Test Article" in card
        assert "#AI" in card
        assert "#Python" in card


# ══════════════════════════════════════════════
#  CONFIG TESTS
# ══════════════════════════════════════════════

class TestConfigLoader:

    def test_valid_config_loads(self, tmp_path):
        cfg = {
            "keywords": ["AI"],
            "feeds": ["https://example.com/feed"],
            "email": {"sender": "a@b.com", "password": "x",
                      "recipients": ["c@d.com"]},
            "schedule_time": "08:00",
            "db_path": "outputs/test.db"
        }
        path = tmp_path / "config.json"
        path.write_text(json.dumps(cfg))
        loaded = load_config(str(path))
        assert loaded["keywords"] == ["AI"]

    def test_missing_key_raises(self, tmp_path):
        cfg = {"keywords": ["AI"]}  # missing required keys
        path = tmp_path / "config.json"
        path.write_text(json.dumps(cfg))
        with pytest.raises(ValueError):
            load_config(str(path))

    def test_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            load_config("/nonexistent/config.json")
