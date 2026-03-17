# 💼 Finance Tracker Bot

> A smart Telegram bot to track your income, expenses, and financial habits.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![aiogram](https://img.shields.io/badge/aiogram-3.7-green.svg)](https://aiogram.dev)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-orange.svg)](https://sqlalchemy.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📖 Description

**Finance Tracker Bot** is a production-ready Telegram bot for personal finance management. Built with clean architecture, async Python, and FSM-driven conversation flows, it supports multiple users out of the box and stores all data in SQLite (easily swappable to PostgreSQL).

---

## ✨ Features

| Feature | Description |
|---|---|
| ➕ Add Expense | Step-by-step flow: amount → category → description |
| 💰 Add Income | Same guided flow for income |
| 🏷️ Categories | 8 expense + 6 income categories |
| 💳 Balance | Total income / expense / net balance |
| 📅 Daily Report | Today's transactions summary |
| 📆 Weekly Report | This week's financial overview |
| 🗓️ Monthly Report | Full month with category breakdown + progress bars |
| 📈 Category Stats | All-time breakdown per category |
| ✏️ Edit Records | Change amount, category, or description |
| 🗑️ Delete Records | Confirm-before-delete safety flow |
| 👥 Multi-user | Each Telegram user has isolated data |

---

## 🛠️ Tech Stack

- **Python 3.11+**
- **aiogram 3.7** — async Telegram Bot framework
- **SQLAlchemy 2.0** — async ORM
- **aiosqlite** — async SQLite driver
- **python-dotenv** — environment config
- **alembic** — database migrations

---

## 📁 Project Structure

```
finance_bot/
├── app.py                  # Entry point
├── config/
│   ├── config.py           # Settings from .env
│   └── logging.py          # Logging setup
├── database/
│   ├── db.py               # Engine & session factory
│   ├── models.py           # SQLAlchemy ORM models
│   └── crud.py             # Raw DB operations
├── handlers/
│   ├── start.py            # /start, /help
│   ├── expense.py          # Add expense FSM
│   ├── income.py           # Add income FSM
│   ├── report.py           # Reports & balance
│   └── settings.py        # Edit, delete, settings
├── keyboards/
│   ├── reply.py            # ReplyKeyboard builders
│   └── inline.py           # InlineKeyboard builders
├── states/
│   └── finance_states.py   # FSM state groups
├── services/
│   ├── finance_service.py  # Business logic
│   └── analytics_service.py# Report generation
├── utils/
│   └── helpers.py          # Formatting & date helpers
├── .env.example
├── requirements.txt
└── README.md
```

---

## 🚀 Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/finance-tracker-bot.git
cd finance-tracker-bot/finance_bot
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and set your bot token:

```env
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrSTUvwxYZ
DATABASE_URL=sqlite+aiosqlite:///./finance_bot.db
LOG_LEVEL=INFO
```

> 🔑 Get your bot token from [@BotFather](https://t.me/BotFather) on Telegram.

### 5. Run the bot

```bash
python app.py
```

---

## 🤖 Bot Commands

| Command | Description |
|---|---|
| `/start` | Start the bot and register |
| `/balance` | Quick balance check |
| `/report` | Open reports menu |
| `/help` | Show help message |

---

## 🗄️ Database Models

### User
| Column | Type | Description |
|---|---|---|
| id | Integer PK | Internal ID |
| telegram_id | BigInteger | Telegram user ID (unique) |
| username | String | Telegram @username |
| full_name | String | Display name |
| created_at | DateTime | Registration time |

### Transaction
| Column | Type | Description |
|---|---|---|
| id | Integer PK | Transaction ID |
| user_id | FK → User | Owner |
| amount | Float | Transaction amount |
| type | Enum | `income` or `expense` |
| category | String | Category label |
| description | String | Optional note |
| created_at | DateTime | Timestamp |

---

## 🎨 Bot Branding

- **Name:** Finance Tracker Bot
- **Username:** @finance_tracker_bot
- **Bio:** A smart Telegram bot to track your income, expenses, and financial habits.

### Profile Image Concept
Minimal, modern design: dark navy background (`#0D1B2A`), centered white wallet or chart icon, subtle green accent (`#00C896`). Clean sans-serif typography.

### Color Palette
| Color | Hex | Usage |
|---|---|---|
| Navy | `#0D1B2A` | Background |
| Mint Green | `#00C896` | Income / positive |
| Coral Red | `#FF4757` | Expense / negative |
| Light Grey | `#F1F2F6` | Neutral text |
| Gold | `#FFA502` | Highlights |

---

## 🔄 Switching to PostgreSQL

1. Install driver: `pip install asyncpg`
2. Update `.env`:
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost/finance_db
```
3. Run `alembic upgrade head` to apply migrations.

---

## 📄 License

MIT License — feel free to use and modify.
