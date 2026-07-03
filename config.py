OPENWEATHER_KEY = ""   # paste your OpenWeatherMap key here
NEWSAPI_KEY     = ""   # paste your NewsAPI key here
GEMINI_KEY      = ""   # paste your Gemini key here

CITIES = [
    "Chennai", "Mumbai", "Delhi", "Bangalore",
    "Hyderabad", "Pune", "Kolkata", "Chandigarh"
]

CITY_COORDS = {
    "Chennai":    (13.0827, 80.2707),
    "Mumbai":     (19.0760, 72.8777),
    "Delhi":      (28.6139, 77.2090),
    "Bangalore":  (12.9716, 77.5946),
    "Hyderabad":  (17.3850, 78.4867),
    "Pune":       (18.5204, 73.8567),
    "Kolkata":    (22.5726, 88.3639),
    "Chandigarh": (30.7333, 76.7794),
}

NEWS_FETCH_DAYS   = 30    # look back window for news
RETRAIN_HOUR      = 2     # 2 AM daily auto-retrain
WARN_RADIUS_M     = 500   # hotspot alert radius in metres — only truly on-route hotspots
HOTSPOT_PATH      = "sample_data/hotspots.pkl"
MODEL_PATH        = "sample_data/risk_model.pkl"
RETRAIN_LOG_PATH  = "sample_data/retrain_log.json"
NEWS_CACHE_PATH   = "sample_data/news_cache.json"
