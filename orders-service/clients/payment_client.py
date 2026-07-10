class PaymentClient:
    """Stub for future payment gateway integration."""

    async def charge(self, amount: float, currency: str = "RSD") -> dict:
        return {"status": "stub", "amount": amount, "currency": currency}
