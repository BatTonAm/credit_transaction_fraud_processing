from pyspark.sql.functions import col
from pyspark import pipelines as dp
from pyspark.sql.dataframe import DataFrame

@dp.table(
    name="credit_transactions.silver.customer",
    comment="standardized customer information"
)
@dp.expect_or_drop("valid_customer_id", "customer_id IS NOT NULL")
def customer_silver() -> DataFrame:
    cust=spark.read.table("credit_transactions.bronze.customer")
    transform_cols={
    "expected_monthly_spend": (col("annual_income")/12).cast("double")}

    tran_cust=cust.withColumns(transform_cols).select(
                "customer_id", 
                col("customer_dob").cast("date"),
                col("customer_signup_date").cast("date"),
                "customer_home_city",   
                "customer_home_country",
                "customer_segment",
                col("annual_income").cast("double"),
                "expected_monthly_spend",
                col("customer_credit_score").cast("short"))
    return tran_cust