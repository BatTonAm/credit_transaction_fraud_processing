import json
from confluent_kafka import Consumer, KafkaException
from .config import load_settings

config=load_settings().to_kafka_config()
config["client.id"]="credit_transaction_consumer"
config["group.id"]="credit_transaction_processing_group"
config["auto.offset.reset"]="earliest"
config["enable.auto.commit"]=False

consumer=Consumer(config)
consumer.subscribe(["credit_card_transactions"])

try:
    while True:
        msg=consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            raise KafkaException(msg.error())
        print(f"Consumed record with key {msg.key().decode('utf-8')} and value {msg.value().decode('utf-8')} from topic {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")
        consumer.commit(msg)
except KafkaException as e:
    print(f"Kafka error: {e}")
except KeyboardInterrupt:
    print("Consumer interrupted by user")
finally:
    consumer.close()
    print("Consumer closed")

