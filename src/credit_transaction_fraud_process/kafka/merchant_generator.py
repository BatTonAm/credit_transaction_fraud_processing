import random
from datetime import date, datetime, timezone
from faker import Faker
 
fake = Faker()
 
def clamp(x, lo, hi):
    return max(lo, min(x, hi))
 
COUNTRY_CITIES = {
    "Australia": ["Melbourne", "Sydney"],
    "Canada": ["Montreal", "Toronto", "Vancouver"],
    "France": ["Lyon", "Paris"],
    "Germany": ["Berlin", "Munich"],
    "India": ["Bangalore", "Delhi", "Hyderabad", "Mumbai"],
    "Singapore": ["Singapore"],
    "UK": ["Birmingham", "London", "Manchester"],
    "USA": ["Chicago", "Houston", "Los Angeles", "New York"],
}
COUNTRIES = list(COUNTRY_CITIES.keys())

MERCHANT_CATEGORY_INFO = {
    "Electronics":   {"acronym": "ELEC", "mcc": "5732"},
    "Entertainment": {"acronym": "ENTM", "mcc": "7832"},
    "Fashion":       {"acronym": "FASH", "mcc": "5651"},
    "Fuel":          {"acronym": "FUEL", "mcc": "5541"},
    "Gaming":        {"acronym": "GAME", "mcc": "5816"},
    "Grocery":       {"acronym": "GROC", "mcc": "5411"},
    "Healthcare":    {"acronym": "HLTH", "mcc": "8011"},
    "Luxury":        {"acronym": "LUXY", "mcc": "5944"},
    "Restaurants":   {"acronym": "REST", "mcc": "5812"},
    "Travel":        {"acronym": "TRVL", "mcc": "4722"},
}
 
SIZE_OPTIONS = ["Small", "Medium", "Enterprise"]
SIZE_WEIGHTS = [50, 35, 15]
 
RISK_OPTIONS = ["High", "Medium", "Low"]
RISK_WEIGHTS = [5, 25, 70]
 
 
def generate_merchants(per_category):
    merchants = []
    today = datetime.now(timezone.utc).date()
 
    for category, info in MERCHANT_CATEGORY_INFO.items():
        for n in range(1, per_category + 1):
            country = random.choice(COUNTRIES)
            city = random.choice(COUNTRY_CITIES[country])
 
            years_ago = int(clamp(random.expovariate(1 / 6), 0, 30))
            established_date = date(today.year - years_ago, random.randint(1, 12), random.randint(1, 28))
 
            merchants.append({
                "merchant_id": f"{info['acronym']}{n:04d}",
                "merchant_name": fake.company(),
                "merchant_category": category,
                "merchant_mcc_code": info["mcc"],
                "merchant_country": country,
                "merchant_city": city,
                "merchant_size": random.choices(SIZE_OPTIONS, weights=SIZE_WEIGHTS)[0],
                "merchant_risk_level": random.choices(RISK_OPTIONS, weights=RISK_WEIGHTS)[0],
                "merchant_established_date": established_date.isoformat(),
                "merchant_online_flag": 1 if random.random() < 0.5 else 0
            })
    return merchants
 
 
