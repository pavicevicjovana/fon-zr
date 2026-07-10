import unittest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, MagicMock

client = TestClient(app)

class TestGatewayFunctional(unittest.TestCase):
    def test_health_check(self):
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    @patch('main.forward_request')
    def test_get_products_proxied(self, mock_forward):
        # Simuliramo odgovor iz catalog servisa
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"id": "1", "name": "Majica"}]
        mock_forward.return_value = mock_response

        response = client.get("/api/products")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["name"], "Majica")