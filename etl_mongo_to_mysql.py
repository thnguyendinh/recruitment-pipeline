#!/usr/bin/env python3
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, hour, date_format, avg, sum, count, when, lit, max as _max
import os
import sys

MONGO_URI = "mongodb://admin:admin123@localhost:27017/recruitment.tracking?authSource=admin"
MYSQL_URL = "jdbc:mysql://localhost:3306/warehouse?useSSL=false"
MYSQL_USER = "root"
MYSQL_PWD = "example"
LAST_TS_FILE = "/home/ubuntu/last_timestamp.txt"

spark = SparkSession.builder \
    .appName("ETL MongoDB to MySQL") \
    .config("spark.jars", "/home/ubuntu/recruitment-pipeline/jars/mongo-spark-connector_2.12-10.4.0.jar") \
    .config("spark.jars.packages", "com.mysql:mysql-connector-j:8.0.30") \
    .config("spark.mongodb.read.connection.uri", MONGO_URI) \
    .getOrCreate()

def get_last_ts():
    try:
        with open(LAST_TS_FILE, 'r') as f:
            return f.read().strip()
    except:
        return "1970-01-01 00:00:00"

def save_last_ts(ts):
    with open(LAST_TS_FILE, 'w') as f:
        f.write(ts)

last_ts = get_last_ts()
print(f"[INFO] Last processed timestamp: {last_ts}")

raw_df = spark.read.format("mongodb") \
    .option("uri", MONGO_URI) \
    .option("database", "recruitment") \
    .option("collection", "tracking") \
    .load() \
    .filter(col("ts") > last_ts) \
    .select("ts", "job_id", "custom_track", "bid", "campaign_id", "group_id", "publisher_id") \
    .filter(col("job_id").isNotNull()) \
    .filter(col("custom_track").isNotNull())

if raw_df.count() == 0:
    print("No new data. Exiting.")
    spark.stop()
    sys.exit(0)

df = raw_df.withColumn("date", date_format("ts", "yyyy-MM-dd").cast("date")) \
           .withColumn("hour", hour("ts"))

agg_df = df.groupBy("date", "hour", "job_id", "campaign_id", "group_id", "publisher_id") \
    .agg(
        count(when(col("custom_track") == "click", 1)).alias("clicks"),
        count(when(col("custom_track") == "conversion", 1)).alias("conversions"),
        count(when(col("custom_track") == "qualified", 1)).alias("qualified"),
        count(when(col("custom_track") == "unqualified", 1)).alias("disqualified"),
        round(avg("bid"), 2).alias("bid_set"),
        round(sum("bid"), 2).alias("spend_hour")
    ) \
    .withColumn("sources", lit("MongoDB"))

agg_df.write.format("jdbc") \
    .option("url", MYSQL_URL) \
    .option("driver", "com.mysql.cj.jdbc.Driver") \
    .option("dbtable", "events") \
    .option("user", MYSQL_USER) \
    .option("password", MYSQL_PWD) \
    .mode("append") \
    .save()

max_ts = raw_df.agg(_max("ts")).collect()[0][0]
if max_ts:
    save_last_ts(str(max_ts))
    print(f"[INFO] Updated last timestamp to {max_ts}")

spark.stop()
