import os
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import unittest
from unittest.mock import MagicMock, AsyncMock, patch
from orders.service import OrderService

class TestOrderIntegration(unittest.IsolatedAsyncioTestCase):
    
    def setUp(self):
        self.service = OrderService()
        self.service.order_repo = MagicMock()
        self.service.cart_repo = MagicMock()
        self.mock_db = MagicMock()

    @patch('orders.service.posalji_order_completed', new_callable=AsyncMock)
    async def test_kreiraj_narudzbu_integration(self, mock_producer):
       
        self.service.cart_repo.get_active_cart.return_value = MagicMock(
            id=1, 
            stavke=[MagicMock(kolicina=2, cijena_po_komadu=500, proizvod_id="p1")]
        )
        
        self.service.order_repo.create.return_value = MagicMock(id=10, ukupan_iznos=1000, status="kreirano")
        
        
        result = await self.service.kreiraj_narudzbu(self.mock_db, 1, {
            "adresa_isporuke": "Test ulica 1",
            "email": "nensi@example.com",
            "user_name": "Nensi"
        })
        
        
        self.assertEqual(result["narudzba_id"], 10)
        self.service.cart_repo.close_cart.assert_called_once()
        mock_producer.assert_called_once()

if __name__ == '__main__':
    unittest.main()