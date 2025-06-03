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

### Discomfort & Risk Alerts  
- Flags cities with hot, cold, humid, or severe conditions  
- Uses simplified tagging logic for clear decision support  
- Dynamic bar charts and alert tables inform action
- Cities with “Severe Weather” are filtered and highlighted separately from heat/cold/humidity tags

### Activity Recommendation Engine  
- Scores cities for:
  - Outdoor Exploration  
  - City Leisure  
  - Beach & Water Relaxation  
- Based on live temperature, humidity, wind, and visibility  
- Streamlit dashboard shows top-scoring cities per activity (Outdoor, Leisure, Beach)
- Uses live 30-minute sliding window and scoring based on weather rules

### Historical Intelligence  
- Radar charts, volatility plots, time series, and heatmaps  
- Reveal stability, risk, and promotional opportunity across cities  
- Enables data-driven planning and marketing alignment

---
## How to Run

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

### 6. Launch Dashboards

#### Run Streamlit Dashboards (Live Map + Activity Recommendations)
```bash
streamlit run live_weather_map.py
streamlit run activity_recommendations.py
```

#### Or launch Jupyter Notebook for alerts and historical analytics
```bash
jupyter notebook
```


### 7. Sample Output: Dashboard Visualization
Then, open the main notebook file to explore **visualizations** and perform **data analytics**.
> ✅ You can now explore multiple dashboards, including the live weather map, alert system, activity suggestions, and historical weather insights.
> Dashboards & Insights:
> - Dashboard 1: Live Weather Map  
> - Dashboard 2: Activity Recommendations Based on Weather  
> - Dashboard 3: Discomfort Detection & Alerts  
> - Historical Weather Data Exploration (Supporting RTA Strategy & Forecasting)
>   - Chart 1: Multi-dimensional Radar Chart for City Weather Comparison
>   - Chart 2: Time Series Weather Trends and Seasonal Patterns
>   - Chart 3: Dynamic Weather Condition Heatmap by Hour and City
>   - Chart 4: Weather Volatility and Risk Assessment Scatter Plot
>   - Chart 5: Interactive Business Intelligence Dashboard for Tourism Marketing
---

## Architecture

> Architecture:  
> OpenWeatherMap API → Kafka Producer → Kafka Topic → Spark Structured Streaming → Parquet Storage → Pandas Analytics → Streamlit & Jupyter Dashboards

---

## Technologies Used

| Component         | Technology                    |
|------------------|-------------------------------|
| Data Source       | OpenWeatherMap API            |
| Streaming         | Apache Kafka + Spark Streaming|
| Storage           | Parquet (local)               |
| Processing        | Pandas, PySpark               |
| Visualization     | Plotly, Folium, Matplotlib    |
| Interface         | Streamlit (real-time dashboards), Jupyter Notebook (supporting modules) |

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
