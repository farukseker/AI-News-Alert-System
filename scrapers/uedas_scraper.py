import requests
from bs4 import BeautifulSoup

from dataclasses import dataclass
from hashlib import sha256
from time import sleep
import re

from logging_config import get_logger


logger = get_logger(f'{__name__}.UedasScraper')


@dataclass
class UedasResult:
    url: str
    hash: str
    hash_type: str
    content: str | None = None


HOMETOWNS_LIST: list[str] =  [
    '184631', '20072', '184633', '20073', '184635', '184621', '184637', '184639', '20077', '184641',
    '184643', '184645', '184647', '184649', '184651', '184653', '20074', '184655', '184657', '184659',
    '20075', '184623', '184661', '184663', '184665', '184625', '20076', '184667', '184669', '184627',
    '184629'
]

class UedasScraper:
    def __init__(self):
        self.session = requests.Session()

        self.global_api_headers: dict[str, str] = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept": "application/xml, text/xml, */*; q=0.01",
            "Origin": "https://www.uedas.com.tr",
            "Referer": "https://www.uedas.com.tr/tr/kesintiler",
        }

        self.api_endpoint: str = "https://www.uedas.com.tr"
        self.api_endpoint_url: str = 'https://www.uedas.com.tr/planli-kesintiler/sec.asp'


    @staticmethod
    def get_clean_text(text: str) -> str:
        cleaned = re.sub(r'\s+', ' ', text).strip()
        return cleaned

    def get_hash_from_request(self, context: str) -> str:
        h = sha256(context.encode('utf-8'))
        return h.hexdigest()

    def get_trigger_start_point(self):
        logger.info('trigger start point')
        self.session.get(
            "https://www.uedas.com.tr/planli-kesintiler/sec.asp",
            headers={
                "User-Agent": "Mozilla/5.0",
                "Referer": "https://www.uedas.com.tr/tr/kesintiler",
            },
        )
        logger.info('trigger start point - end')


    def get_global_trigger_start_point(self) -> UedasResult | None:
        request_data = {"il": "16", "ilce": "1554"}
        logger.info(f'get_global_trigger_start_point - {self.api_endpoint_url}')
        try:
            resp = self.session.post(
                self.api_endpoint_url,
                headers=self.global_api_headers,
                data=request_data
            )
            soup = BeautifulSoup(resp.content, 'lxml')
            cleaned_text = self.get_clean_text(soup.get_text(strip=True))
            return UedasResult(
                url=f'{self.api_endpoint_url}:{16}:{1554}',
                hash=self.get_hash_from_request(cleaned_text),
                hash_type='url+request-data+context',
                content=cleaned_text
            )
        except Exception as e:
            logger.error(f'get_global_trigger_start_point - {e}')
            return None
        finally:
            sleep(1)
            logger.info('trigger start point - end')

    def get_others_hometowns_point(self, hometown_point: str) -> UedasResult | None:
        logger.info(f'get_others_hometowns_point - {self.api_endpoint_url}:{hometown_point}')

        try:
            request_data = {"il": "16", "ilce": "1554", "mahalle": hometown_point}
            resp = self.session.post(
                self.api_endpoint_url,
                headers=self.global_api_headers,
                data=request_data
            )

            soup = BeautifulSoup(resp.content, 'lxml')
            if (context := soup.get_text(strip=True)) and (len(context) > 0):
                cleaned_text = self.get_clean_text(context)
                return UedasResult(
                    url=f'{self.api_endpoint_url}:{16}:{1554}:{hometown_point}',
                    hash=self.get_hash_from_request(cleaned_text),
                    hash_type='url+request-data+context',
                    content=cleaned_text
                )
        except Exception as e:
            logger.error(f'get_others_hometowns_point - {e}')
        finally:
            sleep(1)
            logger.info('get_others_hometowns_point - end')
        return None


    def get_others_hometowns_points(self) -> list[UedasResult]:
        logger.info(f'get_others_hometowns_points')
        hometowns_points_results: list[UedasResult] = []
        try:
            for hometown_point in HOMETOWNS_LIST:
                if resp := self.get_others_hometowns_point(
                        hometown_point=hometown_point,
                ):
                    hometowns_points_results.append(resp)
        except Exception as e:
            logger.error(f'get_others_hometowns_points - {e}')
        finally:
            return hometowns_points_results

    def quit(self) -> None:
        self.session.close()


__all__ = 'UedasScraper', 'UedasResult'