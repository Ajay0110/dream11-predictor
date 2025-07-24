import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# CONFIG
API_KEY = st.secrets["CRICAPI_KEY"]
CSV_FILE = "player_stats.csv"  # Make sure this is the correct name in your repo

# Load CSV
@st.cache_data
def load_stats():
    try:
        df = pd.read_csv(CSV_FILE)
        return df
    except Exception as e:
        st.error(f"Failed to load CSV: {e}")
        return pd.DataFrame()

# Fetch today's matches
def get_today_matches():
    url = f"https://api.cricapi.com/v1/currentMatches?apikey={API_KEY}&offset=0"
    response = requests.get(url)
    if response.status_code != 200:
        st.error("Failed to fetch match data from API")
        return []
    matches = response.json().get("data", [])
    today = datetime.now().date()
    today_matches = [
        match for match in matches
        if match.get("date", "").startswith(str(today)) and match.get("status") not in ["Completed", "Match Ended"]
    ]
    return today_matches

# Predict best 11 players (demo logic)
def predict_best_11(players, stats_df):
    # Simple scoring logic demo: random or based on dummy logic
    filtered = stats_df[stats_df["name"].isin(players)]
    if "fantasy_score" in filtered.columns:
        top11 = filtered.sort_values(by="fantasy_score", ascending=False).head(11)
    else:
        top11 = filtered.head(11)  # fallback
    return top11

# --- UI ---
st.title("🏏 Dream11 Predictor - Fantasy 11 Demo")

stats_df = load_stats()
matches = get_today_matches()

if not matches:
    st.warning("No live/upcoming matches found today or squads not yet announced.")
else:
    match = st.selectbox("Select Match", matches, format_func=lambda x: f"{x['teamInfo'][0]['name']} vs {x['teamInfo'][1]['name']}")
    
    squads = []
    for team in match["teamInfo"]:
        for player in team.get("players", []):
            squads.append(player.get("name"))

    if squads:
        st.subheader("🧠 Predicted Best 11")
        predicted = predict_best_11(squads, stats_df)
        st.dataframe(predicted)
    else:
        st.info("👀 Squads not yet announced. Check back closer to match time!")

st.markdown("---")
st.caption("Demo powered by CSV + CricAPI")
