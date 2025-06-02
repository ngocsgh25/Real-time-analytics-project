from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, from_unixtime
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType, ArrayType

# Create Spark session
spark = SparkSession.builder.appName("WeatherStreamingApp") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# Define schema
weather_schema = StructType([
    StructField("name", StringType()),
    StructField("dt", IntegerType()),
    StructField("visibility", IntegerType()),
    StructField("coord", StructType([
        StructField("lat", DoubleType()),
        StructField("lon", DoubleType())
    ])),
    StructField("main", StructType([
        StructField("temp", DoubleType()),
        StructField("feels_like", DoubleType()),
        StructField("humidity", IntegerType())
    ])),
    StructField("wind", StructType([
        StructField("speed", DoubleType())
    ])),
    StructField("weather", ArrayType(
        StructType([
            StructField("main", StringType()),
            StructField("description", StringType())
        ])
    )),
    StructField("sys", StructType([
        StructField("country", StringType())
    ])),
    StructField("clouds", StructType([
        StructField("all", IntegerType())
    ]))
])

# Read from Kafka
raw_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "weather-stream") \
    .option("startingOffsets", "latest") \
    .option("failOnDataLoss", "false") \
    .load()

# Parse JSON
json_df = raw_df.selectExpr("CAST(value AS STRING)")
parsed_df = json_df.select(from_json(col("value"), weather_schema).alias("data"))

# Extract fields
weather_df = parsed_df.select(
    col("data.name").alias("city"),
    col("data.coord.lat").alias("latitude"),
    col("data.coord.lon").alias("longitude"),
    col("data.main.temp").alias("temperature"),
    col("data.main.feels_like").alias("feels_like"),
    col("data.main.humidity").alias("humidity"),
    col("data.wind.speed").alias("wind_speed"),
    col("data.visibility").alias("visibility"),
    col("data.weather")[0]["main"].alias("condition_main"),
    col("data.weather")[0]["description"].alias("condition_desc"),
    col("data.sys.country").alias("country"),
    col("data.clouds.all").alias("cloudiness"),
    col("data.dt").alias("timestamp"),
    from_unixtime(col("data.dt")).alias("timestamp_readable")
)

spark.sparkContext.setLogLevel("ERROR")

# One stream to write to file (for Databricks later)
weather_df.writeStream \
    .format("parquet") \
    .option("path", "/tmp/stream_weather_output/") \
    .option("checkpointLocation", "/tmp/stream_weather_checkpoint/") \
    .outputMode("append") \
    .start()

# Another stream to print to console (for live debug view)
weather_df.writeStream \
    .format("console") \
    .option("truncate", "false") \
    .outputMode("append") \
    .start() \
    .awaitTermination()
