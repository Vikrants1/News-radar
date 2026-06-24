# 📰 NewsRadar — Automated News Scraper & Daily Digest Bot

A Python automation bot that scrapes headlines from multiple RSS feeds, filters by your keywords,
stores articles in SQLite, and emails you a daily HTML digest — all on autopilot.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen)
![Scheduler](https://img.shields.io/badge/Scheduler-APScheduler-orange)

---

## 📁 Project Structure

```
NewsRadar/
├── src/
│   ├── scraper/        # RSS feed parser & keyword filter
│   ├── database/       # SQLite ORM-style handler
│   ├── notifier/       # HTML email digest builder & sender
│   └── scheduler/      # APScheduler daily job runner
├── config/
│   └── config.json     # Keywords, feeds, email settings
├── tests/              # pytest unit tests
├── outputs/            # Exported digests (HTML/CSV)
├── main.py             # CLI entry point
└── requirements.txt
```

---

## 🚀 Quickstart

```bash
# 1. Clone & install
git clone https://github.com/YOUR_USERNAME/NewsRadar.git
cd NewsRadar
pip install -r requirements.txt

# 2. Configure your keywords and email
nano config/config.json

# 3. Scrape news now
python main.py scrape

# 4. Send digest email now
python main.py digest

# 5. Start the daily scheduler (runs at 8:00 AM every day)
python main.py schedule

# 6. Export saved articles to CSV
python main.py export

# Run tests
pytest tests/ -v
```

---

## ⚙️ Configuration (`config/config.json`)

```json
{
  "keywords": ["AI", "Python", "startup", "technology"],
  "feeds": [
    "http://feeds.bbci.co.uk/news/technology/rss.xml",
    "https://techcrunch.com/feed/"
  ],
  "email": {
    "sender": "your@gmail.com",
    "password": "your_app_password",
    "recipients": ["you@email.com"],
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587
  },
  "schedule_time": "08:00",
  "max_articles_per_digest": 20
}
```

> ⚠️ For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833), not your real password.

---

## 🧠 How It Works

```
RSS Feeds → Scraper → Keyword Filter → SQLite DB → Email Digest
                                                  → CSV Export
```

1. **Scraper** fetches XML from RSS feeds and parses `<title>`, `<link>`, `<pubDate>`, `<description>`
2. **Database** stores articles with duplicate detection via URL hash
3. **Notifier** builds a styled HTML email and sends via SMTP
4. **Scheduler** runs the full pipeline at a configured time every day

---

## 📌 Resume Bullet Points

- Built a Python automation bot that scrapes 5+ RSS feeds, filters articles by keyword using regex, and stores results in SQLite with deduplication via URL hashing
- Engineered an HTML email digest generator that sends formatted daily newsletters via SMTP with APScheduler for cron-style automation
- Achieved 90%+ test coverage with pytest; CLI supports scrape, digest, export, and schedule commands

---

## 📄 License
MIT
