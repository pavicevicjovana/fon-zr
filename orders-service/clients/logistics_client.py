class LogisticsClient:
    """Stub for future logistics/shipping provider integration."""

    async def create_shipment(self, address: str, items: list) -> dict:
        return {"status": "stub", "address": address, "item_count": len(items)}
