[README.md](https://github.com/user-attachments/files/29283895/README.md)
# 📰 NewsRadar — Automated News Scraper & Daily Digest Bot

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)
![Tests](https://img.shields.io/badge/Tests-25%2B%20Passing-22c55e?style=for-the-badge)
![Scheduler](https://img.shields.io/badge/Scheduler-APScheduler-f97316?style=for-the-badge)

**A Python automation bot that scrapes RSS feeds, filters news by your keywords,
stores articles in SQLite, and emails you a beautiful HTML digest — every day, on autopilot.**

[Features](#-features) • [Quickstart](#-quickstart) • [Configuration](#-configuration) • [CLI Commands](#-cli-commands) • [Project Structure](#-project-structure) • [Tests](#-tests)

</div>

---

## ✨ Features

- 🔍 **Multi-feed RSS Scraper** — fetches headlines from BBC, TechCrunch, Reuters, Hacker News, and more
- 🎯 **Keyword Filtering** — regex-powered filtering saves only articles matching your interests
- 🗄️ **SQLite Storage** — lightweight local database with SHA-256 URL hashing for deduplication
- 📧 **HTML Email Digest** — styled, responsive email digest sent via SMTP (Gmail-ready)
- ⏰ **Daily Scheduler** — APScheduler runs the full pipeline automatically at your chosen time
- 📤 **CSV Export** — export all saved articles to CSV anytime
- 🖥️ **Clean CLI** — 5 commands to scrape, digest, schedule, export, and check stats

---

## 🚀 Quickstart

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/NewsRadar.git
cd NewsRadar
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure your settings
```bash
nano config/config.json
```

### 4. Run it!
```bash
# Scrape news now
python main.py scrape

# Preview digest (saves HTML to outputs/)
python main.py digest

# Start the daily scheduler
python main.py schedule
```

---

## ⚙️ Configuration

Edit `config/config.json` to personalise NewsRadar:

```json
{
  "keywords": ["AI", "Python", "startup", "technology", "cybersecurity"],
  "feeds": [
    "http://feeds.bbci.co.uk/news/technology/rss.xml",
    "https://techcrunch.com/feed/",
    "https://feeds.reuters.com/reuters/technologyNews",
    "https://hnrss.org/frontpage"
  ],
  "email": {
    "sender": "your_email@gmail.com",
    "password": "your_app_password",
    "recipients": ["you@email.com"],
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587
  },
  "schedule_time": "08:00",
  "max_articles_per_digest": 20,
  "db_path": "outputs/newsradar.db",
  "export_path": "outputs/articles.csv"
}
```

> **💡 Gmail Tip:** Use a [Gmail App Password](https://support.google.com/accounts/answer/185833) instead of your real password. Takes 2 minutes to set up.

---

## 🖥️ CLI Commands

| Command | Description |
|---|---|
| `python main.py scrape` | Scrape all RSS feeds and save matching articles to SQLite |
| `python main.py digest` | Build HTML digest and save to `outputs/` folder |
| `python main.py schedule` | Start the daily scheduler (runs at configured time) |
| `python main.py export` | Export all articles to CSV |
| `python main.py stats` | Show database statistics |

---

## 🧠 How It Works

```
┌─────────────┐    ┌──────────────────┐    ┌──────────────┐
│  RSS Feeds  │───▶│  Keyword Filter  │───▶│   SQLite DB  │
│ (5+ sources)│    │  (regex match)   │    │ (deduplicate)│
└─────────────┘    └──────────────────┘    └──────┬───────┘
                                                   │
                          ┌────────────────────────┤
                          ▼                        ▼
                   ┌─────────────┐       ┌──────────────────┐
                   │ Email Digest│       │   CSV Export     │
                   │ (HTML/SMTP) │       │  (outputs/*.csv) │
                   └──────┬──────┘       └──────────────────┘
                          │
                   ┌──────▼──────┐
                   │  Scheduler  │
                   │ (daily 8AM) │
                   └─────────────┘
```

**Step-by-step:**
1. **Scraper** fetches XML from each RSS feed using `feedparser` + `requests`
2. **Keyword Filter** uses compiled regex patterns for fast case-insensitive matching
3. **Database** stores each article with a SHA-256 URL hash to prevent duplicates
4. **Notifier** renders a styled HTML email and sends it via SMTP with `smtplib`
5. **Scheduler** wires everything together and triggers the pipeline daily via APScheduler

---

## 📁 Project Structure

```
NewsRadar/
├── src/
│   ├── scraper/
│   │   └── rss_scraper.py       # RSS fetcher, Article dataclass, keyword filter
│   ├── database/
│   │   └── db_handler.py        # SQLite ORM-style handler, deduplication, export
│   ├── notifier/
│   │   └── email_notifier.py    # HTML digest builder, SMTP sender
│   ├── scheduler/
│   │   └── job_scheduler.py     # APScheduler daily job runner
│   └── config_loader.py         # JSON config loader with validation
├── config/
│   └── config.json              # Keywords, feeds, email, schedule settings
├── tests/
│   └── test_newsradar.py        # 25+ pytest unit tests
├── outputs/                     # Generated digests, DB, and CSV exports
├── main.py                      # CLI entry point
├── requirements.txt
└── README.md
```

---

## 🧪 Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --tb=short
```

**Test coverage includes:**

| Module | Tests |
|---|---|
| `Article` dataclass | Hash generation, deduplication, `to_dict()` |
| `RssScraper` | Keyword matching, HTML cleaning, case-insensitivity |
| `DatabaseHandler` | Save, duplicate detection, stats, CSV export |
| `EmailNotifier` | HTML generation, dry run, empty digest handling |
| `ConfigLoader` | Valid config, missing keys, missing file |

---

## 📦 Dependencies

| Package | Purpose |
|---|---|
| `feedparser` | Parse RSS/Atom XML feeds |
| `requests` | HTTP fetching with timeout control |
| `apscheduler` | Cron-style daily job scheduling |
| `pytest` | Unit testing |

> All standard library — `sqlite3`, `smtplib`, `re`, `hashlib`, `csv` — no extra installs needed.

---

## 🗺️ Roadmap

- [ ] Telegram / Slack notification support
- [ ] Web dashboard to browse saved articles
- [ ] Sentiment analysis on headlines
- [ ] Docker support for easy deployment
- [ ] Support for more feed formats (JSON Feed, Atom)

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

```bash
# Fork → clone → create branch
git checkout -b feature/your-feature

# Make changes, add tests, then
git commit -m "feat: your feature description"
git push origin feature/your-feature
```

---

## 📄 License

MIT © [Vikrant S](https://github.com/Vikrants1)

---

<div align="center">
  <b>⭐ Star this repo if you found it useful!</b><br><br>
  Built with ❤️ using Python
</div>
