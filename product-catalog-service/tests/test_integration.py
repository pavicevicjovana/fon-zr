import unittest
from unittest.mock import patch, AsyncMock
import database
import repository


with patch('database.get_db', return_value=AsyncMock()):
    from search.service import SearchService

class TestSearchServiceIntegration(unittest.IsolatedAsyncioTestCase):
    
    
    @patch('search.service.ProductRepository')
    async def test_search_with_repo_integration(self, mock_repo_class):
        
        mock_repo = mock_repo_class.return_value
        mock_repo.search = AsyncMock(return_value=[{"name": "Test Proizvod"}])
        
        
        service = SearchService()
        
        
        result = await service.search(q="test", category=None, collection=None, min_price=None, max_price=None)
        
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Test Proizvod")
        mock_repo.search.assert_called_once()

if __name__ == '__main__':
    unittest.main()