import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import database
import repository 


with patch('database.get_db', return_value=MagicMock()):
    from search.service import SearchService

class TestSearchServiceUnit(unittest.IsolatedAsyncioTestCase):
    
    
    @patch('search.service.ProductRepository')
    async def test_search_logic(self, mock_repo_class):
        
        mock_repo = mock_repo_class.return_value
       
        mock_repo.search = AsyncMock(return_value=[{"id": "1", "name": "Majica"}])
        
        service = SearchService()
        
       
        result = await service.search(
            q="majica", 
            category=None, 
            collection=None, 
            min_price=10, 
            max_price=50
        )
        
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Majica")
        
        
        mock_repo.search.assert_called_once()
        
        
        call_args = mock_repo.search.call_args[0][0]
        self.assertIn("price", call_args)
        self.assertEqual(call_args["price"]["$gte"], 10)

if __name__ == '__main__':
    unittest.main()