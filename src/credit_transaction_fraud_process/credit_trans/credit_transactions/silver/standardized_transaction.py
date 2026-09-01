from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType
from pyspark.sql.functions import col, from_json, to_timestamp, hour, weekday, broadcast, to_date
from pyspark.sql.dataframe import DataFrame
from pyspark import pipelines as dp

@dp.table(
    name="credit_transactions.silver.credit_transactions",
    comment="standardized credit transactions",
    partition_cols=["transaction_date"],
    table_properties={
        "delta.autoOptimize.optimizeWrite": "true",
        "delta.autoOptimize.autoCompact": "true"})
@dp.expect("merchant data", "merchant_risk_level IS NOT NULL")
@dp.expect_or_drop("valid amount", "transaction_amount IS NOT NULL AND transaction_amount > 0")
@dp.expect_or_drop("valid_merchant_id", "merchant_id IS NOT NULL")
@dp.expect_or_drop("valid_customer_id", "customer_id IS NOT NULL")
@dp.expect_or_drop("valid_transaction_id", "transaction_id IS NOT NULL")
def silver_credit_transactions() -> DataFrame:
    bronze_df=dp.read_stream('credit_transactions.bronze.raw_transaction')
    merchant=spark.read.table('credit_transactions.silver.merchant').select("merchant_id", "merchant_risk_level").dropDuplicates(["merchant_id"])
    transaction_schema = StructType([
        StructField("transaction_id", StringType()),
        StructField("customer_id", StringType()),
        StructField("merchant_id", StringType()),
        StructField("transaction_time", StringType()),
        StructField("transaction_amount", DoubleType()),
        StructField("transaction_type", StringType()),
        StructField("payment_method", StringType()),
        StructField("city", StringType()),
        StructField("country", StringType()),
        StructField("ip_country", StringType()),
        StructField("device_type", StringType()),
        StructField("operating_system", StringType()),
        StructField("browser", StringType()),
        StructField("card_type", StringType()),
        StructField("card_present", IntegerType()),
        StructField("international_transaction", IntegerType()),
        StructField("distance_from_home", DoubleType()),
    ])

    transform_cols={
    "transaction_time": to_timestamp("transaction_time"),
    "transaction_date": to_date(col("transaction_time")),
    "transaction_hour": hour(col("transaction_time")),
    "transaction_dayofweek": weekday(col("transaction_time")),
    "country_mismatch": (col("ip_country")!=col("country")).cast("int")
    }

    silver_df=(bronze_df.select(
    from_json(col("value"), transaction_schema).alias("data"),
    col("topic").alias("kafka_topic"),
    col("partition").alias("kafka_partition"),
    col("offset").alias("kafka_offset"),
    col("timestamp").alias("kafka_timestamp"),
    col("ingestion_timestamp")
    ).select(
    col("data.*"),
    col("kafka_topic"),
    col("kafka_partition"),
    col("kafka_offset"),
    col("kafka_timestamp"),
    col("ingestion_timestamp")
    ).withColumns(transform_cols)
    .withWatermark("transaction_time", "10 minutes")
    .dropDuplicates(["transaction_id"]))
    silver_agg=silver_df.join(broadcast(merchant), "merchant_id", "left_outer")
    return silver_agg