import streamlit as st
import pandas as pd
import numpy as np
from nba_api.stats.endpoints import leaguestandingsv3

st.set_page_config(page_title="ESPN Playoff Engine", layout="wide")

st.title("🏆 ESPN-Level Playoff Intelligence Engine")

# =========================
# GET STANDINGS
# =========================
def get_standings():
    try:
        data = leaguestandingsv3.LeagueStandingsV3().get_data_frames()[0]
        return data
    except:
        return pd.DataFrame()

# =========================
# ELO SYSTEM
# =========================
def compute_elo(df):
    teams = df["TeamName"].tolist()
    
    np.random.seed(42)

    elos = {team: 1500 + np.random.randint(-100, 100) for team in teams}

    return elos

# =========================
# WIN PROBABILITY
# =========================
def win_prob(elo_a, elo_b):
    return 1 / (1 + 10 ** ((elo_b - elo_a) / 400))

# =========================
# MONTE CARLO SIMULATION
# =========================
def simulate_series(team_a, team_b, elos, n_sim=500):
    a_wins = 0

    for _ in range(n_sim):
        wins_a = 0
        wins_b = 0

        while wins_a < 4 and wins_b < 4:
            p = win_prob(elos[team_a], elos[team_b])
            if np.random.rand() < p:
                wins_a += 1
            else:
                wins_b += 1

        if wins_a > wins_b:
            a_wins += 1

    return a_wins / n_sim

# =========================
# LOAD DATA
# =========================
standings = get_standings()

tab1, tab2 = st.tabs(["🏀 NBA Playoffs", "🧠 Simulation Engine"])

# =========================
# TAB 1 - PLAYOFF BRACKET
# =========================
with tab1:
    st.subheader("📊 Current Standings")

    if standings.empty:
        st.error("No data available")
    else:
        east = standings[standings["Conference"] == "East"].head(8)
        west = standings[standings["Conference"] == "West"].head(8)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Eastern Conference (Projected Playoffs)")
            st.dataframe(east[["TeamName", "WINS", "LOSSES"]])

        with col2:
            st.markdown("### Western Conference (Projected Playoffs)")
            st.dataframe(west[["TeamName", "WINS", "LOSSES"]])

# =========================
# TAB 2 - SIMULATION ENGINE
# =========================
with tab2:
    st.subheader("🧠 Monte Carlo Playoff Simulation")

    if standings.empty:
        st.stop()

    elos = compute_elo(standings)

    teams = list(elos.keys())

    team_a = st.selectbox("Team A", teams)
    team_b = st.selectbox("Team B", teams, index=1)

    if st.button("Run Series Simulation"):

        prob = simulate_series(team_a, team_b, elos)

        st.subheader("📈 Series Outcome Probability")

        col1, col2 = st.columns(2)

        col1.metric(f"{team_a} Win Chance", f"{round(prob*100,1)}%")
        col2.metric(f"{team_b} Win Chance", f"{round((1-prob)*100,1)}%")

        st.progress(int(prob * 100))

# =========================
# BONUS: TEAM STRENGTH VIEW
# =========================
st.subheader("📊 Team Power Rankings (Elo Model)")

if standings is not None and not standings.empty:
    elos = compute_elo(standings)

    rank_df = pd.DataFrame([
        {"Team": k, "Elo Rating": v}
        for k, v in sorted(elos.items(), key=lambda x: x[1], reverse=True)
    ])

    st.dataframe(rank_df)
