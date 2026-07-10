import unittest
from unittest.mock import AsyncMock, patch, MagicMock 
import httpx
from main import forward_request

class TestGatewayIntegration(unittest.IsolatedAsyncioTestCase):
    
    @patch("httpx.AsyncClient.request")
    async def test_forward_request_success(self, mock_request):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"msg": "ok"}
        mock_request.return_value = mock_resp

        response = await forward_request("http://test.com", "GET", {})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"msg": "ok"})

if __name__ == '__main__':
    unittest.main()