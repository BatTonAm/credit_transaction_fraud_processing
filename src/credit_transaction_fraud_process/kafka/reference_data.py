import json
import os
from pathlib import Path

from .customer_generator import generate_customers
from .merchant_generator import generate_merchants

DATA_DIR = Path(__file__).parent / "data"
CUSTOMER_PATH = DATA_DIR / "customers.json"
MERCHANT_PATH = DATA_DIR / "merchants.json"


def _atomic_write(path: Path, data) -> None:
    tmp_path = path.with_suffix(".tmp")
    tmp_path.write_text(json.dumps(data))
    os.replace(tmp_path, path)


def reference_data_exists() -> bool:
    return CUSTOMER_PATH.exists() and MERCHANT_PATH.exists()


def ensure_reference_data(num_customers=99642, per_category=30):
    if not reference_data_exists():
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        customers = generate_customers(1, num_customers)
        merchants = generate_merchants(per_category)
        _atomic_write(CUSTOMER_PATH, customers)
        _atomic_write(MERCHANT_PATH, merchants)
    else:
        customers = json.loads(CUSTOMER_PATH.read_text())
        merchants = json.loads(MERCHANT_PATH.read_text())
    return customers, merchants
