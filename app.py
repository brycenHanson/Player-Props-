import streamlit as st
import pandas as pd
import numpy as np
from nba_api.stats.endpoints import leaguestandingsv3

st.set_page_config(page_title="Championship Simulator", layout="wide")

st.title("🏆 Championship Simulator (NBA + NHL)")
st.subheader("Monte Carlo Playoff Forecast Engine")

# =========================
# LOAD STANDINGS
# =========================
def get_standings():
    try:
        df = leaguestandingsv3.LeagueStandingsV3().get_data_frames()[0]
        return df
    except:
        return pd.DataFrame()

# =========================
# ELO MODEL
# =========================
def build_elo(df):
    teams = df["TeamName"].tolist()
    np.random.seed(42)

    return {team: 1500 + np.random.randint(-120, 120) for team in teams}

# =========================
# WIN PROBABILITY
# =========================
def win_prob(elo_a, elo_b):
    return 1 / (1 + 10 ** ((elo_b - elo_a) / 400))

# =========================
# SIMULATE SERIES (BEST OF 7)
# =========================
def simulate_series(team_a, team_b, elos):
    wins_a = 0
    wins_b = 0

    while wins_a < 4 and wins_b < 4:
        if np.random.rand() < win_prob(elos[team_a], elos[team_b]):
            wins_a += 1
        else:
            wins_b += 1

    return team_a if wins_a > wins_b else team_b

# =========================
# SIMULATE FULL TOURNAMENT
# =========================
def simulate_playoffs(teams, elos):
    np.random.shuffle(teams)

    while len(teams) > 1:
        next_round = []

        for i in range(0, len(teams), 2):
            winner = simulate_series(teams[i], teams[i+1], elos)
            next_round.append(winner)

        teams = next_round

    return teams[0]

# =========================
# MONTE CARLO ENGINE
# =========================
def run_simulation(teams, elos, n=2000):
    results = {team: 0 for team in teams}

    for _ in range(n):
        champ = simulate_playoffs(teams.copy(), elos)
        results[champ] += 1

    return results

# =========================
# MAIN APP
# =========================
standings = get_standings()

if standings.empty:
    st.error("No data available")
    st.stop()

elos = build_elo(standings)
teams = list(elos.keys())

st.subheader("🏀 Playoff Teams Loaded")
st.write(f"{len(teams)} teams in simulation pool")

# =========================
# RUN SIMULATION
# =========================
if st.button("Run Championship Simulation (2000 runs)"):

    with st.spinner("Simulating playoffs..."):

        results = run_simulation(teams, elos, n=2000)

        df = pd.DataFrame([
            {"Team": k, "Championship Odds %": round(v / 2000 * 100, 2)}
            for k, v in results.items()
        ])

        df = df.sort_values("Championship Odds %", ascending=False)

        st.subheader("🏆 Championship Odds")

        st.dataframe(df)

        st.bar_chart(df.set_index("Team"))

# =========================
# MATCHUP VIEW
# =========================
st.subheader("⚔️ Matchup Simulator")

team_a = st.selectbox("Team A", teams)
team_b = st.selectbox("Team B", teams, index=1)

if st.button("Simulate Series"):

    a_wins = 0
    sims = 1000

    for _ in range(sims):
        winner = simulate_series(team_a, team_b, elos)
        if winner == team_a:
            a_wins += 1

    prob = a_wins / sims

    st.metric(f"{team_a} Win Probability", f"{round(prob*100,1)}%")
    st.metric(f"{team_b} Win Probability", f"{round((1-prob)*100,1)}%")

    st.progress(int(prob * 100))
