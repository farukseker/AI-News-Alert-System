from scrapers import GuncelkesintilerScraper, GuncelkesintilerResult
from .base_task import BaseTask
from models import News
from logging_config import get_logger


logger = get_logger(__name__)


class GuncelkesintilerTask(BaseTask):

    def __init__(self, db_session, **kwargs):
        super().__init__()
        self.db_session = db_session

    def do(self):
        scraper = GuncelkesintilerScraper()
        try:
            target_news_list: list[GuncelkesintilerResult] = []

            pre_news_url_list = scraper.get_news_url_list()
            session = self.db_session.session()
            for news_url in pre_news_url_list:
                if not session.query(News).filter(News.content_hash == news_url.hash).exists():
                    target_news_list.append(news_url)

            news_url_results = scraper.get_news_content(target_news_list)

        except Exception as e:
            logger.error(e)
            self._set_error()
        finally:
            scraper.close()
