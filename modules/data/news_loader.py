 import logging
import requests
import json
import time
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class NewsLoader:
    # Forex Factory JSON feed (unofficial but stable)
    NEWS_URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
    CACHE_DURATION = 4 * 3600  # 4 Hours
    RETRY_DELAY = 300 # 5 minutes on failure
    
    def __init__(self):
        self.news_cache: List[Dict] = []
        self.last_fetch_time = 0
        self.blackout_minutes = 15

    def _fetch_news(self):
        """
        Fetches news from the source if cache is expired.
        """
        now = time.time()
        
        # Check Cache Expiry (regardless of empty cache)
        if now - self.last_fetch_time < self.CACHE_DURATION:
            return

        try:
            logger.info("Fetching News Data from Forex Factory...")
            response = requests.get(self.NEWS_URL, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Filter solely for High Impact to save memory
            # "impact": "High" (Red), "Medium" (Orange), "Low" (Yellow)
            self.news_cache = [
                item for item in data 
                if item.get('impact') == 'High'
            ]
            self.last_fetch_time = now
            logger.info(f"News Fetched. {len(self.news_cache)} High Impact events found.")
            
        except Exception as e:
            logger.error(f"Failed to fetch news: {e}")
            # Prevent spamming on error: set last_fetch_time to now - cache + retry_delay
            # So it waits RETRY_DELAY seconds before trying again
            self.last_fetch_time = now - self.CACHE_DURATION + self.RETRY_DELAY

    def is_news_imminent(self, symbol: str) -> bool:
        """
        Checks if a High Impact news event is happening now 
        (or upcoming/recent) for the currencies in the pair.
        """
        # Ensure we have data
        self._fetch_news()
        
        if not self.news_cache:
            return False

        # Parse Symbol (e.g. "EURUSD" -> ["EUR", "USD"])
        # Standard FX only. For XAUUSD -> ["XAU", "USD"]
        # Very naive splitter, assumes 3+3 chars or matches. 
        # Safer: Check containment.
        
        # Build set of relevant currencies
        relevant = set()
        # Common pairs logic
        if len(symbol) == 6:
            relevant.add(symbol[:3])
            relevant.add(symbol[3:])
        elif "USD" in symbol: # catch exotic
            relevant.add("USD")
            
        now_utc = datetime.utcnow()
        margin = timedelta(minutes=self.blackout_minutes)
        window_start = now_utc - margin
        window_end = now_utc + margin

        for event in self.news_cache:
            country = event.get('country') # e.g. "USD", "EUR"
            if country not in relevant:
                continue

            # Parse Event Time
            # Format usually: "2024-01-24T14:30:00-04:00" or similar
            # Actually the JSON feed usually has "date" like "2024-01-29T15:00:00+00:00"
            date_str = event.get('date')
            try:
                # We need to handle offsets. 
                # For robustness, we'll try standard ISO parsing
                # Python 3.9+ handles 'Z' or offset if valid iso.
                event_time = datetime.fromisoformat(date_str)
                # Ensure events are UTC comparable. 
                # If offset aware, convert to UTC (naive) or just compare aware.
                # Assuming now_utc is naive, we might have issues.
                # Let's clean offset 
                # Strict UTC handling
                if event_time.tzinfo is not None:
                     # Convert to UTC then strip info to match utcnow()
                     event_time = event_time.astimezone(timezone.utc).replace(tzinfo=None)
                
                if window_start <= event_time <= window_end:
                    logger.warning(f"News Blackout: {event['title']} ({country}) at {date_str}")
                    return True

            except Exception:
                continue
                
        return False
