from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup

from config import get_settings

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import re


settings = get_settings()


@dataclass
class GuncelkesintilerResult:
    url: str
    hash: str
    hash_type: str
    title: str | None = None
    content: str | None = None
    urls: list[str] | None = None


class GuncelkesintilerScraper:
    def __init__(self):
        self.url_list = []

        self.options = Options()
        self.options.add_argument('--headless')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument("--disable-notifications")
        self.options.add_argument("--disable-infobars")
        self.options.add_argument("--disable-extensions")

        # self.client_config = ClientConfig(
        #     remote_server_addr='http://selenium_hub:4444/wd/hub',
        # )

        # self.browser = webdriver.Chrome(options=self.options)
        self.browser = webdriver.Remote(
            # client_config=self.client_config,
            options=self.options,
            command_executor=settings.SELENIUM_REMOTE_SERVER_HOST,
            # desired_capabilities=DesiredCapabilities.CHROME
        )
        self.browser.execute_cdp_cmd(
            "Network.enable",
            {}
        )

        self.browser.execute_cdp_cmd(
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

    def get_news_url_list(self) -> list[GuncelkesintilerResult]:
        self.browser.get("https://guncelkesintiler.com/bursa/orhangazi/")
        tables = WebDriverWait(self.browser, 10).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, ".col.s12.m6")
            )
        )

        now = datetime.today()

        for table in tables:
            for url in table.find_elements(By.TAG_NAME, 'a'):
                if re.search(str(now.year), url.text):
                    h = sha256((url.get_attribute('href') + url.text).encode('utf-8')).hexdigest()
                    self.url_list.append(
                        GuncelkesintilerResult(
                            url=url.get_attribute('href'),
                            hash=h,
                            hash_type='href+text',
                        )
                    )
                elif not re.search(str(now.year)[:1], url.text):
                    if not url.text in [
                        'Orhangazi Elektrik Kesintileri',
                        'Orhangazi elektrik arızalarının devamı için tıklayınız',
                        'Orhangazi Su Kesintileri',
                        'Orhangazi su arıza bilgilerinin devamı için tıklayınız'
                    ]:
                        h = sha256((url.get_attribute('href') + url.text).encode('utf-8')).hexdigest()
                        self.url_list.append(
                            GuncelkesintilerResult(
                                url=url.get_attribute('href'),
                                hash=h,
                                hash_type='href+text',
                            )
                        )
        return self.url_list

    def get_news_content(self, news_url_results: list[GuncelkesintilerResult]) -> list[GuncelkesintilerResult]:
        news_content = []
        for news_url_result in news_url_results:
            self.browser.get(news_url_result.url)
            soup = BeautifulSoup(self.browser.page_source, 'html.parser')
            content = soup.get_text(strip=True)
            urls = [
                "https://guncelkesintiler.com" + a.get("href") if a.get("href").startswith("/") else a.get("href")
                for a in soup.find_all("a", href=True)
                if not a.get("href").startswith(("api", "cdn", "static"))
            ]
            news_content.append(
                GuncelkesintilerResult(
                    title=self.browser.title,
                    content=content,
                    url=news_url_result.url,
                    hash=news_url_result.hash,
                    hash_type=news_url_result.hash_type,
                    urls=urls
                )
            )
        return news_content

    def close(self):
        self.browser.quit()


__all__ = "GuncelkesintilerScraper", "GuncelkesintilerResult"