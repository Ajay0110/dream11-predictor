import streamlit as st
import pandas as pd
import requests
import time

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Dream11 Predictor", layout="wide")

# ------------------ LOAD API KEY ------------------
API_KEY = st.secrets["CRICAPI_KEY"]

# ------------------ LOAD DEFAULT STATS ------------------
@st.cache_data
def load_default_stats():
    return pd.read_csv("player_stats.csv")

# ------------------ FETCH CURRENT MATCHES ------------------
def load_current_matches():
    url = f"https://api.cricapi.com/v1/currentMatches?apikey={API_KEY}&offset=0"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get("data", [])
    except:
        pass
    return []

# ------------------ GET CONFIRMED XI ------------------
def get_playing_11(team):
    if "players" in team:
        return [p["name"] for p in team["players"]]
    return []

# ------------------ FILTER TOP 11 ------------------
def predict_top_11(players, stats_df):
    df = stats_df[stats_df["player"].isin(players)].copy()
    df = df.sort_values(by="fantasy_points", ascending=False)
    return df.head(11)

# ------------------ MAIN APP ------------------
st.title("🏏 Dream11 Predictor for All Live Matches")

autorefresh = st.toggle("🔄 Auto-refresh every 60 seconds", value=False)

if autorefresh:
    time.sleep(60)
    st.experimental_rerun()

# ------------------ STATS CSV LOAD ------------------
uploaded_file = st.file_uploader("📁 Upload player stats CSV", type=["csv"])
if uploaded_file:
    stats_df = pd.read_csv(uploaded_file)
    st.success("✅ New stats file loaded")
else:
    stats_df = load_default_stats()

# ------------------ FETCH & DISPLAY MATCHES ------------------
matches = load_current_matches()

if not matches:
    st.error("⚠️ No matches available right now. Please check later.")
    st.stop()

for match in matches:
    if not match.get("teamInfo"): continue

    team1 = match["teamInfo"][0]
    team2 = match["teamInfo"][1]
    has_squad = match.get("hasSquad", False)

    with st.container():
        st.subheader(f"📍 {match['name']} - {team1['name']} vs {team2['name']}")

        col1, col2 = st.columns(2)
        with col1:
            st.image(team1["img"], width=100)
            st.markdown(f"**{team1['name']}**")
        with col2:
            st.image(team2["img"], width=100)
            st.markdown(f"**{team2['name']}**")

        if has_squad:
            team1_players = get_playing_11(team1)
            team2_players = get_playing_11(team2)
            st.success("✅ Playing XI confirmed!")
        else:
            team1_players = [p["name"] for p in team1.get("players", [])]
            team2_players = [p["name"] for p in team2.get("players", [])]
            st.warning("⏳ Waiting for toss / playing XI confirmation...")

        combined_players = team1_players + team2_players
        top_11 = predict_top_11(combined_players, stats_df)

        st.markdown("### 🏆 Top 11 Players Prediction")
        st.dataframe(top_11.reset_index(drop=True))

        st.markdown("---")
