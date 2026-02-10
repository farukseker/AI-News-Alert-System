from sqlalchemy import Column, String, Integer, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base


NewsAlertRecordBase = declarative_base()


class NewsAlertRecord(NewsAlertRecordBase):
    __tablename__ = 'news_alert'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    context = Column(String)
    html = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    is_delivered = Column(Boolean)

__all__ = 'NewsAlertRecord', 'NewsAlertRecordBase'