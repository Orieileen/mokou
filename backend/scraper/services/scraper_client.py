# scraper/services/scraper_client.py

import logging
import os
import time
from typing import Any, Dict

import requests
from dotenv import load_dotenv


class ScraperClient:
    """
    封装 Pangolin ScrapeAPI：
      • login()   获取并保存 token
      • scrape()  调用 /scrape
    出错时抛出 RuntimeError
    """

    def __init__(self) -> None:
        self.MAX_RETRIES = int(os.getenv("MAX_RETRIES"))
        self.RETRY_DELAY = int(os.getenv("RETRY_DELAY"))
        self.session = requests.Session()
        self.BASE_URL = os.getenv("SCRAPER_BASE_URL")
        self.token: str | None = None

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.BASE_URL}{path}"
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        for _ in range(self.MAX_RETRIES):
            try:
                resp = self.session.post(url, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                return data
            except requests.RequestException as e:
                logger.error(f"scrapeapi error: {e}")
                time.sleep(self.RETRY_DELAY)
        raise RuntimeError(f"scrapeapi failed after {self.MAX_RETRIES} retries.")
    
    # ---------- 公开接口 ----------
    def login(self, email: str, password: str) -> None:
        data = self._post("/auth", {"email": email, "password": password})
        token = data.get("data")
        if not token:
            raise RuntimeError("Auth failed: token missing")
        self.token = token

    def scrape(
        self, url: str, parserName: str, zipcode: str
    ) -> Dict[str, Any]:
        payload = {
            "url": url,
            "formats": ["json"],
            "parserName": parserName,
            "bizContext": {"zipcode": zipcode},
            "timeout": 60000,
        }
        return self._post("/scrape/", payload)


if __name__ == "__main__":
    load_dotenv()


    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    client = ScraperClient()
    client.login(os.getenv("SCRAPER_EMAIL"), os.getenv("SCRAPER_PASSWORD"))
    logger.info(client.scrape("https://www.amazon.com/dp/B0C4YHVGRJ", "amzProductDetail", "10001"))