import os
os.environ['JAVA_HOME'] = '/opt/java/openjdk'
os.environ['SPARK_HOME'] = '/opt/spark'

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, to_timestamp, to_date, hour,
    avg, sum as spark_sum, count,
    round as spark_round, lit, current_timestamp
)
from pyspark.sql.types import DoubleType, IntegerType

spark = (
    SparkSession.builder
    .appName("RecruitmentETL")
    .master("local[*]")
    .config("spark.driver.memory", "512m")
    .config("spark.sql.shuffle.partitions", "2")
    .config("spark.mongodb.read.connection.uri",
            "mongodb://admin:admin123@mongodb:27017/recruitment.tracking?authSource=admin")
    .config("spark.jars",
            "/opt/spark/extra-jars/mongo-spark-connector_2.12-10.4.0.jar,"
            "/opt/spark/extra-jars/mysql-connector-j-8.0.33.jar,"
            "/opt/spark/extra-jars/bson-4.11.1.jar,"
            "/opt/spark/extra-jars/mongodb-driver-core-4.11.1.jar,"
            "/opt/spark/extra-jars/mongodb-driver-sync-4.11.1.jar")
    .getOrCreate()
)
spark.sparkContext.setLogLevel("WARN")
print("✅ Spark OK")

print("📥 Reading from MongoDB...")
raw = (
    spark.read
    .format("mongodb")
    .option("database", "recruitment")
    .option("collection", "tracking")
    .load()
)
print(f"   Total records: {raw.count()}")

print("⚙️  Transforming...")
data = (
    raw
    .select("job_id","custom_track","bid","campaign_id","group_id","publisher_id","ts")
    .filter(col("job_id").isNotNull())
    .filter(col("custom_track").isNotNull())
    .withColumn("ts",  to_timestamp(col("ts"), "yyyy-MM-dd HH:mm:ss.SSS"))
    .withColumn("date", to_date(col("ts")))
    .withColumn("hour", hour(col("ts")))
    .filter(col("date").isNotNull())
    .withColumn("bid",          col("bid").cast(DoubleType()))
    .withColumn("job_id",       col("job_id").cast(IntegerType()))
    .withColumn("campaign_id",  col("campaign_id").cast(IntegerType()))
    .withColumn("group_id",     col("group_id").cast(IntegerType()))
    .withColumn("publisher_id", col("publisher_id").cast(IntegerType()))
)
data.cache()

KEYS = ["date","hour","job_id","publisher_id","campaign_id","group_id"]

click_df = (
    data.filter(col("custom_track")=="click")
    .groupBy(*KEYS)
    .agg(
        spark_round(avg("bid"),2).alias("bid_set"),
        spark_round(spark_sum("bid"),2).alias("spend_hour"),
        count("*").alias("clicks")
    )
)
conversion_df = (
    data.filter(col("custom_track")=="conversion")
    .groupBy(*KEYS).agg(count("*").alias("conversions"))
)
qualified_df = (
    data.filter(col("custom_track")=="qualified")
    .groupBy(*KEYS).agg(count("*").alias("qualified"))
)
unqualified_df = (
    data.filter(col("custom_track")=="unqualified")
    .groupBy(*KEYS).agg(count("*").alias("disqualified"))
)

result = (
    click_df
    .join(conversion_df,  KEYS, "full")
    .join(qualified_df,   KEYS, "full")
    .join(unqualified_df, KEYS, "full")
    .fillna(0, subset=["clicks","conversions","qualified","disqualified","bid_set","spend_hour"])
    .withColumn("sources",   lit("MongoDB"))
    .withColumn("load_time", current_timestamp())
)

print(f"   Output rows: {result.count()}")
result.show(5, truncate=False)

print("📤 Writing to MySQL...")
jdbc_url = "jdbc:mysql://mysql:3306/warehouse?useSSL=false&allowPublicKeyRetrieval=true"
(
    result.write
    .format("jdbc")
    .option("url",      jdbc_url)
    .option("driver",   "com.mysql.cj.jdbc.Driver")
    .option("dbtable",  "events")
    .option("user",     "root")
    .option("password", "example")
    .mode("append")
    .save()
)
print("✅ ETL hoàn thành!")
spark.stop()
