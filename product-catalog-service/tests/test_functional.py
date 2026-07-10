import unittest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import database


with patch('database.get_db', return_value=AsyncMock()):
    from main import app 

client = TestClient(app)

class TestSearchFunctional(unittest.TestCase):

    @patch('search.service.SearchService.search')
    def test_search_endpoint_success(self, mock_search):
        
        mock_search.return_value = [{"id": "1", "name": "Majica"}]
        
        
        response = client.get("/products/search?q=majica")
        
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["name"], "Majica")
        
       
        mock_search.assert_called_once()

    def test_health_check(self):
        
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

if __name__ == '__main__':
    unittest.main()