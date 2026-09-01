from pyspark.sql.functions import col, window
from pyspark.sql.dataframe import DataFrame
from pyspark import pipelines as dp

@dp.table(
    name="credit_transactions.gold.customer_velocity_alerts",
    comment="flags customers with high transaction frequency in short time windows",
    table_properties={
        "delta.autoOptimize.optimizeWrite": "true",
        "delta.autoOptimize.autoCompact": "true",
    }
)
def customer_velocity_alerts() -> DataFrame:
    df = dp.read_stream("credit_transactions.silver.credit_transactions")
    veloc_alert= (df
        .withWatermark("transaction_time", "1 minute")
        .groupBy(
            window(col("transaction_time"), "1 minute"),
            col("customer_id")
        )
        .count()
        .withColumnRenamed("count", "transaction_count")
        .withColumn("high_frequency_flag", col("transaction_count") >= 10)
        .select(
            col("window.start").alias("window_start"),
            col("window.end").alias("window_end"),
            "customer_id",
            "transaction_count",
            "high_frequency_flag",
        ).filter(col("high_frequency_flag")=="true")
    )
    return veloc_alert