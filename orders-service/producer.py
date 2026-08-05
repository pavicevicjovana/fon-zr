import os
import json
import logging
from dotenv import load_dotenv
from aiokafka import AIOKafkaProducer
from blockchain_client import BlockchainClient, STATUS_SUCCESS
from log_config import get_correlation_id
from tracing import inject_trace_context


load_dotenv()

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")

blockchain = BlockchainClient("ORDERS_PRIVATE_KEY", "orders-service") 

logger = logging.getLogger(__name__)


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
            "items": stavke,
            "correlation_id": get_correlation_id(),
        }
        inject_trace_context(event)
        await producer.send_and_wait("order_completed", event)
        logger.info(f"Event order_completed poslan za narudžbinu {narudzba_id}")
        blockchain.log_step_bg(narudzba_id, "ORDER_CREATED", STATUS_SUCCESS, correlation_id=get_correlation_id()) 
    finally:
        await producer.stop()