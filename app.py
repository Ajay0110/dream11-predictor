import streamlit as st
import pandas as pd
import requests

# --- Config ---
st.set_page_config("Dream11 Predictor", layout="wide")
st.title("🏏 Live Dream11 Predictor")

# Load stats
@st.cache_data
def load_stats():
    try:
        return pd.read_csv("player_stats.csv")
    except:
        st.error("player_stats.csv not found.")

stats_df = load_stats()

# Live matches from AllSportsAPI
@st.cache_data(ttl=60)
def fetch_live_matches():
    url = f"https://apiv2.allsportsapi.com/cricket/?met=Livescore&APIkey={st.secrets['SPORTSDEV_ALTERNATE_KEY']}"
    res = requests.get(url).json()
    return res.get("result", [])

live = fetch_live_matches()

if not live:
    st.warning("No live matches right now.")
else:
    for m in live:
        st.subheader(f"{m['event_home_team']} vs {m['event_away_team']} – 🔴 Live")
        # Assume squads are available via Sportsdev or separate endpoint
        # Use placeholder team lists here:
        team_players = m.get("squad", [])  # Replace with actual squad fetching
        all_players = []
        for p in team_players:
            pts = stats_df.loc[stats_df['player']==p, 'points'].squeeze() if p in stats_df['player'].values else 0
            all_players.append({"name": p, "points": pts})
        top11 = sorted(all_players, key=lambda x: x['points'], reverse=True)[:11]
        st.table(pd.DataFrame(top11))

st.caption("Using AllSportsAPI Livescore for live matches")
