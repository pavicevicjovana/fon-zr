import os
import json
import asyncio
from dotenv import load_dotenv
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from tracing import setup_tracing, extract_trace_context, inject_trace_context
from opentelemetry import trace

from log_config import (
    setup_logging,
    correlation_id_from_event,
    set_correlation_id,
    get_correlation_id,
)

from blockchain_client import BlockchainClient, STATUS_SUCCESS, STATUS_FAILED

load_dotenv()

client = AsyncIOMotorClient(os.getenv("MONGODB_URL"))
db = client[os.getenv("MONGODB_DB_NAME")]
products_collection = db["products"]

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")

logger = setup_logging("product-catalog-service")
tracer = setup_tracing("product-catalog-service")

blockchain = BlockchainClient("CATALOG_PRIVATE_KEY", "product-catalog-service")


async def main():
    consumer = AIOKafkaConsumer(
        "order_completed",
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="product-catalog-group",
        value_deserializer=lambda m: json.loads(m.decode("utf-8"))
    )

    producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda m: json.dumps(m).encode("utf-8")
    )

    for attempt in range(1, 11):
        try:
            await consumer.start()
            await producer.start()
            logger.info("Product Catalog Consumer uspjesno pokrenut")
            break
        except Exception as e:
            logger.error(f"Pokusaj {attempt}/10 neuspio: {e}. Cekanje 5s...")
            await asyncio.sleep(5)
            if attempt == 10:
                logger.error("Nije moguce pokrenuti consumer nakon 10 pokusaja.")
                raise

    try:
        async for message in consumer:
            data = message.value

            set_correlation_id(correlation_id_from_event(data))
            corr_id = get_correlation_id()

            ctx = extract_trace_context(data)
            with tracer.start_as_current_span("obrada order_completed", context=ctx):
                logger.info(f"Primljen event sa ID-ijem: {corr_id} : {data}")

                narudzba_id = data.get("narudzba_id", "N/A")
                try:
                    stavke = data["stavke"]

                    for stavka in stavke:
                        product_id = stavka["product_id"]
                        quantity = int(stavka["quantity"])
                        size = stavka.get("size")
                        color = stavka.get("color")

                        product = await products_collection.find_one({"_id": ObjectId(product_id)})

                        if not product:
                            raise Exception(f"Proizvod {product_id} nije pronađen")

                        variant_found = False
                        updated_variants = []
                        for variant in product.get("variants", []):
                            if variant["size"].lower() == size.lower() and variant["color"].lower() == color.lower():
                                if variant["stock"] < quantity:
                                    raise Exception(f"Nema dovoljno zaliha za {product['name']}")
                                variant["stock"] -= quantity
                                variant_found = True
                            updated_variants.append(variant)

                        if not variant_found:
                            raise Exception(f"Varijanta velicina={size}, boja={color} nije pronađena")

                        await products_collection.update_one(
                            {"_id": ObjectId(product_id)},
                            {"$set": {"variants": updated_variants}}
                        )
                        logger.info(f"Zalihe smanjene za proizvod {product['name']}, kolicina: {quantity}")

                    confirmed_data = {
                        "order_id": narudzba_id,
                        "user_email": data.get("user_email"),
                        "user_name": data.get("user_name", "Potrosac"),
                        "correlation_id": corr_id,
                    }
                    inject_trace_context(confirmed_data)
                    await producer.send_and_wait("order_confirmed", confirmed_data)
                    logger.info(f"Poslan order_confirmed event za narudžbinu {narudzba_id}")

                    blockchain.log_step_bg(narudzba_id, "STOCK_RESERVED", STATUS_SUCCESS, correlation_id=corr_id)

                except Exception as e:
                    logger.error(f"Greška pri obradi narudžbine: {e}")
                    refund_data = {
                        "order_id": narudzba_id,
                        "user_email": data.get("user_email"),
                        "user_name": data.get("user_name", "Potrosac"),
                        "reason": str(e),
                        "correlation_id": corr_id,
                    }
                    inject_trace_context(refund_data)
                    await producer.send_and_wait("refund_order", refund_data)
                    logger.info(f"Poslat refund_order event za narudžbinu {narudzba_id}")

                    blockchain.log_step_bg(narudzba_id, "STOCK_RESERVATION_FAILED", STATUS_FAILED, correlation_id=corr_id)

    finally:
        await consumer.stop()
        await producer.stop()

if __name__ == "__main__":
    asyncio.run(main())
