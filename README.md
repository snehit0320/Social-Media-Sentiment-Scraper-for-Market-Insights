# Social Signal Scraper

A stealthy pipeline for collecting public Twitter/X posts from selected accounts and saving them for downstream sentiment/NLP analysis. Built for research workflows where you want to correlate social signals with market movement.



## 📋 Project Overview

This tool automates the collection of targeted Twitter posts:
- **Focus**: Economic entities (e.g., central banks, news outlets) for market sentiment tracking.
- **Core Workflow**: Secure login → Dynamic scraping → Data parsing → Persistent storage.
- **Use Case**: Feed into NLP models to predict stock movements based on public discourse.

Key innovations:
- **Anti-Ban Measures**: Human-like interactions (variable pauses, mouse/scroll patterns) to mimic real users.
- **Hybrid Approach**: Browser automation for auth/scraping, with optional GraphQL for efficiency.
- **Scalability**: Cloud-ready; tested on AWS for multi-account parallel processing.

> **Note**: This is for educational/research purposes. Respect platform ToS and data privacy laws.

---

## ✨ Features

- **Secure Authentication**: Playwright handles login with proxy support and fingerprint randomization.
- **Advanced Data Extraction**: Selenium scrolls profiles/searches; BeautifulSoup parses clean tweet metadata (text, author, time, likes/replies/reposts/views, engagement ratio).
- **Date-Range Filtering**: Customizable SINCE/UNTIL for precise historical pulls.
- **Storage Options**: MongoDB (with deduplication) or SQLite for flexible data management.
- **Proxy Integration**: Bright Data support for IP rotation and geo-spoofing.
- **Human Simulation**: Randomized behaviors (e.g., exponential delays, curved mouse paths) to evade detection.
- **Configurable Limits**: Max posts per account; multi-target support.

---

## 🛠 Tech Stack

| Component     | Tools/Libraries                  |
|---------------|----------------------------------|
| Automation   | Playwright, Selenium             |
| Parsing      | BeautifulSoup                    |
| Storage      | MongoDB (PyMongo), SQLite        |
| Anti-Detection | Undetected-Chromedriver, Fake-Useragent |
| Utils        | Requests, Asyncio, Logging       |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Install deps: `pip install -r requirements.txt` (create from: playwright selenium beautifulsoup4 pymongo sqlite3 requests fake-useragent undetected-chromedriver)
- Update credentials in scripts (TWITTER_USERNAME, TWITTER_PASSWORD, proxies if enabled).
- MongoDB (local/Atlas) or SQLite setup.

### Installation
```bash
git clone https://github.com/snehit0320/summa.git
cd summa
pip install -r requirements.txt
playwright install  # For browser binaries
```
