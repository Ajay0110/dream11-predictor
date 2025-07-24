import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# Title
st.set_page_config(page_title="Dream11 Predictor", layout="wide")
st.title("🏏 Dream11 Fantasy XI Predictor")

# Load player stats CSV
@st.cache_data

def load_stats():
    try:
        return pd.read_csv("player_stats.csv")
    except FileNotFoundError:
        st.error("The stats CSV file (player_stats.csv) was not found. Please upload it to the root of the repo.")
        return pd.DataFrame()

stats_df = load_stats()

# Load API Key from secrets
API_KEY = st.secrets["CRICAPI_KEY"]
API_URL = f"https://api.cricapi.com/v1/currentMatches?apikey={API_KEY}&offset=0"

# Get today's matches and filter live/upcoming
response = requests.get(API_URL)
matches = response.json().get("data", [])
today = datetime.now().date()

live_matches = []
for match in matches:
    date_str = match.get("date", "")[:10]
    try:
        match_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        continue
    status = match.get("status", "").lower()
    started = match.get("matchStarted", False)

    if match_date == today and (started and "won by" not in status or not started):
        live_matches.append(match)

if not live_matches:
    st.warning("No upcoming or live matches today with available squad info.")
else:
    for match in live_matches:
        team1 = match.get("teamInfo", [{}])[0].get("name", "Team A")
        team2 = match.get("teamInfo", [{}])[1].get("name", "Team B")
        squads = match.get("squads", [])  # Some matches might not have this

        st.markdown(f"### 🏟️ {team1} vs {team2}")
        if not squads:
            st.info("Squads not announced yet.")
            continue

        teams = {team['teamName']: team['players'] for team in squads}

        # Fantasy XI logic (top 11 players based on stats)
        all_players = []
        for team, players in teams.items():
            for player in players:
                name = player.get("name", "")
                player_stats = stats_df[stats_df['player'] == name]
                if not player_stats.empty:
                    total_points = player_stats.iloc[0]["points"]
                else:
                    total_points = 0
                all_players.append({"name": name, "team": team, "points": total_points})

        # Sort and select top 11
        top_11 = sorted(all_players, key=lambda x: x["points"], reverse=True)[:11]

        df = pd.DataFrame(top_11)
        st.dataframe(df, use_container_width=True)

        st.markdown("---")
