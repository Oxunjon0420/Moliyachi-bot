"""
Utility helpers used across the bot.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional


def format_amount(amount: float) -> str:
    """Format a float amount with thousand separators."""
    return f"{amount:,.0f} so'm"


def parse_amount(text: str) -> Optional[float]:
    """
    Parse an amount string entered by the user.
    Accepts: '15000', '15 000', '15,000', '15.5'
    Returns None if invalid.
    """
    cleaned = text.replace(" ", "").replace(",", "").strip()
    try:
        value = float(cleaned)
        if value <= 0:
            return None
        return value
    except ValueError:
        return None


def day_range(date: Optional[datetime] = None) -> tuple[datetime, datetime]:
    """Return (start_of_day, end_of_day) for a given date (default today)."""
    if date is None:
        date = datetime.now()
    start = date.replace(hour=0, minute=0, second=0, microsecond=0)
    end = date.replace(hour=23, minute=59, second=59, microsecond=999999)
    return start, end


def week_range() -> tuple[datetime, datetime]:
    """Return (start_of_week, now) — Monday to today."""
    now = datetime.now()
    start = now - timedelta(days=now.weekday())
    start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    return start, now


def month_range() -> tuple[datetime, datetime]:
    """Return (first_of_month, now)."""
    now = datetime.now()
    start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return start, now


def progress_bar(value: float, total: float, length: int = 10) -> str:
    """Generate a simple ASCII progress bar."""
    if total == 0:
        ratio = 0.0
    else:
        ratio = min(value / total, 1.0)
    filled = int(ratio * length)
    bar = "█" * filled + "░" * (length - filled)
    return f"[{bar}] {ratio * 100:.0f}%"


def truncate(text: str, max_len: int = 30) -> str:
    """Truncate a string and add ellipsis if too long."""
    return text if len(text) <= max_len else text[: max_len - 1] + "…"
