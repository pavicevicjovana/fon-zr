import unittest
from unittest.mock import AsyncMock, patch
from consumer import send_email

class TestNotificationIntegration(unittest.IsolatedAsyncioTestCase):
    @patch('httpx.AsyncClient.post', new_callable=AsyncMock)
    async def test_send_email_success(self, mock_post):
        mock_post.return_value.status_code = 201
        await send_email("test@test.com", "Nensi", "Subject", "Content")
        mock_post.assert_called_once()