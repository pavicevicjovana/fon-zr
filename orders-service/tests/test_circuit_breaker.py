import sys
import os
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
import pytest
from unittest.mock import patch, AsyncMock
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from cart.service import CartService, product_catalog_breaker

@pytest.fixture
def cart_service():
    return CartService()

@pytest.mark.asyncio
async def test_circuit_breaker_triggers_fallback(cart_service):
    
    with patch("httpx.AsyncClient.get", side_effect=Exception("Connection Error")):
        
        
        for _ in range(3):
            try:
                await cart_service._validate_stock("123", "M", "crvena", 1)
            except Exception:
                pass
        
       
        print(f"Breaker failures: {product_catalog_breaker.fail_counter}")
        
        assert product_catalog_breaker.current_state == "open"