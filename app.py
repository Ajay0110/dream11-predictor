import streamlit as st
import pandas as pd
import requests

# Set Streamlit app configuration
st.set_page_config(page_title="Dream11 Live Predictor", layout="wide")
st.title("🏏 Dream11 Live Match Predictor")
st.markdown("---")

# Load player stats from CSV
@st.cache_data

def load_stats():
    try:
        return pd.read_csv("player_stats.csv")
    except FileNotFoundError:
        st.error("❌ 'player_stats.csv' not found in the repo root.")
        return pd.DataFrame()

stats_df = load_stats()

# Fetch live matches from AllSportsAPI
@st.cache_data(ttl=60)
def fetch_live_matches():
    url = f"https://apiv2.allsportsapi.com/cricket/?met=Livescore&APIkey={st.secrets['SPORTSDEV_ALTERNATE_KEY']}"
    res = requests.get(url)
    if res.status_code != 200:
        st.error("⚠️ Failed to fetch live matches from API.")
        return []
    data = res.json()
    return data.get("result", [])

live_matches = fetch_live_matches()

if not live_matches:
    st.warning("📭 No live matches at the moment.")
else:
    for match in live_matches:
        team1 = match.get("event_home_team")
        team2 = match.get("event_away_team")
        st.subheader(f"{team1} vs {team2} — 🔴 Live")

        # For now, simulate squad extraction using player_stats.csv
        team_players = stats_df[stats_df['team'].isin([team1, team2])]

        if team_players.empty:
            st.info("⏳ Waiting for confirmed squad announcement...")
            continue

        # Rank players based on their 'points' column
        top_players = team_players.sort_values(by="points", ascending=False).head(11)

        st.markdown("### 🏆 Predicted Fantasy XI")
        st.table(top_players[['player', 'role', 'points']].reset_index(drop=True))
        st.markdown("---")

st.caption("Built with ❤️ using AllSportsAPI + Dream11 stats")
