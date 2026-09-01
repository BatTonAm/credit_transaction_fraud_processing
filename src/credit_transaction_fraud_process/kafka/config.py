import os
from dotenv import load_dotenv
from dataclasses import asdict, dataclass



@dataclass(frozen=True)
class Settings:
    bootstrap_servers: str
    security_protocol: str
    sasl_mechanisms: str
    sasl_username: str
    sasl_password: str
    def to_kafka_config(self) -> dict:
        return {k.replace("_", "."): v for k, v in asdict(self).items()}

def load_settings() -> Settings:
    load_dotenv()
    settings = Settings(
        bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVER"),
        security_protocol="SASL_SSL",
        sasl_mechanisms="PLAIN",
        sasl_username=os.getenv("KAFKA_API_KEY"),
        sasl_password=os.getenv("KAFKA_API_SECRET")
    )
    validate_settings(settings)
    return settings
def validate_settings(settings: Settings) -> None:
    if not settings.bootstrap_servers:
        raise ValueError("KAFKA_BOOTSTRAP_SERVER is not set in the environment variables.")
    if not settings.sasl_username:
        raise ValueError("KAFKA_API_KEY is not set in the environment variables.")
    if not settings.sasl_password:
        raise ValueError("KAFKA_API_SECRET is not set in the environment variables.")
