import streamlit as st
import requests
import pandas as pd

# Title
st.set_page_config(page_title="Dream11 Predictor", layout="wide")
st.title("🏏 Dream11 Best 11 Predictor")
st.markdown("---")

# Secrets
API_KEY = st.secrets["CRICAPI_KEY"]

# API URL
API_URL = f"https://api.cricapi.com/v1/currentMatches?apikey={API_KEY}&offset=0"

# Fetch matches from CricAPI
@st.cache_data(ttl=300)
def get_today_matches():
    try:
        response = requests.get(API_URL)
        data = response.json()
        return data.get("data", [])
    except Exception as e:
        st.error(f"Error fetching matches: {e}")
        return []

# Best 11 selection logic
def select_best_11_players(squad):
    preferred_roles = [
        "Batting Allrounder", "Bowling Allrounder", "Allrounder",
        "Bowler", "Batsman", "WK-Batsman", "Wicketkeeper"
    ]
    sorted_players = sorted(
        squad,
        key=lambda p: preferred_roles.index(p["role"]) if p["role"] in preferred_roles else 99
    )
    return sorted_players[:11]

# Load Matches
matches = get_today_matches()

if not matches:
    st.warning("No matches available today or API limit reached.")
else:
    for match in matches:
        team1 = match.get("teamInfo", [])[0].get("name", "Team 1")
        team2 = match.get("teamInfo", [])[1].get("name", "Team 2")
        st.subheader(f"📌 {team1} vs {team2}")

        team1_players = match.get("teamInfo", [])[0].get("players", [])
        team2_players = match.get("teamInfo", [])[1].get("players", [])

        # Combine squads
        full_squad = team1_players + team2_players

        # Predict Best 11
        best_11 = select_best_11_players(full_squad)

        with st.expander("🔮 Predicted Best 11 Players"):
            for i, player in enumerate(best_11, start=1):
                st.markdown(
                    f"{i}. **{player['name']}** – {player['role']} ({player.get('battingStyle', 'NA')})"
                )

st.markdown("---")
st.caption("Built with ❤️ by Ajay")
