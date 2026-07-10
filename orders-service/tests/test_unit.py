import os
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import unittest
from unittest.mock import MagicMock, patch, AsyncMock
from cart.service import CartService

class TestCartServiceUnit(unittest.IsolatedAsyncioTestCase):
    
    @patch('cart.service.httpx.AsyncClient')
    def setUp(self, mock_client_class):
        
        self.service = CartService()
       
        self.service.repo = MagicMock()

    @patch('cart.service.httpx.AsyncClient')
    async def test_dodaj_stavku_success(self, mock_client_class):
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        
        
        mock_response.json = MagicMock(return_value={
            "variants": [{"size": "L", "color": "Crna", "stock": 10}]
        })
        
        
        mock_client = mock_client_class.return_value.__aenter__.return_value
        mock_client.get.return_value = mock_response

        
        self.service.repo.get_active_cart.return_value = MagicMock(id=1)
        self.service.repo.add_item.return_value = MagicMock(id=100)

        
        mock_db = MagicMock()
        res = await self.service.dodaj_stavku(mock_db, 1, {
            "proizvod_id": "p1", "velicina": "L", "boja": "Crna", 
            "kolicina": 1, "naziv_proizvoda": "Majica", "cijena_po_komadu": 1000
        })

        
        self.assertEqual(res["message"], "Artikal dodan u korpu")
        self.service.repo.add_item.assert_called_once()

if __name__ == '__main__':
    unittest.main()