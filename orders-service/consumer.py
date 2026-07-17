import os
import json
import asyncio
from dotenv import load_dotenv
from aiokafka import AIOKafkaConsumer
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Narudzba
from blockchain_client import BlockchainClient, STATUS_SUCCESS, STATUS_COMPENSATED

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

blockchain = BlockchainClient("ORDERS_CONSUMER_PRIVATE_KEY", "orders-service")

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
            print("Orders Consumer uspjesno pokrenut")
            break
        except Exception as e:
            print(f"Pokusaj {attempt}/10 neuspio: {e}. Cekanje 5s...")
            await asyncio.sleep(5)
            if attempt == 10:
                print("Nije moguce pokrenuti consumer nakon 10 pokusaja.")
                raise

    try:
        async for message in consumer:
            data = message.value
            topic = message.topic
            print(f"Primljen event sa topica '{topic}': {data}")

            db = SessionLocal()
            try:
                narudzba = db.query(Narudzba).filter(
                    Narudzba.id == data.get("order_id")
                ).first()

                if narudzba:
                    korak = None

                    if topic == "order_confirmed":
                        narudzba.status = "potvrdjena"
                        print(f"Narudžbina {narudzba.id} potvrđena")
                        korak = ("ORDER_CONFIRMED", STATUS_SUCCESS)
                    elif topic == "refund_order":
                        narudzba.status = "otkazano"
                        print(f"Narudžbina {narudzba.id} otkazana — razlog: {data.get('reason')}")
                        
                        korak = ("ORDER_CANCELLED", STATUS_COMPENSATED)

                    db.commit()

                    
                    if korak:
                        blockchain.log_step_bg(narudzba.id, korak[0], korak[1])
            except Exception as e:
                print(f"Greška pri ažuriranju narudžbine: {e}")
            finally:
                db.close()

    finally:
        await consumer.stop()

if __name__ == "__main__":
    asyncio.run(main())