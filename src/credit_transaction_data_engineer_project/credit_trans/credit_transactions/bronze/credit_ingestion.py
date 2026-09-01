from pyspark.sql.functions import col, current_timestamp
from pyspark import pipelines as dp
from pyspark.sql.dataframe import DataFrame
@dp.table(
    name="credit_transactions.bronze.raw_transaction",
    comment="raw transaction data from Kafka",
    table_properties= {
        "delta.autoOptimize.optimizeWrite": "true",
        "delta.autoOptimize.autoCompact": "true"
    }  
)
def transaction_bronze() -> DataFrame:
    api_key = dbutils.secrets.get("azurekeyvault", "kafkaapi")
    api_secret = dbutils.secrets.get("azurekeyvault", "kafkasecret")
    jaas_config = f'kafkashaded.org.apache.kafka.common.security.plain.PlainLoginModule required username="{api_key}" password="{api_secret}";' 
    credit_data=(spark.readStream.format("kafka")
             .option("kafka.bootstrap.servers", dbutils.secrets.get("azurekeyvault", "kafkabootstrap"))
             .option("kafka.security.protocol", "SASL_SSL")
             .option("subscribe", "credit_card_transactions")
             .option("kafka.sasl.mechanism","PLAIN")
             .option("kafka.sasl.jaas.config", jaas_config)
             .option("startingOffsets", "earliest")
             .load())
    parsed_data=credit_data.select(
    col("key").cast("string"),
    col("value").cast("string"),
    col("topic"),
    col("partition"),
    col("offset"),
    col("timestamp"),
    col("timestampType"),
    current_timestamp().alias("ingestion_timestamp"))

    return parsed_data

