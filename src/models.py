from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'ttrss_users'
    id = Column(Integer, primary_key=True)
    login = Column(String(120), unique=True, nullable=False)
    # Add other fields as necessary

class FeedCategory(Base):
    __tablename__ = 'ttrss_feed_categories'
    id = Column(Integer, primary_key=True)
    owner_uid = Column(Integer, ForeignKey('ttrss_users.id'), nullable=False)
    title = Column(String(200), nullable=False)
    parent_cat = Column(Integer, ForeignKey('ttrss_feed_categories.id'), nullable=True)

    feeds = relationship("Feed", back_populates="category")

class Feed(Base):
    __tablename__ = 'ttrss_feeds'
    id = Column(Integer, primary_key=True)
    owner_uid = Column(Integer, ForeignKey('ttrss_users.id'), nullable=False)
    title = Column(String(200), nullable=False)
    cat_id = Column(Integer, ForeignKey('ttrss_feed_categories.id'), nullable=True)
    feed_url = Column(Text, nullable=False)
    last_updated = Column(DateTime)

    category = relationship("FeedCategory", back_populates="feeds")
    entries = relationship("UserEntry", back_populates="feed")

class Entry(Base):
    __tablename__ = 'ttrss_entries'
    id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    updated = Column(DateTime, nullable=False)
    date_entered = Column(DateTime, nullable=False)

    user_entries = relationship("UserEntry", back_populates="entry")

class UserEntry(Base):
    __tablename__ = 'ttrss_user_entries'
    int_id = Column(Integer, primary_key=True)
    ref_id = Column(Integer, ForeignKey('ttrss_entries.id'), nullable=False)
    feed_id = Column(Integer, ForeignKey('ttrss_feeds.id'), nullable=True)
    owner_uid = Column(Integer, ForeignKey('ttrss_users.id'), nullable=False)
    marked = Column(Boolean, default=False)
    published = Column(Boolean, default=False)
    unread = Column(Boolean, default=True)
    last_read = Column(DateTime)

    feed = relationship("Feed", back_populates="entries")
    entry = relationship("Entry", back_populates="user_entries")

class Label(Base):
    __tablename__ = 'ttrss_labels2'
    id = Column(Integer, primary_key=True)
    owner_uid = Column(Integer, ForeignKey('ttrss_users.id'), nullable=False)
    caption = Column(String(250), nullable=False)
    fg_color = Column(String(15), default='')
    bg_color = Column(String(15), default='')
