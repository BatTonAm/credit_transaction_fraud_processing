from pyspark.sql.functions import col, round, datediff, current_date, when
from pyspark import pipelines as dp
from pyspark.sql.dataframe import DataFrame

@dp.table(
    name="credit_transactions.gold.dim_customer",
    comment="dim_customer load")
def load_cust_gold()-> DataFrame:
    silver_cust=dp.read('credit_transactions.silver.customer')
    customer_age = round(datediff(current_date(), col('customer_dob')) / 365).cast("int")
    account_tenure_years = round(datediff(current_date(), col('customer_signup_date')) / 365).cast("int")
    transform_cols={
        'account_tenure_years': account_tenure_years,
        'customer_age': customer_age,
        'age_bracket': (when(customer_age < 26, "18-25")
                        .when(customer_age < 36, "26-35")
                        .when(customer_age < 51, "36-50")
                        .when(customer_age < 66, "51-65")
                        .otherwise("65+")),
        'tenure_bracket': (when(account_tenure_years < 1, "New (<1yr)")
                            .when(account_tenure_years < 3, "1-3yrs")
                            .when(account_tenure_years < 5, "3-5yrs")
                            .otherwise("5+yrs"))
    }
    gold_cust=(silver_cust.withColumns(transform_cols)
               .select(
                   "customer_id",
                   "customer_dob",
                   "customer_age",
                   "age_bracket",
                   "customer_signup_date",
                   "account_tenure_years",
                   "tenure_bracket",
                   "customer_home_city",
                   "customer_home_country",
                   "customer_segment",
                   "annual_income",
                   round(col("expected_monthly_spend"), 2).cast("double").alias("expected_monthly_spend"),
                   "customer_credit_score"
               ))
    return gold_cust