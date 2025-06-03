import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
from pyspark.sql import SparkSession
from datetime import timedelta

# App title
st.set_page_config(page_title="Live Weather Map", layout="wide")
st.title("🌍 Live Weather Map (Real-Time)")

# Load data from parquet via Spark
@st.cache_resource(ttl=60)  # refresh every 60s
def load_latest_weather():
    spark = SparkSession.builder.appName("ReadWeatherData").getOrCreate()
    df = spark.read.parquet("/tmp/stream_weather_output/")
    pdf = df.toPandas()

    # Convert timestamp to datetime
    pdf['timestamp_readable'] = pd.to_datetime(pdf['timestamp_readable'])

    # Align to latest 15-minute window
    now = pdf['timestamp_readable'].max()
    aligned_now = now - timedelta(
        minutes=now.minute % 15,
        seconds=now.second,
        microseconds=now.microsecond
    )
    window_start = aligned_now - timedelta(minutes=15)

    # Filter for window & dedupe per city
    window_df = pdf[(pdf['timestamp_readable'] >= window_start) & (pdf['timestamp_readable'] <= aligned_now)].copy()
    latest_df = window_df.sort_values("timestamp_readable", ascending=False).drop_duplicates("city")

    return latest_df

# Load data
df = load_latest_weather()

if df.empty:
    st.warning("⚠️ No weather data available in the last 15 minutes.")
    st.stop()

# Build folium map
m = folium.Map(location=[20, 0], zoom_start=2)
marker_cluster = MarkerCluster().add_to(m)

for _, row in df.iterrows():
    popup_text = (
        f"<b>{row['city']}, {row['country']}</b><br>"
        f"Temp: {row['temperature']}°C<br>"
        f"Feels Like: {row['feels_like']}°C<br>"
        f"Weather: {row['condition_desc']}<br>"
        f"Humidity: {row['humidity']}%<br>"
        f"Wind: {row['wind_speed']} m/s<br>"
        f"Time: {row['timestamp_readable']}"
    )

    # Color by condition
    condition = row['condition_main']
    if condition in ["Rain", "Thunderstorm", "Snow"]:
        colour = "red"
    elif condition in ["Clouds", "Mist"]:
        colour = "orange"
    else:
        colour = "green"

    folium.CircleMarker(
        location=[row["latitude"], row["longitude"]],
        radius=6,
        color=colour,
        fill=True,
        fill_color=colour,
        fill_opacity=0.7,
        popup=folium.Popup(popup_text, max_width=250)
    ).add_to(marker_cluster)

# Display map
st_folium(m, width=900, height=600)

st.caption("🕒 Map updates automatically every 60 seconds with the most recent data.")
