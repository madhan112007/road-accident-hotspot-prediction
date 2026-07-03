# SafeRoute AI — Road Accident Hotspot Prediction

India records over **1.5 lakh road accident deaths annually** — a crisis that is largely preventable if the right risk information reaches the driver *before* they encounter the danger. SafeRoute AI is a data-driven road safety system that uses machine learning, spatial clustering, real-time weather, and AI-generated alerts to predict accident hotspots along any route in India and warn drivers proactively.

---

## The Problem

Existing navigation tools like Google Maps flag fixed government black-spot zones — static, manually maintained, and often outdated. They don't factor in live weather, time of day, or continuously updated accident data. SafeRoute AI goes further: it learns from data, updates itself daily, and delivers risk intelligence aligned to your actual road path.

---

## How It Works — The ML Pipeline

### 1. Data Foundation
Two datasets power the system:
- `indian_roads_dataset.csv` — 20,000+ GPS-tagged accident records with features: `latitude`, `longitude`, `severity`, `weather`, `road_type`, `cause`, `casualties`, `hour`, `day_of_week`, `visibility`, `traffic_density`, `risk_score`, `is_peak_hour`
- `accident_prediction_india.csv` — a broader India-wide accident dataset with additional fields: `vehicle_type`, `alcohol_involvement`, `lighting_conditions`, `road_condition`, `speed_limit`

Both datasets are merged, cleaned, and aligned to a unified schema before training.

### 2. Risk Classification — Random Forest
A **Random Forest Classifier** (200 estimators, `max_depth=12`, `class_weight='balanced'`) is trained to predict whether a road segment is **high-risk** (severity ≥ 2, i.e. major or fatal). Input features:

| Feature | Description |
|---|---|
| `latitude`, `longitude` | GPS coordinates |
| `hour` | Time of day |
| `weather` | Encoded: clear=0, fog=1, rain=2, storm=3 |
| `road_type` | Encoded: rural → national highway |
| `traffic_density` | low / medium / high |
| `visibility` | high / medium / low |
| `is_peak_hour` | 1 if 7–10 AM or 5–8 PM |
| `vehicles_involved` | Count |
| `risk_score` | Continuous severity proxy (0–1) |

The model outputs a **probabilistic risk score (0–1)** per point, thresholded into HIGH (≥0.6) / MEDIUM (≥0.35) / LOW risk levels.

### 3. Spatial Hotspot Discovery — DBSCAN
Rather than relying on manually defined zones, **DBSCAN clustering** (Haversine metric, `eps=800m`, `min_samples=3`) is applied on historical GPS accident coordinates to automatically discover **1,126 high-density accident clusters** from the data itself — no human labeling required.

Each cluster is enriched with:
- Total accidents, fatal count, casualty count
- Dominant cause (overspeeding / drunk driving / weather / poor road / distraction)
- Peak accident hour and day
- Night accident percentage
- Average risk score → final risk level

### 4. Continuous Learning — Daily Auto-Retrain
The model is not static. Every day at **2 AM**, an APScheduler background job:
1. Fetches fresh accident news via **NewsAPI** across 8 Indian cities
2. Applies keyword-based NLP to extract `severity`, `cause`, `weather`, `road_type` from article text
3. Appends structured rows to the training dataset
4. Retrains the Random Forest on the expanded data
5. Rebuilds DBSCAN hotspot clusters
6. Logs accuracy, record count, and cluster count to `sample_data/retrain_log.json`

This keeps the system aligned with current ground reality, not just historical snapshots.

### 5. Route-Aligned Hotspot Scanning
At query time:
- Origin and destination are geocoded via **Nominatim (OpenStreetMap)**
- The actual road path is fetched from **OSRM** (real road geometry, not straight lines)
- A **vectorized Haversine scan** checks all 1,126 hotspots against every route point
- Only hotspots within **500m of the actual road path** are surfaced — no off-route false alerts

### 6. Real-Time Context Layers
- **OpenWeatherMap API** — live weather (temperature, wind, rain/fog flags) at the route midpoint
- **Gemini AI (gemini-2.0-flash)** — generates a short, driver-facing safety brief per hotspot combining accident history, current weather, peak hours, and primary cause. Falls back to a rule-based description if the key is not set.

---

## Cities Covered
Chennai · Mumbai · Delhi · Bangalore · Hyderabad · Pune · Kolkata · Chandigarh

---

## Tech Stack

| Layer | Technology |
|---|---|
| App Framework | Streamlit |
| ML Model | scikit-learn RandomForestClassifier |
| Clustering | scikit-learn DBSCAN (Haversine) |
| Maps | Folium + streamlit-folium |
| Routing | OSRM (open-source road router) |
| Geocoding | Nominatim / OpenStreetMap |
| Weather | OpenWeatherMap API |
| AI Descriptions | Google Gemini API (gemini-2.0-flash) |
| News Ingestion | NewsAPI |
| Scheduler | APScheduler (CronTrigger) |
| Model Persistence | joblib |

---

## Project Structure

```
road-accident-app/
├── app.py                        # Entry point — redirects to Home
├── config.py                     # API keys, city coords, constants
├── requirements.txt
├── pages/
│   ├── Home.py                   # Landing page with stats and how-it-works
│   └── 5_Driver_Alert.py         # Core route analyzer — map + alert cards
├── utils/
│   ├── hotspot_engine.py         # DBSCAN clustering, hotspot builder
│   ├── risk_model.py             # Random Forest train/predict
│   ├── route_analyzer.py         # Geocoding, OSRM routing, hotspot scan
│   ├── ai_description.py         # Gemini + fallback alert descriptions
│   ├── news_fetcher.py           # NewsAPI ingestion + NLP extraction
│   ├── auto_retrain.py           # APScheduler daily retrain job
│   └── ui_components.py          # CSS, nav components
├── Dataset1 Folder/
│   └── indian_roads_dataset.csv
├── Dataset2 Folder/
│   └── accident_prediction_india.csv
└── sample_data/
    ├── hotspots.pkl              # Cached DBSCAN clusters
    ├── risk_model.pkl            # Trained Random Forest
    ├── retrain_log.json          # Auto-retrain history
    └── news_cache.json           # Latest fetched news rows
```

---

## Setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

Set your API keys in `config.py`:
```python
OPENWEATHER_KEY = "<your_openweathermap_key>"
NEWSAPI_KEY     = "<your_newsapi_key>"
GEMINI_KEY      = "<your_gemini_key>"   # optional — fallback descriptions work without it
```

---

## The Bigger Vision

The natural evolution of this project is a **Google Maps API integration** — where this ML risk layer becomes a real-time overlay on top of existing navigation. Every route a driver plans would automatically surface the accident hotspots along it, the risk level, and a plain-language safety brief — without requiring any behavioral change from the user.

The goal is to make risk-awareness **invisible infrastructure**: something that works in the background every time someone opens a map, so that knowing the danger before you drive becomes the default, not the exception.

---

## Stats
- 20,000+ accident records trained on
- 1,126 DBSCAN hotspot clusters indexed
- 8 major Indian cities covered
- 500m route-alignment radius for hotspot alerts
- Daily auto-retrain at 02:00 AM
- 55 HIGH risk zones identified
