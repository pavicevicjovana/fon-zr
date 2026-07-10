import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import unittest
from unittest.mock import MagicMock, patch, AsyncMock
from users.service import UserService

class TestUserServiceUnit(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        
        self.mock_db = MagicMock()
        
        self.service = UserService(db=self.mock_db)
        
        self.service.repo = MagicMock()

    async def test_get_profil_success(self):
        
        self.service.repo.get_by_id.return_value = {"id": 1, "ime": "Nensi"}
        
        result = self.service.get_profil(1)
        
        self.assertEqual(result["ime"], "Nensi")
        self.service.repo.get_by_id.assert_called_with(1)

    @patch('users.service.httpx.AsyncClient')
    async def test_dodaj_adresu_success(self, mock_client_class):
       
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_client = mock_client_class.return_value.__aenter__.return_value
        mock_client.get.return_value = mock_response

        
        self.service.repo.get_by_id.return_value = MagicMock()
        self.service.repo.get_or_create_mesto.return_value = MagicMock(id=1, grad="BG", drzava="Serbia")
        self.service.repo.add_address.return_value = MagicMock(id=10, ulica="Test", kucni_broj="1")
        
        
        result = await self.service.dodaj_adresu(
            korisnik_id=1, ulica="Test", kucni_broj="1", sprat=1, 
            postanski_broj="11000", grad="BG", drzava="Serbia"
        )
        
        
        self.assertEqual(result["message"], "Adresa uspješno dodana")
        self.service.repo.add_address.assert_called()

if __name__ == '__main__':
    unittest.main()