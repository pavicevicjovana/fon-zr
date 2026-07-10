import unittest
from unittest.mock import MagicMock  
from fastapi import HTTPException
from main import verify_token

class TestGatewayAuth(unittest.TestCase):
    def test_verify_token_invalid(self):
        mock_creds = MagicMock()
        mock_creds.credentials = "neki.nevalidan.token"
        
        with self.assertRaises(HTTPException):
            verify_token(mock_creds)

if __name__ == '__main__':
    unittest.main()