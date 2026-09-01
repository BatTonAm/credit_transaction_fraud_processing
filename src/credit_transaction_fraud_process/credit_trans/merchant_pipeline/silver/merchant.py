from pyspark import pipelines as dp
from pyspark.sql.functions import col, trim
from pyspark.sql.dataframe import DataFrame

@dp.table(
    name="credit_transactions.silver.merchant",
    comment="standardized merchant data"
)
@dp.expect_or_drop("valid size", "merchant_size IN ('Small', 'Medium', 'Enterprise')")
@dp.expect_or_drop("valid risk level", "merchant_risk_level IN ('High', 'Medium', 'Low')")
@dp.expect_or_drop("valid merchant id", "merchant_id IS NOT NULL")
def load_merchant_silver() -> DataFrame:
    merch=spark.read.table(
    "credit_transactions.bronze.merchants")
    trans_merch=merch.select(
        "merchant_id",
        trim(col("merchant_name")).alias("merchant_name"),
        "merchant_mcc_code",
        col("merchant_established_date").cast("date"),
        "merchant_category",
        "merchant_size",
        "merchant_country",
        "merchant_city",
        "merchant_risk_level",
        "merchant_online_flag")
    return trans_merch