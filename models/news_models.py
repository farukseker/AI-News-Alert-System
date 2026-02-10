from sqlalchemy import Column, String, Integer, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base


NewsBase = declarative_base()


class News(NewsBase):
    __tablename__ = 'news'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    url = Column(String)
    content_hash = Column(String)
    is_trustable = Column(Boolean)

    created_at = Column(DateTime)
    updated_at = Column(DateTime)


__all__ = 'News', 'NewsBase'