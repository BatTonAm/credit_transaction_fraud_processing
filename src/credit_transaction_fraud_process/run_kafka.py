from .kafka.reference_data import ensure_reference_data
from .kafka.kafka_producer import produce_message, producer
from .kafka.transaction_generator import stream_transactions


def main() -> None:
    customers, merchants = ensure_reference_data()
    try:
        for txn in stream_transactions(customers, merchants, rate_per_sec=5):
            produce_message("credit_card_transactions", txn)
    finally:
        producer.flush()
