from delta.tables import DeltaTable

RECONCILIATION_WINDOW_DAYS = 7

fraud_metrics_df = spark.sql(f"""
    SELECT
        DATE(transaction_time) AS metric_date,
        COUNT(*) AS total_transactions,
        SUM(fraud_prediction) AS fraud_count,
        AVG(fraud_prediction) AS fraud_rate,
        SUM(CASE WHEN fraud_prediction = 1 THEN transaction_amount ELSE 0 END) AS fraud_amount_total,
        SUM(CASE WHEN transaction_type = 'Online' THEN fraud_prediction ELSE 0 END) AS fraud_count_online,
        SUM(CASE WHEN transaction_type = 'POS' THEN fraud_prediction ELSE 0 END) AS fraud_count_pos,
        SUM(CASE WHEN transaction_type = 'ATM' THEN fraud_prediction ELSE 0 END) AS fraud_count_atm
    FROM credit_transactions.gold.scored_transactions
    WHERE transaction_time >= current_date() - INTERVAL {RECONCILIATION_WINDOW_DAYS} DAYS
    GROUP BY DATE(transaction_time)
""")

target = DeltaTable.forName(spark, "credit_transactions.gold.daily_fraud_metrics")
(target.alias("t")
    .merge(fraud_metrics_df.alias("s"), "t.metric_date = s.metric_date")
    .whenMatchedUpdateAll()
    .whenNotMatchedInsertAll()
    .execute())