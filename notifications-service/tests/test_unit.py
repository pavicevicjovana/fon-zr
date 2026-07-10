import unittest
from consumer import build_welcome_email

class TestEmailBuilders(unittest.TestCase):
    def test_build_welcome_email(self):
        data = {"user_name": "Nensi"}
        subject, html = build_welcome_email(data)
        self.assertIn("Dobrodošli, Nensi!", html)
        self.assertEqual(subject, "Dobrodošli u Velura Online Store!")