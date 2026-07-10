import os
import json
from dotenv import load_dotenv
from aiokafka import AIOKafkaProducer

load_dotenv()

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")

async def posalji_order_completed(narudzba_id: int, korisnik_id: int,
                                   email: str, ukupan_iznos: float, stavke: list,
                                   user_name: str = "Potrosac"):
    """
    Šalje order_completed event u Kafka topic
    Prima ga:
      - product-catalog-service → smanjuje zalihe
      - notifications-service   → šalje email potvrdu
    """
    producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda m: json.dumps(m).encode("utf-8")
    )

    await producer.start()
    try:
        event = {
            "narudzba_id": narudzba_id,
            "order_id": narudzba_id,
            "korisnik_id": korisnik_id,
            "user_email": email,
            "user_name": user_name,
            "total_price": ukupan_iznos,
            "stavke": stavke,
            "items": stavke
        }
        await producer.send_and_wait("order_completed", event)
        print(f"Event order_completed poslan za narudžbinu {narudzba_id}")
    finally:
        await producer.stop()