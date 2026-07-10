import os
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import unittest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from main import app
from database import get_db


mock_db = MagicMock()


app.dependency_overrides[get_db] = lambda: mock_db

client = TestClient(app)

class TestUserFunctional(unittest.TestCase):
    def test_health_check(self):
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["service"], "users-service")

    def test_get_users_endpoint(self):
        
        pass

if __name__ == '__main__':
    unittest.main()