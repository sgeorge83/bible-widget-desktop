"""Fetch and cache the daily verse from the WordOnAir backend."""

from __future__ import annotations

import json
import time
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

API_URL = "https://bible-widget-backend.vercel.app/api/morning"
DUBAI = timezone(timedelta(hours=4))
CACHE_FILE = Path.home() / ".bible-widget-desktop" / "verse-cache.json"


def dubai_key(dt: datetime | None = None) -> str:
    stamp = (dt or datetime.now(timezone.utc)).astimezone(DUBAI)
    return stamp.strftime("%Y-%m-%d")


def clean_verse_text(raw: str, reference: str) -> str:
    text = (raw or "").strip()
    if "\n" not in text:
        return text or raw or ""
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    if lines and lines[0].lower() == (reference or "").lower():
        return "\n\n".join(lines[1:])
    return text or raw or ""


def load_cache() -> dict:
    if not CACHE_FILE.exists():
        return {}
    try:
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def save_cache(cache: dict) -> None:
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache), encoding="utf-8")


def cached_verse() -> dict | None:
    cache = load_cache()
    return cache.get(dubai_key()) or cache.get("lastVerse")


def fetch_verse() -> dict:
    request = urllib.request.Request(
        API_URL,
        headers={"Accept": "application/json", "User-Agent": "BibleWidgetDesktop/1.0"},
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        payload = json.loads(response.read().decode("utf-8"))

    reference = (payload.get("reference") or "Daily Verse").strip()
    generated = payload.get("generated_at")
    key = dubai_key()
    if generated:
        try:
            parsed = datetime.fromisoformat(str(generated).replace("Z", "+00:00"))
            key = dubai_key(parsed)
        except ValueError:
            pass

    verse = {
        "text": clean_verse_text(payload.get("esv_text") or "", reference),
        "reference": reference,
        "meaning": (payload.get("simple_meaning") or "").strip(),
        "message": (payload.get("message") or "").strip(),
        "generated_at": generated,
    }
    cache = load_cache()
    cache[key] = verse
    cache["lastVerse"] = verse
    cache["fetched_at"] = time.time()
    save_cache(cache)
    return verse


def ms_until_dubai_930() -> int:
    now = datetime.now(DUBAI)
    target = now.replace(hour=9, minute=30, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)
    return int((target - now).total_seconds() * 1000)
