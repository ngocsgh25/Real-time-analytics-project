import streamlit as st
import seaborn as sns
import pandas as pd
from datetime import timedelta
from datetime import datetime
from pyspark.sql import SparkSession
import altair as alt
import matplotlib.pyplot as plt

st.set_page_config(page_title="Dashboard 2", layout="wide")
st.title("🌍 Dashboard 2: Activity Recommendations Based on Real-Time Weather")
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.markdown(f"🕒 **Current Time:** {now}")

@st.cache_resource(ttl=60)
def load_data():
    spark = SparkSession.builder.appName("WeatherScore").getOrCreate()
    df = spark.read.parquet("/tmp/stream_weather_output/")
    return df.toPandas()

pandas_df = load_data()
if pandas_df.empty:
    st.warning("No weather data available.")
    st.stop()

pandas_df['timestamp_readable'] = pd.to_datetime(pandas_df['timestamp_readable'])

now = pandas_df['timestamp_readable'].max()
aligned_now = now - timedelta(
    minutes=now.minute % 5,
    seconds=now.second,
    microseconds=now.microsecond
)
window_start = aligned_now - timedelta(minutes=30)

window_df = pandas_df[
    (pandas_df['timestamp_readable'] >= window_start) &
    (pandas_df['timestamp_readable'] < aligned_now)
].copy()

agg_df = window_df.sort_values("timestamp_readable").groupby("city").agg({
    'temperature': 'mean',
    'humidity': 'mean',
    'wind_speed': 'max',
    'visibility': 'mean',
    'condition_main': 'last',
    'cloudiness': 'mean',
    'latitude': 'last',
    'longitude': 'last',
    'country': 'last',
    'timestamp_readable': 'last'
}).reset_index()

beach_cities = ["Rio de Janeiro", "San Francisco", "Barcelona", "Puerto Princesa",
                "Dubai", "Cape Town", "Sydney", "Bali", "Mal\u00e9"]
excluded_exploration = ["Mal\u00e9", "Bali"]

def score_outdoor_exploration(row):
    if row["city"] in excluded_exploration or row["condition_main"] in ["Rain", "Thunderstorm", "Snow"]:
        return 0.0
    return round(
        (0.5 if 17 <= row["temperature"] <= 24 else 0) +
        (0.1 if row["humidity"] < 60 else 0) +
        (0.15 if row["wind_speed"] <= 5 else 0) +
        (0.25 if row["condition_main"] in ["Clear", "Clouds"] else 0), 3)

def score_city_leisure(row):
    return round(
        (0.4 if 18 <= row["temperature"] <= 28 else 0) +
        (0.3 if row["visibility"] > 8000 else 0) +
        (0.3 if row["condition_main"] in ["Clear", "Clouds"] else 0), 3)

def score_beach_relaxation(row):
    if row["city"] not in beach_cities:
        return None
    score = (
        (0.5 if 27 <= row["temperature"] <= 32 else 0) +
        (0.2 if row["wind_speed"] < 4.5 else 0) +
        (0.3 if row["condition_main"] == "Clear" else 0)
    )
    if row["condition_main"] in ["Rain", "Thunderstorm"]:
        return min(score, 0.2)
    return round(score, 3)

agg_df["outdoor_score"] = agg_df.apply(score_outdoor_exploration, axis=1)
agg_df["leisure_score"] = agg_df.apply(score_city_leisure, axis=1)
agg_df["beach_score"] = agg_df.apply(score_beach_relaxation, axis=1)

def top_percent(df, col):
    top_scores = df[col].dropna().drop_duplicates().nlargest(1).tolist()
    top_df = df[df[col].isin(top_scores)].copy()
    top_df[col + "_percent"] = (top_df[col] * 100).astype(int).astype(str) + "%"
    return top_df[["city", "temperature", "humidity", "wind_speed", col + "_percent"]] \
             .rename(columns={col + "_percent": "score"}) \
             .sort_values("score", ascending=False).reset_index(drop=True)

outdoor_display = top_percent(agg_df, "outdoor_score")
leisure_display = top_percent(agg_df, "leisure_score")
beach_display = top_percent(agg_df, "beach_score")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("### 🥾 1. Outdoor Exploration")
    st.markdown("*hiking, walking tours, parks*", unsafe_allow_html=True)
    st.dataframe(outdoor_display, use_container_width=True)

with col2:
    st.markdown("### 🏙️ 2. City Leisure")
    st.markdown("*sightseeing, open-air cafes, casual strolls*", unsafe_allow_html=True)
    st.dataframe(leisure_display, use_container_width=True)

with col3:
    st.markdown("### 🏖️ Beach & Water Relaxation")
    st.markdown("*lounging, light swimming, beachfront dining*", unsafe_allow_html=True)
    st.dataframe(beach_display, use_container_width=True)

st.caption("\U0001F4C5 Updated every 60 seconds with the latest weather streaming data.")

# --- Temperature Trends Across Selected Cities ---
st.markdown("## 🌡️ Temperature Trends Across Selected Cities")

# Multiselect city picker
selected_cities = st.multiselect(
    "Compare temperature trends across cities:",
    pandas_df["city"].unique(),
    default=pandas_df["city"].unique()[:3]
)

# Filter dataframe for selected cities
filtered_df = pandas_df[pandas_df["city"].isin(selected_cities)].sort_values("timestamp_readable")

if not filtered_df.empty:
    # --- Line chart: Temperature over time ---
    temp_trend_chart = alt.Chart(filtered_df).mark_line().encode(
        x=alt.X("timestamp_readable:T", title="Time"),
        y=alt.Y("temperature:Q", title="Temperature (°C)"),
        color="city:N",
        tooltip=["city", "timestamp_readable", "temperature"]
    ).properties(title="Temperature Comparison", height=300)

    st.altair_chart(temp_trend_chart, use_container_width=True)

    # --- Two charts side by side ---
    col1, col2 = st.columns(2)

    # --- Bar chart: temperature comparison ---
    with col1:
        st.markdown("### Temperature Across Selected Cities")
        fig1, ax1 = plt.subplots()
        sns.barplot(data=filtered_df, x="city", y="temperature", ax=ax1)
        ax1.set_ylabel("Temperature (°C)", fontsize=11)
        ax1.set_xlabel("")
        ax1.set_title("Temperature by City", fontsize=13)
        ax1.tick_params(axis='x', labelsize=10)
        st.pyplot(fig1)

    # --- Scatter plot: wind vs humidity ---
    with col2:
        st.markdown("### Wind Speed vs Humidity")
        fig2, ax2 = plt.subplots()
        # Loop over cities to plot each with different color and label
        for city in filtered_df["city"].unique():
            city_data = filtered_df[filtered_df["city"] == city]
            ax2.scatter(
                city_data["wind_speed"], 
                city_data["humidity"], 
                label=city,
                alpha=0.7,
                s=60  # marker size
            )

        ax2.set_xlabel("Wind Speed (m/s)", fontsize=11)
        ax2.set_ylabel("Humidity (%)", fontsize=11)
        ax2.set_title("Wind vs Humidity by City", fontsize=13)
        ax2.tick_params(labelsize=10)
        ax2.legend(title="City", fontsize=8, title_fontsize=9, loc="upper right")
        st.pyplot(fig2)

else:
    st.warning("Please select at least one city with available data.")

# City selection for detailed climate trend
latest_city = st.selectbox("View detailed weather log for a city:", pandas_df["city"].unique())
city_data = pandas_df[pandas_df["city"] == latest_city].sort_values("timestamp_readable")

if not city_data.empty:
    st.markdown(f"### \U0001F4CB Latest Weather Records for {latest_city}")
    st.dataframe(city_data[["timestamp_readable", "temperature", "humidity", "wind_speed"]].tail(20), use_container_width=True)
