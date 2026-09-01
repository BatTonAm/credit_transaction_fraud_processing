
import random
from datetime import date, datetime, timedelta, timezone
 
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
 
SEGMENT_OPTIONS = ["Retail", "Premium", "Business"]
SEGMENT_WEIGHTS = [70, 25, 5]
 
 
def generate_customers(start_id, end_id):
    customers = []
    today = datetime.now(timezone.utc).date()
 
    for i in range(start_id, end_id + 1):
        home_country = random.choice(COUNTRIES)
        home_city = random.choice(COUNTRY_CITIES[home_country])
 
        chosen_segment = random.choices(SEGMENT_OPTIONS, weights=SEGMENT_WEIGHTS)[0]
 
        age_years = int(clamp(random.gauss(38, 10), 18, 80))
        birth_year = today.year - age_years
        dob = date(birth_year, random.randint(1, 12), random.randint(1, 28))
 
        credit_score = int(clamp(random.gauss(700, 50), 300, 850))
        annual_income = round(clamp(random.lognormvariate(10.8, 0.6), 15000, 500000), 2)
 
        signup_days_ago = int(clamp(random.expovariate(1 / (365 * 4)), 0, 365 * 20))
        signup_date = today - timedelta(days=signup_days_ago)
 
        customers.append({
            "customer_id": f"CUST{i:06d}",
            "customer_home_country": home_country,
            "customer_home_city": home_city,
            "customer_dob": dob.isoformat(),
            "customer_segment": chosen_segment,
            "customer_credit_score": credit_score,
            "annual_income": annual_income,
            "customer_signup_date": signup_date.isoformat(),
        })
    return customers
 


 