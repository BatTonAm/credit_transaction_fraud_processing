from pyspark.sql.functions import col
import mlflow
from pyspark import pipelines as dp
@dp.table(
    name="credit_transactions.gold.scored_transactions",
    comment="per transaction fraud predictions from the registered model",
    partition_cols=["transaction_date"],
    table_properties={
        "delta.autoOptimize.optimizeWrite": "true",
        "delta.autoOptimize.autoCompact": "true",
    }
)
def scored_transactions():
    model_udf = mlflow.pyfunc.spark_udf(
        spark,
        model_uri="models:/credit_transactions.gold.fraud_model/1"
    )

    feature_cols = [
        "transaction_amount", "transaction_type", "payment_method", "city",
        "country", "ip_country", "device_type", "operating_system", "browser",
        "card_type", "card_present", "international_transaction",
        "distance_from_home", "merchant_risk_level", "country_mismatch",
        "transaction_hour", "transaction_dayofweek",
    ]

    df = dp.read_stream("credit_transactions.silver.credit_transactions")

    scored_trans= (df
        .withColumn("fraud_prediction", model_udf(*[col(c) for c in feature_cols]))
        .select(
            "transaction_id", "customer_id", "merchant_id", "transaction_time", "transaction_date",
            *feature_cols,
            "fraud_prediction",
        )
    )
    return scored_trans