import random
import time
import uuid
from datetime import datetime, timezone
 
from .customer_generator import generate_customers
from .merchant_generator import generate_merchants, COUNTRY_CITIES, COUNTRIES
 
def clamp(x, lo, hi):
    return max(lo, min(x, hi))
 
MERCHANT_AVG_RANGE = {
    "Electronics": (150, 1200),
    "Entertainment": (10, 80),
    "Fashion": (30, 300),
    "Fuel": (20, 100),
    "Gaming": (5, 150),
    "Grocery": (10, 150),
    "Healthcare": (50, 500),
    "Luxury": (200, 5000),
    "Restaurants": (10, 120),
    "Travel": (100, 3000),
}
 
PAYMENT_OPTIONS = ["Credit Card", "Debit Card", "Digital Wallet"]
CARD_TYPE_OPTIONS = ["American Express", "Mastercard", "Visa"]
 
DEVICE_OS_MAP = {
    "Desktop": ["Windows", "MacOS", "Linux"],
    "Mobile": ["Android", "iOS"],
    "Tablet": ["Android", "iOS"],
}
OS_BROWSER_MAP = {
    "Windows": ["Chrome", "Edge", "Firefox"],
    "MacOS": ["Chrome", "Safari", "Firefox"],
    "Linux": ["Chrome", "Firefox"],
    "Android": ["Chrome", "Firefox"],
    "iOS": ["Safari", "Chrome"],
}
 
 
def make_transaction(customer, merchant):
    """Builds one complete transaction dict from an already-picked customer
    and merchant"""
 
    if merchant["merchant_online_flag"] == 1:
        transaction_type = random.choices(["Online", "POS", "ATM"], weights=[70, 25, 5])[0]
    else:
        transaction_type = random.choices(["Online", "POS", "ATM"], weights=[10, 75, 15])[0]
    card_present = 0 if transaction_type == "Online" else 1
 
    device_type = random.choice(list(DEVICE_OS_MAP.keys()))
    operating_system = random.choice(DEVICE_OS_MAP[device_type])
    browser = random.choice(OS_BROWSER_MAP[operating_system])
 
    home_country = customer["customer_home_country"]
    domestic = random.random() < 0.90
    country = home_country if domestic else random.choice([c for c in COUNTRIES if c != home_country])
    city = random.choice(COUNTRY_CITIES[country])
    international = 0 if country == home_country else 1
 
    ip_country = country if random.random() < 0.95 else random.choice([c for c in COUNTRIES if c != country])
 
    distance = round(random.uniform(0, 50) if not international else random.uniform(500, 15000), 2)
 
    lo, hi = MERCHANT_AVG_RANGE[merchant["merchant_category"]]
    amount = round(random.uniform(lo, hi), 2)
    if random.random() < 0.01:         
        amount = round(amount * random.uniform(5, 10), 2)
 
    return {
        "transaction_id": str(uuid.uuid4()),
        "customer_id": customer["customer_id"],
        "merchant_id": merchant["merchant_id"],
        "transaction_time": datetime.now(timezone.utc).isoformat(),
        "transaction_amount": amount,
        "transaction_type": transaction_type,
        "payment_method": random.choice(PAYMENT_OPTIONS),
        "city": city,
        "country": country,
        "ip_country": ip_country,
        "device_type": device_type,
        "operating_system": operating_system,
        "browser": browser,
        "card_type": random.choice(CARD_TYPE_OPTIONS),
        "card_present": card_present,
        "international_transaction": international,
        "distance_from_home": distance,
    }
 
 
def stream_transactions(customers, merchants, rate_per_sec=None, duration_sec=None):
    """stream transactions to a Kafka topic using the provided producer.
        for txn in stream_transactions(customers, merchants):
            producer.send(topic, value=txn)
    rate_per_sec=None means no throttling.
    duration_sec=None means run forever .
    """
    interval = 1.0 / rate_per_sec if rate_per_sec else 0
    start = time.monotonic()
    while True:
        if duration_sec is not None and (time.monotonic() - start) >= duration_sec:
            return
        customer = random.choice(customers)
        merchant = random.choice(merchants)
        yield make_transaction(customer, merchant)
        if interval:
            time.sleep(interval)
 
 
