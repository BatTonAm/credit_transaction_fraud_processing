from datetime import datetime, timezone

STALL_THRESHOLD_MINUTES = 30

result = spark.sql("""
    SELECT MAX(transaction_time) AS last_ingested
    FROM credit_transactions.gold.scored_transactions
""").collect()[0]

last_ingested = result["last_ingested"]

if last_ingested is None:
    raise Exception("No rows exist in scored_transactions — pipeline may have never started.")

now = datetime.now(timezone.utc)
age_minutes = (now - last_ingested.replace(tzinfo=timezone.utc)).total_seconds() / 60

print(f"Last ingested row: {last_ingested} ({age_minutes:.1f} minutes ago)")

if age_minutes > STALL_THRESHOLD_MINUTES:
    raise Exception(
        f"STALL DETECTED: no new data in scored_transactions for {age_minutes:.1f} minutes "
        f"(threshold: {STALL_THRESHOLD_MINUTES}). Streaming pipeline may have silently stopped."
    )

print("Pipeline is healthy — data is fresh.")