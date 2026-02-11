from datetime import datetime

from scrapers import UedasScraper, UedasResult
from models import News

from logging_config import get_logger

from ai_agents import analyze_news
from .base_task import BaseTask


logger = get_logger(__name__)


class UedasTask(BaseTask):

    def __init__(self, db_session, **kwargs):
        super().__init__()
        self.db_session = db_session

    def do(self):
        scraper = UedasScraper()
        news_url_results: list[News] = []

        try:
            scraper.get_trigger_start_point()

            pre_uedas_new_list: list[UedasResult] = []

            if global_trigger_start_point := scraper.get_global_trigger_start_point():
                pre_uedas_new_list.append(
                    global_trigger_start_point
                )

            pre_uedas_new_list.extend(
                scraper.get_others_hometowns_points()
            )

            target_news_list: list[UedasResult] = []
            target_news_hash_list: set = set()

            for news_url in pre_uedas_new_list:
                if not news_url.hash in target_news_hash_list:
                    target_news_hash_list.add(news_url.hash)
                    exists_criteria = self.db_session.query(News).filter(News.content_hash == news_url.hash).exists()
                    if not self.db_session.query(exists_criteria).scalar():
                        target_news_list.append(news_url)


            for news_url in target_news_list:
                logger.info(f'from {self.__class__.__name__}:do > start analyze_news on {news_url.url}')
                r = analyze_news(
                    text=news_url.content,
                    now=datetime.now().isoformat(),
                    urls=[]
                )
                new = News(
                    url=news_url.url,
                    content_hash=news_url.hash,
                    is_trustable=r.confidence >= .80,
                    summary=r.summary,
                )
                news_url_results.append(new)

                logger.info(f'from {self.__class__.__name__}:do > analyze_news result output type{type(r)}')

        except Exception as e:
            logger.error(f'log from {self.__class__.__name__}:do > error {e}')
            self._set_error()

        finally:
            self.db_session.add_all(news_url_results)
            self.db_session.commit()
            self.db_session.close()

            scraper.quit()
            logger.info(f'from {self.__class__.__name__}:do > analyze_news final')


__all__ = 'UedasTask',