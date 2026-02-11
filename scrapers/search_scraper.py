
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.client_config import ClientConfig

from bs4 import BeautifulSoup

from dataclasses import dataclass
from hashlib import sha256
from typing import Optional
import time
import re

from config import  get_settings

from logging_config import get_logger


logger = get_logger(f'{__name__}.SearchScraper')
settings = get_settings()


@dataclass
class SearchResult:
    title: str
    url: str
    content: str
    hash: str


class SearchScraper:

    @staticmethod
    def initialize() -> webdriver.Remote:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        client_config = ClientConfig(
            remote_server_addr=settings.SELENIUM_REMOTE_SERVER_ADDR,
        )
        browser = webdriver.Remote(
            options=options,
            client_config=client_config,
        )

        browser.execute_cdp_cmd(
            "Network.enable",
            {}
        )

        browser.execute_cdp_cmd(
            "Network.setBlockedURLs",
            {
                "urls": [
                    "*googlesyndication.com/*",
                    "*doubleclick.net/*",
                    "*adsystem.com/*",
                    "*adservice.google.com/*",
                    "*facebook.com/tr/*",
                    "*taboola.com/*",
                    "*outbrain.com/*"
                ]
            }
        )

        return browser

    @staticmethod
    def get_clean_text(text: str) -> str:
        cleaned = re.sub(r'\s+', ' ', text).strip()
        return cleaned

    def __init__(self):
        self.browser: webdriver.Remote = self.initialize()

    def fetch(self, url: str, wait: int = 5) -> Optional[SearchResult, None]:
        try:
            self.browser.get(url)

            if wait > 0:
                time.sleep(wait)

            soup = BeautifulSoup(self.browser.page_source, 'html.parser')

            page_context = self.get_clean_text(soup.get_text(strip=True))
            h = sha256(page_context.encode('utf-8')).hexdigest()

            return SearchResult(
                url=url,
                content=page_context,
                hash=h,
                title=self.browser.title
            )

        except Exception as e:
            logger.error(f'ERROR - SearchScraper:fetch{e}')
            self.close()
            logger.info(f'ERROR - SearchScraper:fetch:browser-removed')
            time.sleep(1)
            self.initialize()
            logger.info(f'ERROR - SearchScraper:fetch:reinitialize')

        return None

    def close(self):
        if hasattr(self, 'browser') and self.browser is not None:
            self.browser.close()
            self.browser.quit()


__all__ = 'SearchScraper', 'SearchResult'