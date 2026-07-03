import json
import os
import logging
import threading
import pandas as pd
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from config import RETRAIN_HOUR, RETRAIN_LOG_PATH
from utils.news_fetcher import fetch_news_accidents
from utils.hotspot_engine import build_hotspots, _load_ds1
from utils.risk_model import train_model

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [AutoRetrain] %(message)s")
log = logging.getLogger("auto_retrain")

_scheduler = None
_lock      = threading.Lock()   # prevent concurrent retrains


def _retrain_job():
    """Core job: fetch news → merge → retrain model → rebuild hotspots."""
    with _lock:
        log.info("Auto-retrain started.")
        try:
            # 1. Fetch fresh news
            log.info("Fetching accident news...")
            news_rows = fetch_news_accidents(days_back=30)
            log.info(f"Fetched {len(news_rows)} news-derived accident records.")

            if not news_rows:
                log.info("No new news records — skipping retrain.")
                _write_log("skipped", 0, 0, "No new news records")
                return

            # 2. Merge with base dataset
            base_df  = _load_ds1()
            news_df  = pd.DataFrame(news_rows)
            merged   = pd.concat([base_df, news_df], ignore_index=True)
            log.info(f"Total training records: {len(merged)}")

            # 3. Retrain model
            clf, acc = train_model(merged)
            log.info(f"Model retrained. Accuracy: {acc*100:.1f}%")

            # 4. Rebuild hotspots
            hotspots = build_hotspots()
            log.info(f"Hotspots rebuilt: {len(hotspots)} clusters")

            # 5. Log result
            _write_log("success", len(news_rows), round(acc * 100, 1),
                       f"{len(hotspots)} hotspot clusters")

        except Exception as e:
            log.error(f"Auto-retrain failed: {e}")
            _write_log("failed", 0, 0, str(e))


def _write_log(status: str, new_records: int, accuracy: float, note: str):
    os.makedirs("sample_data", exist_ok=True)
    history = []
    if os.path.exists(RETRAIN_LOG_PATH):
        with open(RETRAIN_LOG_PATH) as f:
            history = json.load(f)
    history.append({
        "timestamp":   datetime.now().isoformat(),
        "status":      status,
        "new_records": new_records,
        "accuracy":    accuracy,
        "note":        note,
    })
    # keep last 30 entries
    history = history[-30:]
    with open(RETRAIN_LOG_PATH, "w") as f:
        json.dump(history, f, indent=2)


def get_retrain_log() -> list:
    if os.path.exists(RETRAIN_LOG_PATH):
        with open(RETRAIN_LOG_PATH) as f:
            return json.load(f)
    return []


def start_scheduler():
    """Start background scheduler — call once at app startup."""
    global _scheduler
    if _scheduler is not None and _scheduler.running:
        return  # already running

    _scheduler = BackgroundScheduler(daemon=True)

    # Daily at RETRAIN_HOUR (default 2 AM)
    _scheduler.add_job(
        _retrain_job,
        trigger=CronTrigger(hour=RETRAIN_HOUR, minute=0),
        id="daily_retrain",
        replace_existing=True,
    )

    _scheduler.start()
    log.info(f"Scheduler started. Next retrain at {RETRAIN_HOUR:02d}:00 daily.")


def run_retrain_now():
    """Trigger an immediate retrain (called on first app boot if model is stale)."""
    t = threading.Thread(target=_retrain_job, daemon=True)
    t.start()
