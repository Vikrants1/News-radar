"""
main.py
--------
NewsRadar CLI — entry point.

Commands:
  python main.py scrape    — Scrape feeds & save to DB
  python main.py digest    — Send email digest (dry_run saves HTML)
  python main.py schedule  — Start daily scheduler
  python main.py export    — Export DB to CSV
  python main.py stats     — Show DB statistics
"""

import sys
import os
import logging

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from src.config_loader import load_config
from src.scraper.rss_scraper import RssScraper
from src.database.db_handler import DatabaseHandler
from src.notifier.email_notifier import EmailNotifier
from src.scheduler.job_scheduler import JobScheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)


def get_components():
    config  = load_config()
    scraper = RssScraper(keywords=config["keywords"])
    db      = DatabaseHandler(db_path=config["db_path"])
    emailer = EmailNotifier(email_config=config["email"])
    return config, scraper, db, emailer


def cmd_scrape():
    print("\n🔍 Scraping RSS feeds...\n")
    config, scraper, db, _ = get_components()

    articles = scraper.scrape_feeds(config["feeds"])
    print(f"\n  Found {len(articles)} matching articles across {len(config['feeds'])} feeds.")

    saved, dupes = db.save_articles(articles)
    print(f"  ✅ Saved: {saved}  |  Duplicates skipped: {dupes}\n")
    return saved, dupes


def cmd_digest(dry_run: bool = True):
    print("\n📧 Sending digest...\n")
    config, _, db, emailer = get_components()

    articles = db.get_recent_articles(
        limit=config.get("max_articles_per_digest", 20),
        since_hours=24
    )

    if not articles:
        print("  ⚠️  No recent articles found. Run 'scrape' first.\n")
        return

    print(f"  Building digest with {len(articles)} articles...")
    success = emailer.send_digest(articles, dry_run=dry_run)
    if success:
        print("  ✅ Digest ready!\n")
    else:
        print("  ❌ Failed to send digest.\n")


def cmd_schedule():
    config, scraper, db, emailer = get_components()

    def scrape_fn():
        articles = scraper.scrape_feeds(config["feeds"])
        return db.save_articles(articles)

    def digest_fn():
        articles = db.get_recent_articles(limit=config.get("max_articles_per_digest", 20))
        emailer.send_digest(articles, dry_run=False)

    scheduler = JobScheduler(
        scrape_fn=scrape_fn,
        digest_fn=digest_fn,
        schedule_time=config.get("schedule_time", "08:00"),
    )
    scheduler.start()


def cmd_export():
    print("\n📤 Exporting to CSV...\n")
    config, _, db, _ = get_components()
    path = db.export_to_csv(output_path=config.get("export_path", "outputs/articles.csv"))
    print(f"  ✅ Exported to: {path}\n")


def cmd_stats():
    print("\n📊 Database Statistics\n")
    config, _, db, _ = get_components()
    stats = db.get_stats()
    print(f"  Total articles   : {stats['total_articles']}")
    print(f"  Unique sources   : {stats['unique_sources']}")
    print(f"  Latest saved at  : {stats['latest_saved']}\n")


COMMANDS = {
    "scrape":   cmd_scrape,
    "digest":   lambda: cmd_digest(dry_run=True),
    "schedule": cmd_schedule,
    "export":   cmd_export,
    "stats":    cmd_stats,
}

HELP = """
╔══════════════════════════════════════════╗
║           📰 NewsRadar Bot               ║
╚══════════════════════════════════════════╝

Usage:  python main.py <command>

Commands:
  scrape    Scrape RSS feeds and save articles to DB
  digest    Build HTML digest (saved to outputs/ folder)
  schedule  Start the daily scheduler (runs at configured time)
  export    Export all articles to CSV
  stats     Show database statistics
"""

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(HELP)
        sys.exit(0)

    COMMANDS[sys.argv[1]]()
