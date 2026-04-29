import streamlit as st
import pandas as pd
import numpy as np
import random
import time

st.set_page_config(page_title="Player Props Finder", layout="wide")

st.title("🔥 Best Player Props Finder (NBA | NHL | MLB)")

# -----------------------------
# SIMULATED DATA (REPLACE WITH API LATER)
# -----------------------------
def generate_fake_props(league):
    players = []

    if league == "NBA":
        stat = "Points"
        names = ["LeBron James", "Luka Doncic", "Steph Curry", "Jayson Tatum", "Kevin Durant"]

    elif league == "NHL":
        stat = "Shots"
        names = ["Connor McDavid", "Nathan MacKinnon", "Auston Matthews", "Sidney Crosby", "David Pastrnak"]

    else:
        stat = "Hits"
        names = ["Aaron Judge", "Shohei Ohtani", "Mookie Betts", "Freddie Freeman", "Juan Soto"]

    for name in names:
        line = random.uniform(1.5, 30)
        last5 = np.random.normal(loc=line, scale=3, size=5)

        avg = np.mean(last5)
        hit_rate = sum(last5 > line) / 5

        edge = avg - line

        players.append({
            "Player": name,
            "Stat": stat,
            "Line": round(line, 2),
            "Last 5 Avg": round(avg, 2),
            "Hit Rate": f"{hit_rate*100:.0f}%",
            "Edge": round(edge, 2)
        })

    return pd.DataFrame(players)

# -----------------------------
# SCORING FUNCTION
# -----------------------------
def find_best_props(df):
    df["Score"] = df["Edge"] * 2 + df["Last 5 Avg"]
    return df.sort_values(by="Score", ascending=False)

# -----------------------------
# UI
# -----------------------------
league = st.selectbox("Select League", ["NBA", "NHL", "MLB"])

if st.button("Find Best Props"):
    with st.spinner("Analyzing player props..."):
        time.sleep(1)

        df = generate_fake_props(league)
        best = find_best_props(df)

        st.subheader("📊 All Props")
        st.dataframe(df)

        st.subheader("🔥 Best Picks Today")
        st.dataframe(best.head(3))

        # Highlight best pick
        top = best.iloc[0]

        st.success(
            f"Top Play: {top['Player']} OVER {top['Line']} {top['Stat']} "
            f"(Edge: {top['Edge']}, Hit Rate: {top['Hit Rate']})"
        )

# -----------------------------
# NOTES
# -----------------------------
st.markdown("""
### ⚠️ Notes
- This version uses simulated data  
- Replace with real APIs for live betting:
  - Odds API
  - PrizePicks
  - Underdog Fantasy  
- Always verify lines before betting
""")
