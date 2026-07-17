import sys
import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import unittest
from unittest.mock import patch, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pybreaker
from fastapi import HTTPException
from cart.service import CartService, product_catalog_breaker


class TestCircuitBreaker(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.cart_service = CartService()
        
        product_catalog_breaker.close()
        product_catalog_breaker._state_storage.reset_counter()

    def tearDown(self):
        product_catalog_breaker.close()
        product_catalog_breaker._state_storage.reset_counter()

    async def test_pocetno_stanje_je_zatvoreno(self):
        self.assertEqual(product_catalog_breaker.current_state, "closed")

    async def test_prekidac_se_otvara_posle_tri_otkaza(self):
        """Posle fail_max (3) uzastopna otkaza servisa prekidac se otvara."""
        with patch("httpx.AsyncClient.get", side_effect=Exception("Connection Error")):
            for _ in range(3):
                with self.assertRaises(Exception):
                    await self.cart_service._validate_stock("123", "M", "crvena", 1)

        self.assertEqual(product_catalog_breaker.fail_counter, 3)
        self.assertEqual(product_catalog_breaker.current_state, "open")

    async def test_otvoren_prekidac_odbija_poziv_bez_cekanja(self):
        """Kada je prekidac otvoren, poziv se odbija odmah, bez HTTP zahteva."""
        product_catalog_breaker.open()

        with patch("httpx.AsyncClient.get") as mock_get:
            with self.assertRaises(pybreaker.CircuitBreakerError):
                await self.cart_service._validate_stock("123", "M", "crvena", 1)
            
            mock_get.assert_not_called()

    async def test_fallback_ne_prekida_dodavanje_u_korpu(self):
        """Kada je prekidac otvoren, validacija se preskace bez izuzetka."""
        product_catalog_breaker.open()
        
        await self.cart_service.validate_stock_with_fallback("123", "M", "crvena", 1)

    async def test_poslovna_greska_ne_otvara_prekidac(self):
        """
        Nedostatak zaliha (HTTPException) je poslovna greska, a ne otkaz servisa,
        pa se ne broji kao otkaz. Zbog toga je HTTPException u exclude listi.
        """
        odgovor = MagicMock()
        odgovor.status_code = 200
        odgovor.json.return_value = {
            "variants": [{"size": "M", "color": "crvena", "stock": 1}]
        }

        with patch("httpx.AsyncClient.get", return_value=odgovor):
            for _ in range(5):
                with self.assertRaises(HTTPException):
                    # Trazi se 99 komada, a na stanju je 1.
                    await self.cart_service._validate_stock("123", "M", "crvena", 99)

        self.assertEqual(product_catalog_breaker.fail_counter, 0)
        self.assertEqual(product_catalog_breaker.current_state, "closed")


if __name__ == "__main__":
    unittest.main()