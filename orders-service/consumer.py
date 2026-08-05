import os
import json
import asyncio
import logging
from dotenv import load_dotenv
from aiokafka import AIOKafkaConsumer
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Narudzba
from blockchain_client import BlockchainClient, STATUS_SUCCESS, STATUS_COMPENSATED
from log_config import setup_logging, correlation_id_from_event

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

blockchain = BlockchainClient("ORDERS_CONSUMER_PRIVATE_KEY", "orders-service")

logger = setup_logging("orders-service")

async def main():
    consumer = AIOKafkaConsumer(
        "refund_order",
        "order_confirmed",
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="orders-group",
        value_deserializer=lambda m: json.loads(m.decode("utf-8"))
    )

    for attempt in range(1, 11):
        try:
            await consumer.start()
            logger.info("Orders Consumer uspesno pokrenut")
            break
        except Exception as e:
            logger.error(f"Pokusaj {attempt}/10 neuspeo: {e}. Cekanje 5s...")
            await asyncio.sleep(5)
            if attempt == 10:
                logger.error("Nije moguce pokrenuti consumer nakon 10 pokusaja.")
                raise

    try:
        async for message in consumer:
            data = message.value
            topic = message.topic

            from log_config import set_correlation_id
            set_correlation_id(correlation_id_from_event(data))

            logger.info(f"Primljen event sa topica '{topic}': {data}")

            db = SessionLocal()
            try:
                narudzba = db.query(Narudzba).filter(
                    Narudzba.id == data.get("order_id")
                ).first()

                if narudzba:
                    korak = None

                    if topic == "order_confirmed":
                        narudzba.status = "potvrdjena"
                        logger.info(f"Narudžbina {narudzba.id} potvrdjena")
                        korak = ("ORDER_CONFIRMED", STATUS_SUCCESS)
                    elif topic == "refund_order":
                        narudzba.status = "otkazano"
                        logger.info(f"Narudžbina {narudzba.id} otkazana. Razlog: {data.get('reason')}")
                        
                        korak = ("ORDER_CANCELLED", STATUS_COMPENSATED)

                    db.commit()

                    
                    if korak:
                        blockchain.log_step_bg(narudzba.id, korak[0], korak[1])
            except Exception as e:
                logger.error(f"Greška pri ažuriranju narudžbine: {e}")
            finally:
                db.close()

    finally:
        await consumer.stop()

if __name__ == "__main__":
    asyncio.run(main())