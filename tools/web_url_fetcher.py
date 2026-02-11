import time

from langchain.tools import tool

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from bs4 import BeautifulSoup

from pydantic import BaseModel, Field, field_validator

from config import  get_settings


settings = get_settings()


class WebUrlFetcherInput(BaseModel):
    url: str = Field(..., description="The URL to fetch content from")

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        v = v.strip()
        if not v.startswith(("http://", "https://")):
            raise ValueError(f"Invalid URL - must start with http:// or https://, got: {v!r}")
        if v in ("https://...", "http://..."):
            raise ValueError(f"Invalid URL - placeholder value detected: {v!r}")
        if v.startswith("https://www.example.com/"):
            raise ValueError(f"Invalid URL - must be sourced by 'candidate_urls' in your messages or prompts: {v!r}")
        return v

@tool(
    description="Fetch a web page using a headless browser and return the visible text content with ads blocked."
                "you can  use only 3 times is important 'cause other events blocked",
    args_schema=WebUrlFetcherInput,
)
def web_url_fetcher(url: str) -> str:

    print('web_url_fetcher: entry')


    print('web_url_fetcher: ', url)
    browser = None
    try:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")

        # browser = webdriver.Chrome(options=options)
        # client_config = ClientConfig(
        #     remote_server_addr='http://selenium_hub:4444/wd/hub',
        # )

        browser = webdriver.Remote(
            options=options,
            # client_config=client_config,
            command_executor=settings.SELENIUM_REMOTE_SERVER_HOST,
            # desired_capabilities=DesiredCapabilities.CHROME
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

        browser.get(url)
        time.sleep(5)
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        return 'page context: ' + soup.get_text(strip=True)

    except Exception as e:
        return f"ERROR - Could not fetch URL {url!r}: {e}"

    finally:
        if browser is not None:
            browser.close()
            browser.quit()


__all__ = 'web_url_fetcher',