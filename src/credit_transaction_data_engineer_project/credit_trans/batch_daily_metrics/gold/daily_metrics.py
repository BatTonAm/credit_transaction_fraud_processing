from delta.tables import DeltaTable

RECONCILIATION_WINDOW_DAYS = 7

business_metrics_df = spark.sql(f"""
    SELECT
        DATE(transaction_time) AS metric_date,
        COUNT(*) AS total_transactions,
        SUM(transaction_amount) AS total_volume,
        AVG(transaction_amount) AS avg_ticket_size,
        COUNT(DISTINCT customer_id) AS active_customers,
        COUNT(DISTINCT merchant_id) AS active_merchants,
        SUM(CASE WHEN payment_method = 'Credit Card' THEN transaction_amount ELSE 0 END) AS volume_credit_card,
        SUM(CASE WHEN payment_method = 'Debit Card' THEN transaction_amount ELSE 0 END) AS volume_debit_card,
        SUM(CASE WHEN payment_method = 'Digital Wallet' THEN transaction_amount ELSE 0 END) AS volume_digital_wallet
    FROM credit_transactions.gold.scored_transactions
    WHERE transaction_time >= current_date() - INTERVAL {RECONCILIATION_WINDOW_DAYS} DAYS
    GROUP BY DATE(transaction_time)
""")

target = DeltaTable.forName(spark, "credit_transactions.gold.daily_business_metrics")
(target.alias("t")
    .merge(business_metrics_df.alias("s"), "t.metric_date = s.metric_date")
    .whenMatchedUpdateAll()
    .whenNotMatchedInsertAll()
    .execute())