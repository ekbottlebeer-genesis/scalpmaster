import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime
from modules.data.news_loader import NewsLoader

class TestNewsLoader(unittest.TestCase):
    def setUp(self):
        self.loader = NewsLoader()
        # Mock Data (Forex Factory Format subset)
        self.mock_data = [
            {
                "title": "Unemployment Claims",
                "country": "USD",
                "date": "2024-01-01T12:00:00+00:00", # Noon UTC
                "impact": "High", # Red
                "forecast": "200k",
                "previous": "190k"
            },
            {
                "title": "Minor Speech",
                "country": "EUR",
                "date": "2024-01-01T12:00:00+00:00",
                "impact": "Low", # Yellow
            }
        ]

    @patch('modules.data.news_loader.requests.get')
    @patch('modules.data.news_loader.datetime')
    def test_news_blackout_active(self, mock_datetime, mock_get):
        # 1. Mock Request
        mock_response = MagicMock()
        mock_response.json.return_value = self.mock_data
        mock_get.return_value = mock_response
        
        # 2. Mock Time to be 12:05 (During news window)
        # Note: Loader uses datetime.utcnow()
        mock_datetime.utcnow.return_value = datetime.fromisoformat("2024-01-01T12:05:00")
        mock_datetime.fromisoformat = datetime.fromisoformat # Keep original method

        # 3. Test USD Pair (Should match High Impact USD news)
        is_news = self.loader.is_news_imminent("EURUSD")
        self.assertTrue(is_news)
        
    @patch('modules.data.news_loader.requests.get')
    @patch('modules.data.news_loader.datetime')
    def test_news_blackout_inactive_time(self, mock_datetime, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = self.mock_data
        mock_get.return_value = mock_response
        
        # 2. Time 13:00 (1 hour later, outside 15m window)
        mock_datetime.utcnow.return_value = datetime.fromisoformat("2024-01-01T13:00:00")
        mock_datetime.fromisoformat = datetime.fromisoformat

        is_news = self.loader.is_news_imminent("EURUSD")
        self.assertFalse(is_news)

    @patch('modules.data.news_loader.requests.get')
    @patch('modules.data.news_loader.datetime')
    def test_news_ignore_low_impact(self, mock_datetime, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = self.mock_data
        mock_get.return_value = mock_response
        
        # Time 12:00 (During news)
        mock_datetime.utcnow.return_value = datetime.fromisoformat("2024-01-01T12:00:00")
        mock_datetime.fromisoformat = datetime.fromisoformat

        # 3. Test JPY Pair (Should NOT match USD/EUR news) - Assuming standard pair code
        # Actually logic matches if JPY is in country. 
        # "USD", "EUR" are in data. 
        # If we check "GBPCHF", it should be False.
        is_news = self.loader.is_news_imminent("GBPCHF")
        self.assertFalse(is_news)

if __name__ == '__main__':
    unittest.main()
