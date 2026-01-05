# call_events_stream.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, window
from pyspark.sql.types import StructType, StringType, IntegerType, TimestampType

spark = SparkSession.builder \
    .appName("CallEventsStream") \
    .getOrCreate()

schema = StructType() \
    .add("ts", StringType()) \
    .add("event", StringType()) \
    .add("provider_id", StringType()) \
    .add("provider_name", StringType())

df = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "call_events") \
    .option("startingOffsets", "latest") \
    .load()

json_df = df.selectExpr("CAST(value AS STRING) as json_str") \
    .select(from_json(col("json_str"), schema).alias("data")) \
    .select("data.*")

# NOTE: ts is currently string ISO; for demo we won't parse it. Use processing-time window
agg = json_df.groupBy(window(col("ts"), "30 seconds"), col("provider_name"), col("event")) \
    .count().orderBy("window")

query = agg.writeStream.format("console").outputMode("complete").option("truncate","false").start()
query.awaitTermination()
