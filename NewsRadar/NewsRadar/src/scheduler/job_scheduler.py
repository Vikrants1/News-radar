"""
src/scheduler/job_scheduler.py
--------------------------------
Schedules daily scrape + digest job using APScheduler.

Run: python main.py schedule
"""

import logging
from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)


class JobScheduler:

    def __init__(self, scrape_fn, digest_fn, schedule_time: str = "08:00"):
        """
        Args:
            scrape_fn:     callable — runs the scraper + saves to DB
            digest_fn:     callable — sends the email digest
            schedule_time: "HH:MM" string (24h format)
        """
        self.scrape_fn     = scrape_fn
        self.digest_fn     = digest_fn
        self.schedule_time = schedule_time
        self.scheduler     = BlockingScheduler(timezone="Asia/Kolkata")

    def start(self):
        """Register jobs and start the blocking scheduler."""
        hour, minute = map(int, self.schedule_time.split(":"))

        self.scheduler.add_job(
            func=self._daily_job,
            trigger=CronTrigger(hour=hour, minute=minute),
            id="daily_newsradar",
            name="NewsRadar Daily Digest",
            replace_existing=True,
            misfire_grace_time=300,
        )

        next_run = self.scheduler.get_job("daily_newsradar").next_run_time
        print(f"\n  ⏰ Scheduler started.")
        print(f"  📅 Daily job scheduled at {self.schedule_time} IST")
        print(f"  ⏭  Next run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Press Ctrl+C to stop.\n")

        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            print("\n  Scheduler stopped.")

    def _daily_job(self):
        logger.info(f"[{datetime.now()}] Starting daily NewsRadar job...")
        try:
            saved, dupes = self.scrape_fn()
            logger.info(f"Scrape done: {saved} new, {dupes} duplicates")
            self.digest_fn()
            logger.info("Digest sent.")
        except Exception as e:
            logger.error(f"Daily job failed: {e}", exc_info=True)

    def run_once(self):
        """Run the job immediately once (useful for testing)."""
        print("  Running job once immediately...")
        self._daily_job()
