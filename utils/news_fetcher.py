import requests
import json
import os
import re
import random
from datetime import datetime, timedelta
from config import NEWSAPI_KEY, CITIES, CITY_COORDS, NEWS_CACHE_PATH

SEVERITY_KEYWORDS = {
    "fatal":  ["died", "killed", "dead", "death", "fatality", "fatal"],
    "major":  ["serious", "critical", "severe", "grievous", "injured badly"],
    "minor":  ["minor", "injured", "hurt", "accident", "crash", "collision"],
}

WEATHER_KEYWORDS = {
    "fog":  ["fog", "foggy", "mist", "visibility", "haze"],
    "rain": ["rain", "wet", "slippery", "monsoon", "flood", "waterlogged"],
    "clear": [],
}

CAUSE_KEYWORDS = {
    "drunk driving": ["drunk", "alcohol", "intoxicated", "inebriated", "drunken"],
    "overspeeding":  ["speed", "overspeeding", "rash", "fast", "racing"],
    "poor road":     ["pothole", "crater", "road condition", "bad road", "damaged road"],
    "weather":       ["fog", "rain", "wet road", "slippery", "visibility"],
    "distraction":   ["distracted", "phone", "negligence", "unaware"],
}

ROAD_KEYWORDS = {
    "highway":  ["highway", "nh", "national highway", "expressway", "bypass"],
    "urban":    ["junction", "signal", "intersection", "city", "road"],
    "rural":    ["village", "rural", "outskirts"],
}


def _extract_severity(text: str) -> str:
    text_lower = text.lower()
    for sev, keywords in SEVERITY_KEYWORDS.items():
        if any(k in text_lower for k in keywords):
            return sev
    return "minor"


def _extract_weather(text: str) -> str:
    text_lower = text.lower()
    for weather, keywords in WEATHER_KEYWORDS.items():
        if keywords and any(k in text_lower for k in keywords):
            return weather
    return "clear"


def _extract_cause(text: str) -> str:
    text_lower = text.lower()
    for cause, keywords in CAUSE_KEYWORDS.items():
        if any(k in text_lower for k in keywords):
            return cause
    return "distraction"


def _extract_road_type(text: str) -> str:
    text_lower = text.lower()
    for road, keywords in ROAD_KEYWORDS.items():
        if any(k in text_lower for k in keywords):
            return road
    return "urban"


def _extract_vehicles(text: str) -> int:
    matches = re.findall(r'(\d+)\s*vehicle', text.lower())
    if matches:
        return min(int(matches[0]), 6)
    if any(w in text.lower() for w in ["truck", "lorry", "bus"]):
        return 3
    return 2


def _jitter_coords(lat: float, lon: float, radius_deg: float = 0.05) -> tuple:
    """Add small random offset to city centre coords for variety."""
    return (
        lat + random.uniform(-radius_deg, radius_deg),
        lon + random.uniform(-radius_deg, radius_deg),
    )


def fetch_news_accidents(days_back: int = 30) -> list:
    """
    Fetch accident news for all cities, extract structured rows.
    Returns list of dicts compatible with DS1 schema.
    """
    from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    rows = []
    seen_titles = set()

    for city in CITIES:
        city_lat, city_lon = CITY_COORDS[city]
        try:
            r = requests.get(
                "https://newsapi.org/v2/everything",
                params={
                    "q":        f"road accident {city}",
                    "language": "en",
                    "from":     from_date,
                    "pageSize": 20,
                    "sortBy":   "publishedAt",
                    "apiKey":   NEWSAPI_KEY,
                },
                timeout=10,
            )
            data = r.json()
            if data.get("status") != "ok":
                continue

            for article in data.get("articles", []):
                title = article.get("title") or ""
                desc  = article.get("description") or ""
                text  = f"{title} {desc}"

                # skip duplicates and non-accident articles
                if title in seen_titles:
                    continue
                if not any(w in text.lower() for w in
                           ["accident", "crash", "collision", "killed",
                            "injured", "died", "fatal"]):
                    continue
                seen_titles.add(title)

                pub_date = article.get("publishedAt", "")[:10]
                try:
                    dt = datetime.strptime(pub_date, "%Y-%m-%d")
                    hour = random.choice([7, 8, 17, 18, 20, 22, 23, 0, 1])
                    day_of_week = dt.strftime("%A")
                except Exception:
                    hour = 20
                    day_of_week = "Monday"

                severity  = _extract_severity(text)
                weather   = _extract_weather(text)
                cause     = _extract_cause(text)
                road_type = _extract_road_type(text)
                vehicles  = _extract_vehicles(text)
                sev_num   = {"minor": 1, "major": 2, "fatal": 3}[severity]
                lat, lon  = _jitter_coords(city_lat, city_lon)

                rows.append({
                    "latitude":        round(lat, 6),
                    "longitude":       round(lon, 6),
                    "severity":        sev_num,
                    "severity_raw":    severity,
                    "weather":         weather,
                    "road_type":       road_type,
                    "cause":           cause,
                    "casualties":      1 if sev_num >= 2 else 0,
                    "vehicles_involved": vehicles,
                    "hour":            hour,
                    "day_of_week":     day_of_week,
                    "risk_score":      round(sev_num / 3.0, 3),
                    "traffic_density": "high" if hour in range(7, 10) or hour in range(17, 20) else "medium",
                    "visibility":      "low" if weather in ("fog", "rain") else "high",
                    "is_peak_hour":    1 if hour in range(7, 10) or hour in range(17, 20) else 0,
                    "alcohol":         1 if cause == "drunk driving" else 0,
                    "location_type":   "Straight Road",
                    "vehicle_type":    "Car",
                    "source":          "news",
                    "news_title":      title[:120],
                    "city":            city,
                })

        except Exception as e:
            print(f"[news_fetcher] Error fetching {city}: {e}")
            continue

    # cache to disk
    os.makedirs("sample_data", exist_ok=True)
    with open(NEWS_CACHE_PATH, "w") as f:
        json.dump({
            "fetched_at": datetime.now().isoformat(),
            "count":      len(rows),
            "rows":       rows,
        }, f, indent=2)

    return rows


def load_cached_news() -> list:
    if os.path.exists(NEWS_CACHE_PATH):
        with open(NEWS_CACHE_PATH) as f:
            return json.load(f).get("rows", [])
    return []
