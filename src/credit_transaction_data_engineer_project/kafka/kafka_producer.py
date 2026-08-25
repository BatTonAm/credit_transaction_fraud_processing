import json
from confluent_kafka import Producer
from .config import load_settings

config=load_settings().to_kafka_config()
config["client.id"]="credit_transaction_producer"

producer=Producer(config)
def delivery_report(err, msg):
    if err is not None:
        print(f"Delivery failed for record {msg.key()}: {err}")
    else:
        print(f"Record {msg.key()} successfully produced to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")

def produce_message(topic, record: dict):
    key=record.get("customer_id","")
    value=json.dumps(record)
    producer.produce(
        topic,
        key=key.encode("utf-8"),
        value=value.encode("utf-8"),
        callback=delivery_report
    )
    producer.poll(0)

    