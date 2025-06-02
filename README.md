# Real-Time Weather Intelligence System for Tourism Operations and Strategy

A real-time streaming system that transforms weather data into actionable insights for the tourism industry.

---

## Overview

This project delivers a real-time weather intelligence platform tailored for travel agencies, tour operators, and destination marketers.  
It merges live weather streaming with smart analytics to power:

- Discomfort and safety alerts  
- Activity suitability recommendations  
- Strategic dashboards for tourism decision-making  
- Historical insights to guide promotions and planning

Built with Kafka, Spark, Pandas, Plotly, and Folium — the system processes weather from 30+ cities, turning raw data into rich, business-ready intelligence.

---

## Key Features

### Real-Time Weather Streaming  
- Streams weather from the OpenWeatherMap API using Kafka  
- Spark Structured Streaming parses and stores the data in `.parquet` format  
- Data updated every few seconds for live monitoring and decision-making

### Live Weather Dashboard  
- Interactive map with weather markers per city  
- Color-coded alerts for storms, clouds, or clear skies  
- Real-time visibility for operators across global locations

### Activity Recommendation Engine  
- Scores cities for:
  - Outdoor Exploration  
  - City Leisure  
  - Beach & Water Relaxation  
- Based on live temperature, humidity, wind, and visibility  
- HTML dashboard displays top-suited cities per activity

### Discomfort & Risk Alerts  
- Flags cities with hot, cold, humid, or severe conditions  
- Uses simplified tagging logic for clear decision support  
- Dynamic bar charts and alert tables inform action

### Historical Intelligence  
- Radar charts, volatility plots, time series, and heatmaps  
- Reveal stability, risk, and promotional opportunity across cities  
- Enables data-driven planning and marketing alignment

---

## 🚀 How to Run

### 1. Clone the Repository
```bash
git clone https://github.com/ngocsgh25/Real-time-analytics-project.git
cd Real-time-analytics-project
```

### 2. Start Kafka and Zookeeper (via Docker)
Make sure Docker is installed and running. Use the provided `docker-compose.yml` file:
```bash
docker-compose up -d
```

### 3. Create Kafka Topic for Streaming
After Kafka and Zookeeper are running:
```bash
docker exec real-time-analytics-project-kafka-1 \
  /usr/bin/kafka-topics --create \
  --topic weather-stream \
  --bootstrap-server localhost:9092 \
  --replication-factor 1 \
  --partitions 1
```

### 4. Run the Kafka Weather Producer
Start the producer that fetches weather data from OpenWeatherMap and sends it to Kafka:
```bash
python producer.py
```

### 5. Start Spark Structured Streaming Consumer
Read from Kafka and save structured weather data to `.parquet`:
```bash
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 consumer.py
```

### 6. Launch Dashboard Notebook
```bash
jupyter notebook
```


### 7. Sample Output: Dashboard Visualization

The Jupyter notebook includes multiple dashboards. Below is an example showing how the **Live Weather Map** is created from data within a 15-minute tumbling window.

```python
from datetime import timedelta
import folium
from folium.plugins import MarkerCluster

# Convert timestamp to datetime
pandas_df['timestamp_readable'] = pd.to_datetime(pandas_df['timestamp_readable'])

# Define tumbling window: last full 15-minute interval
now = pandas_df['timestamp_readable'].max()
aligned_now = now - timedelta(
    minutes=now.minute % 15,
    seconds=now.second,
    microseconds=now.microsecond
)
window_start = aligned_now - timedelta(minutes=15)

# Filter records
tumbling_df = pandas_df[
    (pandas_df['timestamp_readable'] >= window_start) &
    (pandas_df['timestamp_readable'] < aligned_now)
].copy()

# Select most recent per city
latest_per_city = tumbling_df.sort_values("timestamp_readable", ascending=False).drop_duplicates("city")

# Plot using Folium
weather_map = folium.Map(location=[20, 0], zoom_start=2)
marker_cluster = MarkerCluster().add_to(weather_map)

for _, row in latest_per_city.iterrows():
    condition = row["condition_main"]
    popup_text = f"<b>{row['city']}</b><br>Temp: {row['temperature']}°C<br>Weather: {row['condition_desc']}"

    if condition in ["Rain", "Thunderstorm", "Snow"]:
        color = "red"
    elif condition in ["Clouds", "Mist"]:
        color = "orange"
    else:
        color = "green"

    folium.CircleMarker(
        location=[row["latitude"], row["longitude"]],
        radius=6,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.7,
        popup=popup_text
    ).add_to(marker_cluster)

# Save the map
weather_map.save("weather_dashboard.html")
```

This map helps teams visually monitor real-time conditions across destinations and quickly assess where weather may disrupt or enable tourism activities.

Open the main Jupyter Notebook to run visualizations and analytics:
```bash
jupyter notebook
```

> You can now explore the dashboards: live map, alerts, activity recommendations, and historical insights.
---

## Architecture

> Architecture:  
> OpenWeatherMap API → Kafka Producer → Kafka Topic → Spark Structured Streaming → Parquet Storage → Pandas Analytics → Jupyter Dashboard

---

## Technologies Used

| Component         | Technology                    |
|------------------|-------------------------------|
| Data Source       | OpenWeatherMap API            |
| Streaming         | Apache Kafka + Spark Streaming|
| Storage           | Parquet (local)               |
| Processing        | Pandas, PySpark               |
| Visualization     | Plotly, Folium, Matplotlib    |
| Interface         | Jupyter Notebook (static preview) |

---

## Future Extensions

- Streamlit/Dash integration for live dashboards  
- Personalized recommendations based on user profiles  
- Weather-driven promotion engine for hospitality apps  
- Predictive alerting via ML models

---

## Contributors

- Joanna Marie Corpuz — 131120  
- Thi Minh Ngoc Dao — 131112  
- Li Xinyi — 131082  

---

"Weather data becomes a strategic asset — when designed for the people who need it most."
