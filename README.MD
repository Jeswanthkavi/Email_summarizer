# AI Email Summarizer Agent

An automated Python agent that fetches incoming emails from Gmail, stores them in MySQL, analyzes and classifies them with the Google Gemini API (`google-genai`), and delivers prioritized email digests to Telegram on a scheduled basis.

---

## Key Features

- **Gmail Ingestion & Deduplication:** Fetches latest `INBOX` emails via the Gmail API (`gmail.readonly` scope), parses plain-text and HTML bodies (`BeautifulSoup` + `lxml`), and prevents duplicates using unique `gmail_message_id` records.
- **AI Email Analysis (Google Gemini):** Summarizes each unprocessed email, classifies it into a category (`Work`, `Education`, `Finance`, `Personal`, `Meeting`, `Shopping`, `Travel`, `Security`, `Promotion`, `Newsletter`, `Social`, `Other`), assigns priority (`High`, `Medium`, `Low`), and extracts required actions in structured JSON.
- **Resilient Model Fallback & Retry:** Uses `GEMINI_MODEL` with automatic fallback across `gemini-3.5-flash`, `gemini-3.1-flash-lite`, and `gemini-2.5-flash-lite`, a 30-second HTTP timeout, and `tenacity` retries on transient rate limits/timeouts.
- **Transactional MySQL Persistence:** Stores emails and AI analyses in MySQL 8.0 via SQLAlchemy 2.0 (`pymysql`), committing analysis results and `processed = True` atomically.
- **Prioritized Telegram Digest:** Groups unsent processed emails into High, Medium, and Low priority sections, automatically splits messages exceeding Telegram's 4096-character limit, and marks `digest_sent = True` **only after** successful Telegram delivery.
- **Scheduled Execution (IST):** Runs automatically via APScheduler at **09:00, 13:00, 17:00, and 22:00 (`Asia/Kolkata`)** with overlap locking and an OS-level process lock (`logs/scheduler.lock`) to prevent duplicate scheduler instances.

---

## Tech Stack

- **Language:** Python 3.12
- **Email:** Google Gmail API (`google-api-python-client`, `google-auth`, `google-auth-oauthlib`, `google-auth-httplib2`)
- **HTML Parsing:** `beautifulsoup4`, `lxml`
- **AI SDK:** `google-genai`
- **Database:** MySQL 8.0, `SQLAlchemy>=2.0,<2.1`, `pymysql`
- **Notifications:** Telegram Bot API (`requests`)
- **Scheduling:** `APScheduler` (`BlockingScheduler` + `CronTrigger`)
- **Configuration, Logging & Retries:** `python-dotenv`, `loguru`, `tenacity`

---

## Project Structure

```text
Em/
├── app/
│   ├── ai/
│   │   ├── gemini_client.py         # Gemini client, prompt builder, model fallback & JSON parsing
│   │   ├── list_models.py           # Lists available generateContent models for your API key
│   │   ├── test_gemini.py           # Basic Gemini text generation check
│   │   └── test_email_analysis.py   # Tests Gemini analysis on an unprocessed DB email
│   ├── config/
│   │   └── settings.py              # Loads .env config, DB URL, paths, and timezone
│   ├── database/
│   │   ├── connection.py            # SQLAlchemy engine, SessionLocal, and Base
│   │   ├── models.py                # Email and EmailAnalysis ORM models
│   │   └── repository.py            # CRUD helpers, duplicate prevention, digest state updates
│   ├── gmail/
│   │   ├── auth.py                  # OAuth2 login, token loading, and automatic refresh
│   │   ├── gmail_client.py          # Authenticated Gmail v1 service builder
│   │   ├── email_fetcher.py         # Message fetching, MIME/HTML decoding, header extraction
│   │   └── test_gmail.py            # Standalone Gmail fetch verification script
│   ├── scheduler/
│   │   ├── jobs.py                  # Overlap-locked scheduled pipeline wrapper
│   │   └── scheduler.py             # APScheduler setup (Asia/Kolkata) & single-instance lock
│   ├── services/
│   │   ├── email_service.py         # Fetches Gmail messages and persists unique emails
│   │   ├── analysis_service.py      # Analyzes unprocessed emails and commits results atomically
│   │   ├── digest_service.py        # Formats High/Medium/Low priority Telegram digest
│   │   ├── notification_service.py  # Sends digest and marks digest_sent=True on success
│   │   ├── test_email_service.py    # Gmail -> MySQL ingestion test
│   │   ├── test_analysis_service.py # Unprocessed emails -> Gemini -> MySQL test
│   │   └── test_notification_service.py # Digest -> Telegram test
│   ├── telegram/
│   │   ├── telegram_client.py       # Telegram Bot API client with 4096-char message chunking
│   │   ├── test_telegram.py         # Fetches getUpdates to inspect chat IDs
│   │   └── send_test_message.py     # Sends a safe connectivity test message
│   ├── utils/
│   │   └── logger.py                # Loguru console + rotating file logger (logs/application.log)
│   └── main.py                      # Main pipeline & scheduler CLI entry point
├── credentials/                     # Git-ignored Gmail OAuth files (gmail_credentials.json, gmail_token.json)
├── logs/                            # Git-ignored application logs and scheduler.lock
├── tests/                           # Placeholder directory for unit test modules
├── .env                             # Git-ignored runtime configuration
├── .gitignore
├── requirements.txt
└── run.py                           # Initializes MySQL tables (emails, email_analysis)
```

---

## Pipeline Workflow

1. **Fetch & Store (`email_service.fetch_and_save_emails`):** Connects to Gmail, retrieves latest `INBOX` messages, checks `gmail_message_id` uniqueness, maps `date` to `received_at`, safely truncates long text for MySQL `TEXT`, and inserts new rows into `emails`.
2. **Analyze (`analysis_service.process_unprocessed_emails`):** Queries `emails` where `processed = False`, sends email metadata/body to Gemini, and atomically saves the `email_analysis` row and sets `processed = True`. Failed Gemini requests roll back and leave `processed = False` for retry on the next run.
3. **Digest & Notify (`notification_service.send_email_digest`):** Queries processed rows where `digest_sent = False`, builds a priority-grouped digest (`digest_service.generate_email_digest`), sends it to Telegram (splitting at 4096 chars if needed), and marks `digest_sent = True` only after Telegram returns success.

---

## Database Schema

Initialized via `run.py` using SQLAlchemy `Base.metadata.create_all`:

### `emails`
| Column | Type | Constraints / Notes |
|---|---|---|
| `id` | `INTEGER` | Primary key, auto-increment |
| `gmail_message_id` | `VARCHAR(255)` | Unique, indexed, not null |
| `thread_id` | `VARCHAR(255)` | Nullable |
| `sender` | `TEXT` | Nullable |
| `subject` | `TEXT` | Nullable |
| `received_at` | `VARCHAR(255)` | Nullable |
| `body` | `TEXT` | Nullable |
| `processed` | `TINYINT` (`Boolean`) | Not null, default `False` |
| `digest_sent` | `TINYINT` (`Boolean`) | Not null, default `False` |
| `created_at` | `DATETIME` | Not null, UTC timestamp |

### `email_analysis`
| Column | Type | Constraints / Notes |
|---|---|---|
| `id` | `INTEGER` | Primary key, auto-increment |
| `email_id` | `INTEGER` | Unique FK -> `emails.id` (`ON DELETE CASCADE`) |
| `summary` | `TEXT` | Nullable |
| `category` | `VARCHAR(100)` | Nullable |
| `priority` | `VARCHAR(50)` | Nullable |
| `action_required` | `TEXT` | Nullable |
| `analyzed_at` | `DATETIME` | Not null, UTC timestamp |

---

## Setup Instructions (Windows 11 / PowerShell)

### 1. Create & Activate Virtual Environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install dependencies (use `python -m pip` if Windows Application Control blocks standalone `pip.exe`):

```powershell
cd Em
..\venv\Scripts\python.exe -m pip install --upgrade pip
..\venv\Scripts\python.exe -m pip install -r requirements.txt
```

> **Note:** `requirements.txt` pins `SQLAlchemy>=2.0,<2.1` for Windows Application Control compatibility.

### 2. Configure Environment Variables

Create `Em/.env` with your credentials and settings (never commit this file):

```ini
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3.5-flash

GMAIL_CREDENTIALS_FILE=credentials/gmail_credentials.json
GMAIL_TOKEN_FILE=credentials/gmail_token.json

TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id

DB_HOST=localhost
DB_PORT=3306
DB_NAME=ai_email_agent
DB_USER=ai_agent_user
DB_PASSWORD=your_mysql_password
DATABASE_URL=mysql+pymysql://ai_agent_user:your_mysql_password@localhost:3306/ai_email_agent

TIMEZONE=Asia/Kolkata
```

If `DATABASE_URL` is omitted, `app/config/settings.py` constructs it automatically from `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, and `DB_PASSWORD` (URL-encoding special characters).

### 3. Configure MySQL Database

Ensure the `MySQL80` Windows service is running, and create the database and user:

```sql
CREATE DATABASE IF NOT EXISTS ai_email_agent CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'ai_agent_user'@'localhost' IDENTIFIED BY 'your_mysql_password';
GRANT ALL PRIVILEGES ON ai_email_agent.* TO 'ai_agent_user'@'localhost';
FLUSH PRIVILEGES;
```

Initialize the tables from inside `Em\`:

```powershell
..\venv\Scripts\python.exe run.py
```

### 4. Configure Gmail OAuth

1. In Google Cloud Console, enable the **Gmail API** and create an **OAuth 2.0 Client ID** (`Desktop app`).
2. Download the JSON file and save it as `Em/credentials/gmail_credentials.json`.
3. Run the Gmail test script once to complete browser consent and generate `Em/credentials/gmail_token.json`:

```powershell
..\venv\Scripts\python.exe -m app.gmail.test_gmail
```

### 5. Configure Telegram Bot

1. Create a bot with `@BotFather` to get `TELEGRAM_BOT_TOKEN`.
2. Open your bot in Telegram and click **Start**.
3. Run `..\venv\Scripts\python.exe -m app.telegram.test_telegram` to retrieve your `TELEGRAM_CHAT_ID`, add it to `Em/.env`, and verify delivery with:

```powershell
..\venv\Scripts\python.exe -m app.telegram.send_test_message
```

---

## Running the Application

Run all commands from inside the `Em/` directory:

### Single Pipeline Run

```powershell
..\venv\Scripts\python.exe -m app.main --once --max-results 10
```

### Automated Scheduled Mode (09:00, 13:00, 17:00, 22:00 IST)

```powershell
..\venv\Scripts\python.exe -m app.main
```

- Uses `Asia/Kolkata` timezone (`TIMEZONE` in `.env`).
- Acquires `Em/logs/scheduler.lock` so a second scheduler process cannot start accidentally.
- Logs progress to both the console and `Em/logs/application.log` (10 MB rotation, 30-day retention).

---

## Verification & Utility Scripts

Run from inside `Em/`:

| Command | Purpose |
|---|---|
| `..\venv\Scripts\python.exe -m app.gmail.test_gmail` | Verify Gmail OAuth & fetch latest 5 emails |
| `..\venv\Scripts\python.exe -m app.ai.list_models` | List available Gemini models for your API key |
| `..\venv\Scripts\python.exe -m app.ai.test_gemini` | Test Gemini text generation |
| `..\venv\Scripts\python.exe -m app.ai.test_email_analysis` | Test Gemini analysis on an unprocessed DB email |
| `..\venv\Scripts\python.exe -m app.telegram.test_telegram` | Inspect recent bot updates (`getUpdates`) |
| `..\venv\Scripts\python.exe -m app.telegram.send_test_message` | Send a connectivity test message to Telegram |
| `..\venv\Scripts\python.exe -m app.services.test_email_service` | Test Gmail -> MySQL ingestion |
| `..\venv\Scripts\python.exe -m app.services.test_analysis_service` | Test MySQL -> Gemini -> MySQL analysis |
| `..\venv\Scripts\python.exe -m app.services.test_notification_service` | Test digest formatting & Telegram delivery |

---

## Security Notes

- `.gitignore` excludes `.env`, `venv/`, `__pycache__/`, `*.pyc`, `logs/`, `*.log`, `credentials/*.json`, `credentials.json`, `token.json`, `gmail_credentials.json`, and `gmail_token.json`.
- Never commit `.env` or files inside `credentials/` to version control.
