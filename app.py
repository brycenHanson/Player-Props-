import streamlit as st
import requests
import pandas as pd
import numpy as np

st.set_page_config(page_title="Player Props AI", layout="wide")

# =========================
# CONFIG
# =========================
API_KEY = st.secrets.get("API_KEY", "YOUR_ODDS_API_KEY")
BASE_URL = "https://api.the-odds-api.com/v4/sports"

SPORTS = {
    "NBA": "basketball_nba",
    "NHL": "icehockey_nhl",
    "MLB": "baseball_mlb"
}

# =========================
# CACHE API CALLS
# =========================
@st.cache_data(ttl=60)
def fetch_props(sport_key):
    url = f"{BASE_URL}/{sport_key}/odds"

    params = {
        "apiKey": API_KEY,
        "regions": "us",
        "markets": "player_points",
        "oddsFormat": "american"
    }

    try:
        res = requests.get(url, params=params, timeout=10)

        if res.status_code != 200:
            return {"error": f"HTTP {res.status_code}", "raw": res.text}

        return res.json()

    except Exception as e:
        return {"error": str(e)}

# =========================
# SIMPLE MODEL
# =========================
def get_player_avg(player):
    np.random.seed(abs(hash(player)) % 10000)
    return 20 + np.random.normal(0, 3)

def predict(avg, line):
    diff = avg - line
    confidence = min(100, abs(diff) * 10)

    return ("OVER" if diff > 0 else "UNDER"), round(confidence, 1)

# =========================
# UI
# =========================
st.title("🏀🏒⚾ Player Props AI Dashboard")

sport = st.selectbox("Select Sport", list(SPORTS.keys()))
sport_key = SPORTS[sport]

if st.button("Load Props"):

    data = fetch_props(sport_key)

    # =========================
    # HANDLE ERRORS FIRST
    # =========================
    if isinstance(data, dict) and "error" in data:
        st.error(f"API Error: {data['error']}")
        st.stop()

    if not isinstance(data, list):
        st.error("Unexpected API response format.")
        st.json(data)
        st.stop()

    rows = []

    # =========================
    # SAFE PARSING
    # =========================
    for game in data:
        if not isinstance(game, dict):
            continue

        for bookmaker in game.get("bookmakers", []) or []:
            for market in bookmaker.get("markets", []) or []:

                if "player" not in market.get("key", ""):
                    continue

                for outcome in market.get("outcomes", []) or []:

                    rows.append({
                        "player": outcome.get("description", "Unknown"),
                        "prop": market.get("key"),
                        "line": outcome.get("point", 0)
                    })

    df = pd.DataFrame(rows)

    # =========================
    # EMPTY STATE
    # =========================
    if df.empty:
        st.warning("No player props found for this sport right now.")
        st.stop()

    st.subheader("📊 Live Player Props")
    st.dataframe(df)

    # =========================
    # MODEL OUTPUT
    # =========================
    st.subheader("🧠 AI Predictions")

    results = []

    for _, row in df.iterrows():
        avg = get_player_avg(row["player"])
        pick, conf = predict(avg, row["line"])

        results.append({
            "Player": row["player"],
            "Prop": row["prop"],
            "Line": row["line"],
            "Model Avg": round(avg, 2),
            "Pick": pick,
            "Confidence %": conf
        })

    result_df = pd.DataFrame(results)

    st.dataframe(result_df.sort_values("Confidence %", ascending=False))
