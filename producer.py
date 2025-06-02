# producer.py

import json, time, requests
from kafka import KafkaProducer

API_KEY = "0e4055bdf6c6b9529514d47772c1cf24" # replace this with your API key
CITIES = [
    'New York', 'Los Angeles', 'Rio de Janeiro', 'San Francisco',
    'Mexico City', 'Toronto', 'London', 'Paris', 'Rome', 'Barcelona',
    'Krakow', 'Tokyo', 'Seoul', 'Singapore', 'Hanoi', 'Puerto Princesa',
    'Beijing', 'Delhi', 'Dubai', 'Istanbul', 'Cairo', 'Nairobi',
    'Cape Town', 'Sydney', 'Auckland', 'Warsaw', 'Bali',
    'Malé', 'Moscow', 'Oslo'
]

KAFKA_TOPIC = "weather-stream"
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

def fetch_weather(city):
    url = (
        f"http://api.openweathermap.org/data/2.5/weather?"
        f"q={city}&appid={API_KEY}&units=metric"
    )
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()

def stream_weather():
    while True:
        for city in CITIES:
            data = fetch_weather(city)
            if data:
                print(f"[SENT] {city} →", json.dumps(data))
                producer.send(KAFKA_TOPIC, value=data)
            time.sleep(10)  

if __name__ == "__main__":
    stream_weather()
