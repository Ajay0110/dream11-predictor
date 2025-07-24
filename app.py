import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Dream11 Predictor", layout="wide")

st.title("🏏 Dream11 Team Predictor")
st.markdown("Get the best predicted XI based on real-time match data.")
st.markdown("---")

API_KEY = st.secrets["CRICAPI_KEY"]
API_URL = f"https://api.cricapi.com/v1/currentMatches?apikey={API_KEY}&offset=0"

@st.cache_data(ttl=600)
def get_today_matches():
    try:
        res = requests.get(API_URL)
        data = res.json()
        today = datetime.today().date()
        matches = []

        for match in data.get("data", []):
            date_str = match.get("date", "")[:10]
            try:
                match_day = datetime.strptime(date_str, "%Y-%m-%d").date()
            except:
                continue

            status = match.get("status", "").lower()
            if match_day != today:
                continue
            if "completed" in status or "result" in status:
                continue

            matches.append(match)
        return matches
    except Exception as e:
        st.error("Failed to fetch match data.")
        return []

def extract_players(match):
    teams = match.get("teams", [])
    team_data = match.get("teamInfo", [])
    team_players = {}

    if not team_data:
        return {}

    for team in team_data:
        name = team.get("name")
        players = team.get("players", [])
        if players:
            team_players[name] = players
    return team_players

def predict_best_11(team_players):
    all_players = []
    for team, players in team_players.items():
        for player in players:
            all_players.append({"team": team, **player})

    # Simple logic: Allrounders > Bowlers > Batsmen > Keepers
    role_priority = {
        "Allrounder": 1,
        "Batting Allrounder": 1,
        "Bowling Allrounder": 1,
        "Bowler": 2,
        "Batsman": 3,
        "WK-Batsman": 4,
        "Wicketkeeper": 4
    }

    sorted_players = sorted(all_players, key=lambda x: role_priority.get(x.get("role", ""), 5))
    return sorted_players[:11]

today_matches = get_today_matches()

if not today_matches:
    st.warning("No matches with announced squads today.")
else:
    for match in today_matches:
        st.subheader(f"{match.get('name', 'Unknown Match')}")
        team_players = extract_players(match)

        if not team_players:
            st.info("🚨 Squads not announced yet.")
            continue

        best_11 = predict_best_11(team_players)
        for player in best_11:
            st.markdown(f"**{player['name']}** ({player['team']}) - {player.get('role', 'Unknown')}")

        st.markdown("---")
