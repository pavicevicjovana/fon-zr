import os
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import unittest
from unittest.mock import MagicMock
from users.service import UserService
from repository import UserRepository

class TestUserIntegration(unittest.TestCase):
    def setUp(self):
        
        self.mock_db = MagicMock()
        self.repo = UserRepository(self.mock_db)
        self.service = UserService(self.mock_db)
        
        self.service.repo = self.repo

    def test_get_profil_integration(self):
       
        self.mock_db.query.return_value.filter.return_value.first.return_value = MagicMock(id=1, ime="Nensi")
        
        user = self.service.get_profil(1)
        self.assertEqual(user.ime, "Nensi")

if __name__ == '__main__':
    unittest.main()