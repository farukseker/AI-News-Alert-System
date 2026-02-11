from ddgs import DDGS

from datetime import datetime

from models import News

from logging_config import get_logger
from scrapers import SearchScraper, SearchResult
from ai_agents import analyze_news
from . import BaseTask


logger = get_logger(__name__)


class NewsSearchTask(BaseTask):
    def __init__(self, session):
        super().__init__()
        self.db_session = session

    def do(self):
        scraper = SearchScraper()

        search_list: list[dict] = []
        search_list_uniq: set[str] = set()
        news_url_results: list[News] = []
        search_keywords: list[str] = [
            'Bursa Orhangazi sondakika haberler',
            'Bursa Orhangazi su kesintileri',
            'Bursa Orhangazi elektrik kesintileri',
            'Bursa Orhangazi doğalgaz kesintileri',
        ]

        for search_keyword in search_keywords:
            for search_result in DDGS().text(query=search_keyword, region='tr-tr', max_results=3):
                if (href := search_result.get('href')) not in search_list_uniq:
                    search_list_uniq.add(href)
                    search_list.append(search_result)

        if len(search_list_uniq) > 0:
            try:
                for search_result in search_list:
                    result: SearchResult | None = scraper.fetch(search_result.get('href'))
                    if result is not None:
                        exists_criteria = self.db_session.query(News).filter(News.content_hash == result.hash).exists()
                        if not self.db_session.query(exists_criteria).scalar():
                            r = analyze_news(
                                text=result.content,
                                now=datetime.now().isoformat(),
                                urls=[],
                            )
                            new = News(
                                url=result.url,
                                title=result.title,
                                content_hash=result.hash,
                                is_trustable=r.confidence >= .80,
                                confidence=r.confidence,
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

__all__ = 'NewsSearchTask',