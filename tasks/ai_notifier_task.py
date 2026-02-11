from ai_agents.ai_email_copywriter import generate_email_html
from bs4 import BeautifulSoup

from models import News
from logging_config import get_logger
from mailsender import HtmlSmtpMailer
from config import get_settings
from . import BaseTask


logger = get_logger(__name__)
settings = get_settings()


class AiNotifierTask(BaseTask):
    def __init__(self, session):
        super().__init__()
        self.db_session = session

    def do(self):
        news = (
            self.db_session.query(News)
            .filter(
                News.is_evaluated.is_(False),
                News.confidence.__ge__(.60),
            )
            .all()
        )
        extracted_data = [
            {
                "piantik": new.is_trustable,
                "confidence": new.confidence,
                "summary": (new.title if new.title else '') + new.summary,
            }
            for new in news
        ]
        if extracted_data:
            html = generate_email_html(extracted_data)
            soup = BeautifulSoup(html, "html.parser")

            title = soup.find("title").get_text(strip=True)

            html_smtp_mailer: HtmlSmtpMailer = HtmlSmtpMailer(
                username=settings.SMTP_USERNAME,
                password=settings.SMTP_PASSWORD,
                host=settings.SMTP_DOMAIN,
                port=settings.SMTP_PORT,
            )

            html_smtp_mailer.send_html(
                subject=title,
                html_body=html,
                from_email=settings.SMTP_USERNAME,
                to_emails=settings.TO_EMAIL,
            )

            # Mark all processed news as evaluated
            for new in news:
                new.is_evaluated = True
            else:
                logger.info('news list empty')
            self.db_session.commit()


__all__ = "AiNotifierTask",