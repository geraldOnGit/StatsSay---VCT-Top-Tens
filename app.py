import streamlit as st
import requests
import pandas as pd
import altair as alt

API_URL = "https://vct-fastapi-backend.onrender.com/top-players"


st.set_page_config(page_title="VCT Top Players", layout="wide")
st.title("🏆 VCT Top 10 Players by Tournament")

# Year selector
year = st.selectbox("Select Year", [2021, 2022, 2023, 2024, 2025])

# Fetch data
with st.spinner(f"Loading data for {year}..."):
    response = requests.get(API_URL, params={"year": year})

# Validate
if response.status_code != 200:
    st.error(response.json().get("detail"))
    st.stop()

data = response.json()["top_players"]

if not data:
    st.warning("No data found for this year.")
    st.stop()

# Tournament selector
tournaments = list(data.keys())
selected_tournament = st.selectbox("Select Tournament", tournaments)

# Player DataFrame
df = pd.DataFrame(data[selected_tournament])
if df.empty:
    st.warning("No data for this tournament.")
    st.stop()

# Clean numbers
numeric_cols = df.select_dtypes(include='number').columns
df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')

# Show table
st.subheader(f"🔹 Top 10 Players — {selected_tournament}")
st.dataframe(df.style.format("{:.2f}", subset=numeric_cols), use_container_width=True)

# Metric visualizations
st.markdown("### 📊 Metric Visualizations")

metric = st.selectbox("Select Metric", [
    "Composite Score",
    "Average Combat Score",
    "K:D Ratio",
    "Headshot %",
    "Kill, Assist, Trade, Survive %",
    "Clutch Success %",
    "Average Damage Per Round",
    "First Kills"
])

if metric not in df.columns:
    st.warning(f"{metric} not available for this tournament.")
else:
    chart_df = df[["Player", metric]].sort_values(metric, ascending=False)

    chart = alt.Chart(chart_df).mark_bar().encode(
        x=alt.X(metric, title=metric),
        y=alt.Y("Player", sort='-x'),
        color=alt.value("#4B8BBE")
    ).properties(
        width=700,
        height=400,
        title=f"Top 10 Players by {metric}"
    )

    st.altair_chart(chart, use_container_width=True)
