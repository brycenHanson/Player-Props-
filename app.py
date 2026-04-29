import streamlit as st
import pandas as pd
import numpy as np
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players

st.set_page_config(page_title="Prop Model (No API)", layout="wide")

# =========================
# GET PLAYER LIST
# =========================
nba_players = players.get_players()
player_names = sorted([p["full_name"] for p in nba_players])

st.title("🏀 Player Props Model (No API Version)")

selected_player = st.selectbox("Select NBA Player", player_names)

stat_type = st.selectbox("Stat Type", ["PTS", "REB", "AST"])

# =========================
# FETCH GAME LOGS
# =========================
def get_stats(player_name):
    player_id = next(
        p["id"] for p in nba_players if p["full_name"] == player_name
    )

    logs = playergamelog.PlayerGameLog(player_id=player_id).get_data_frames()[0]

    if logs.empty:
        return None

    return logs

# =========================
# MODEL
# =========================
def calculate_projection(data, stat):
    last_games = data.head(15)

    avg = last_games[stat].mean()
    std = last_games[stat].std()

    # simple projection adjustment
    projection = avg + (np.random.normal(0, 1))

    return avg, std, projection

def predict(avg, projection):
    diff = avg - projection
    confidence = min(100, abs(diff) * 15)

    return ("OVER" if diff > 0 else "UNDER"), confidence

# =========================
# RUN
# =========================
if st.button("Generate Pick"):

    data = get_stats(selected_player)

    if data is None:
        st.error("No data found for player.")
        st.stop()

    stat_map = {
        "PTS": "PTS",
        "REB": "REB",
        "AST": "AST"
    }

    stat_col = stat_map[stat_type]

    avg, std, projection = calculate_projection(data, stat_col)

    pick, conf = predict(avg, projection)

    # =========================
    # OUTPUT
    # =========================
    st.subheader(f"📊 {selected_player} - {stat_type}")

    st.write("Last 10–15 game stats:")
    st.dataframe(data[[stat_col]].head(10))

    col1, col2, col3 = st.columns(3)

    col1.metric("Player Avg", round(avg, 2))
    col2.metric("Model Projection", round(projection, 2))
    col3.metric("Std Dev", round(std, 2))

    st.subheader("🧠 Prediction")

    st.success(f"Pick: {pick}")
    st.info(f"Confidence: {round(conf, 1)}%")
