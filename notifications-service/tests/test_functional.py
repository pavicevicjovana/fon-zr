import unittest
from unittest.mock import AsyncMock, patch
import asyncio
from consumer import main

class TestConsumerFunctional(unittest.IsolatedAsyncioTestCase):
    
    @patch('consumer.AIOKafkaConsumer')
    async def test_consumer_loop(self, mock_kafka_class):
      
        mock_consumer = AsyncMock()
        mock_kafka_class.return_value = mock_consumer
        
        
        mock_consumer.start = AsyncMock(return_value=None)
        
        
        mock_consumer.__aiter__.return_value = [] 
        
        
        try:
            await asyncio.wait_for(main(), timeout=2)
        except (asyncio.TimeoutError, StopAsyncIteration):
            pass
            
       
        mock_consumer.start.assert_called()
        print("Test prošao trenutno bez čekanja!")

if __name__ == '__main__':
    unittest.main()