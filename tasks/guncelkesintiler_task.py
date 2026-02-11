from datetime import datetime

from scrapers import GuncelkesintilerScraper, GuncelkesintilerResult
from models import News

from logging_config import get_logger

from ai_agents import analyze_news
from .base_task import BaseTask


logger = get_logger(__name__)


class GuncelkesintilerTask(BaseTask):

    def __init__(self, db_session, **kwargs):
        super().__init__()
        self.db_session = db_session

    def do(self):
        scraper = GuncelkesintilerScraper()
        news_url_results: list[News] = []

        try:
            pre_news_url_list = scraper.get_news_url_list()

            target_news_list_swap: list[GuncelkesintilerResult] = []
            target_news_list: list[GuncelkesintilerResult] = []
            target_news_uniq_url_list: set = set()

            for news_url in pre_news_url_list:
                if news_url.hash not in target_news_uniq_url_list:
                    target_news_uniq_url_list.add(news_url.url)
                    target_news_list_swap.append(news_url)


            for news_url in target_news_list_swap:
                exists_criteria = self.db_session.query(News).filter(News.content_hash == news_url.hash).exists()
                if not self.db_session.query(exists_criteria).scalar():
                    target_news_list.append(news_url)


            for news_url in  scraper.get_news_content(target_news_list):
                logger.info(f'from {self.__class__.__name__}:do > start analyze_news on {news_url.url}')
                r = analyze_news(
                    text=news_url.content,
                    now=datetime.now().isoformat(),
                    urls=news_url.urls,
                )
                new = News(
                    url=news_url.url,
                    title=news_url.title,
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
            news_url_results_hash: set[str] = set()
            _news_url_results: list[News] = []

            for new in news_url_results:
                if new.content_hash not in news_url_results_hash:
                    _news_url_results.append(new)
                    news_url_results_hash.add(new.content_hash)

            self.db_session.add_all(_news_url_results)
            self.db_session.commit()
            self.db_session.close()

            scraper.close()
            logger.info(f'from {self.__class__.__name__}:do > analyze_news final')

__all__ = 'GuncelkesintilerTask',