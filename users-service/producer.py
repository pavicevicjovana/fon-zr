import os
import json
from dotenv import load_dotenv
from aiokafka import AIOKafkaProducer
import logging
from log_config import get_correlation_id

load_dotenv()

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")

logger = logging.getLogger(__name__)


async def posalji_user_registered(korisnik_id: int, email: str, ime: str, prezime: str):
    producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda m: json.dumps(m).encode("utf-8")
    )
    await producer.start()
    try:
        event = {
            "korisnik_id": korisnik_id,
            "user_email": email,
            "user_name": f"{ime} {prezime}",
            "correlation_id": get_correlation_id(),
        }
        await producer.send_and_wait("user_registered", event)
        logger.info(f"Event user_registered poslan za korisnika {korisnik_id}")
    finally:
        await producer.stop()
