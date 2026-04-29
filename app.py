import streamlit as st
import requests
import pandas as pd
import numpy as np

st.set_page_config(page_title="Player Props AI", layout="wide")

# =========================
# CONFIG
# =========================
API_KEY = "YOUR_ODDS_API_KEY"
BASE_URL = "https://api.the-odds-api.com/v4/sports"

SPORTS = {
    "NBA": "basketball_nba",
    "NHL": "icehockey_nhl",
    "MLB": "baseball_mlb"
}

# =========================
# FETCH ODDS
# =========================
def fetch_props(sport_key):
    url = f"{BASE_URL}/{sport_key}/odds"
    params = {
        "apiKey": API_KEY,
        "regions": "us",
        "markets": "player_points,player_shots,player_hits",
        "oddsFormat": "american"
    }

    try:
        res = requests.get(url, params=params)
        data = res.json()
        return data
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return []

# =========================
# MOCK PLAYER STATS (replace with real dataset later)
# =========================
def get_player_avg(player_name, stat_type):
    np.random.seed(abs(hash(player_name)) % 10000)

    base = {
        "points": 20,
        "shots": 5,
        "hits": 3
    }

    noise = np.random.normal(0, 3)
    return base.get(stat_type, 10) + noise

# =========================
# SIMPLE MODEL
# =========================
def predict(player_avg, line):
    diff = player_avg - line

    confidence = min(100, abs(diff) * 12)

    if diff > 0:
        return "OVER", confidence
    else:
        return "UNDER", confidence

# =========================
# UI
# =========================
st.title("🏀🏒⚾ Player Props Over/Under AI Model")

sport = st.selectbox("Select Sport", list(SPORTS.keys()))
sport_key = SPORTS[sport]

if st.button("Load Live Props"):
    data = fetch_props(sport_key)

    if not data:
        st.warning("No data returned. Check API key or limits.")
    else:
        rows = []

        for game in data:
            for bookmaker in game.get("bookmakers", []):
                for market in bookmaker.get("markets", []):
                    if "player" in market["key"]:
                        for outcome in market["outcomes"]:
                            rows.append({
                                "player": outcome.get("description"),
                                "prop": market["key"],
                                "line": outcome.get("point", 0)
                            })

        df = pd.DataFrame(rows)

        if df.empty:
            st.warning("No player props found in API response.")
        else:
            st.dataframe(df)

            st.subheader("📊 AI Predictions")

            results = []

            for _, row in df.iterrows():
                stat_type = "points"

                player_avg = get_player_avg(row["player"], stat_type)

                pick, conf = predict(player_avg, row["line"])

                results.append({
                    "Player": row["player"],
                    "Prop": row["prop"],
                    "Line": row["line"],
                    "Avg Model Stat": round(player_avg, 2),
                    "Pick": pick,
                    "Confidence %": round(conf, 1)
                })

            results_df = pd.DataFrame(results)

            st.dataframe(results_df.sort_values("Confidence %", ascending=False))
