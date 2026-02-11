from sqlalchemy import Column, String, Integer, Boolean, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base


NewsBase = declarative_base()


class News(NewsBase):
    __tablename__ = 'news'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    url = Column(String)

    content_hash = Column(String, unique=True)

    summary = Column(String)

    confidence = Column(Float)

    is_trustable = Column(Boolean)
    is_evaluated = Column(Boolean, default=False)

    created_at = Column(DateTime)
    updated_at = Column(DateTime)


__all__ = 'News', 'NewsBase'