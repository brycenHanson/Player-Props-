import streamlit as st
import pandas as pd
import numpy as np
from nba_api.stats.endpoints import scoreboardv2

st.set_page_config(page_title="Playoff Pulse", layout="wide")

st.title("🏀 Playoff Pulse Dashboard")

# =========================
# SIMPLE MOCK PLAYOFF BRACKET
# (we upgrade to live data later)
# =========================
nba_playoffs = {
    "East": [
        {"series": "BOS vs MIA", "score": "2-1"},
        {"series": "NYK vs PHI", "score": "1-2"}
    ],
    "West": [
        {"series": "DEN vs LAL", "score": "3-0"},
        {"series": "GSW vs DAL", "score": "2-2"}
    ]
}

tab1, tab2 = st.tabs(["🏀 NBA Playoffs", "📊 Team Analyzer"])

# =========================
# TAB 1 - PLAYOFF BRACKET
# =========================
with tab1:
    st.subheader("NBA Playoff Bracket")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Eastern Conference")
        for series in nba_playoffs["East"]:
            st.write(f"**{series['series']}** — {series['score']}")

    with col2:
        st.markdown("### Western Conference")
        for series in nba_playoffs["West"]:
            st.write(f"**{series['series']}** — {series['score']}")

# =========================
# TAB 2 - SIMPLE TEAM MODEL
# =========================
teams = ["BOS", "MIA", "NYK", "PHI", "DEN", "LAL", "GSW", "DAL"]

with tab2:
    team = st.selectbox("Select Team", teams)

    np.random.seed(hash(team) % 1000)

    # fake but realistic metrics
    offense = np.random.randint(100, 120)
    defense = np.random.randint(100, 120)
    momentum = np.random.uniform(0.4, 0.9)

    win_prob = (offense - defense + 10) * 2 + momentum * 20
    win_prob = max(10, min(90, win_prob))

    st.subheader(f"{team} Analysis")

    col1, col2, col3 = st.columns(3)

    col1.metric("Offensive Rating", offense)
    col2.metric("Defensive Rating", defense)
    col3.metric("Momentum", round(momentum, 2))

    st.subheader("🧠 Win Probability Estimate")
    st.progress(int(win_prob))
    st.write(f"Estimated Win Chance: **{round(win_prob, 1)}%**")
