from pyspark.sql.functions import col, round, datediff, current_date, when
from pyspark import pipelines as dp
from pyspark.sql.dataframe import DataFrame

@dp.table(
    name="credit_transactions.gold.dim_merchant")
def dim_merchant() -> DataFrame:
    silver_merch=dp.read("credit_transactions.silver.merchant")
    transform_cols={
        "operation_years": round(datediff(current_date(), col("merchant_established_date"))/365).cast("int"),
        "channel": (when(col("merchant_online_flag")==1, "online").otherwise("in-store")),
        "business_year_bracket": (when(col("operation_years") < 2, "New")
                                  .when(col("operation_years") < 10, "Established")
                                  .otherwise("Mature"))
    }
    gold_merch=(
        silver_merch.withColumns(transform_cols)
        .select(
            "merchant_id",
            "merchant_name",
            "merchant_mcc_code",
            "merchant_established_date",
            "merchant_category",
            "merchant_size",
            "merchant_country",
            "merchant_city",
            "merchant_risk_level",
            "channel",
            "operation_years",
            "business_year_bracket"
        )
    )
    return gold_merch