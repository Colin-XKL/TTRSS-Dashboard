from typing import List, Dict, Any, Tuple
from sqlalchemy import func, desc
from sqlalchemy.orm import Session
import jieba
from collections import Counter

from src.models import Feed, UserEntry, FeedCategory, Label, Entry

class DashboardService:
    def __init__(self, db: Session, user_id: int = 1):
        # Defaulting to user_id=1 (usually admin) for single-user dashboard scenarios
        self.db = db
        self.user_id = user_id

    def get_global_stats(self) -> Dict[str, int]:
        """
        Returns high-level statistics for the dashboard.
        """
        feed_count = self.db.query(func.count(Feed.id))\
            .filter(Feed.owner_uid == self.user_id).scalar()

        unread_count = self.db.query(func.count(UserEntry.int_id))\
            .filter(UserEntry.owner_uid == self.user_id, UserEntry.unread == True).scalar()

        label_count = self.db.query(func.count(Label.id))\
            .filter(Label.owner_uid == self.user_id).scalar()

        starred_count = self.db.query(func.count(UserEntry.int_id))\
            .filter(UserEntry.owner_uid == self.user_id, UserEntry.marked == True).scalar()

        return {
            "feed_count": feed_count or 0,
            "unread_count": unread_count or 0,
            "label_count": label_count or 0,
            "starred_count": starred_count or 0
        }

    def get_feeds_by_category(self) -> List[Dict[str, Any]]:
        """
        Returns a breakdown of feeds per category.
        """
        results = self.db.query(
            FeedCategory.title,
            func.count(Feed.id).label('feed_count')
        ).join(Feed, Feed.cat_id == FeedCategory.id)\
         .filter(FeedCategory.owner_uid == self.user_id)\
         .group_by(FeedCategory.id, FeedCategory.title)\
         .all()

        return [{"category": r.title, "count": r.feed_count} for r in results]

    def get_all_categories(self) -> List[FeedCategory]:
        return self.db.query(FeedCategory).filter(FeedCategory.owner_uid == self.user_id).all()

    def get_feeds_in_category(self, cat_id: int) -> List[Feed]:
        return self.db.query(Feed).filter(
            Feed.owner_uid == self.user_id,
            Feed.cat_id == cat_id
        ).all()

    def get_feed_word_frequency(self, feed_id: int, limit: int = 100) -> List[Tuple[str, int]]:
        """
        Fetches titles from a specific feed, tokenizes them, and returns word frequency.
        """
        # Join UserEntry -> Entry to get titles
        entries = self.db.query(Entry.title)\
            .join(UserEntry, UserEntry.ref_id == Entry.id)\
            .filter(UserEntry.feed_id == feed_id, UserEntry.owner_uid == self.user_id)\
            .order_by(desc(Entry.date_entered))\
            .limit(200)\
            .all()

        titles = [e.title for e in entries]

        words = []
        for title in titles:
            # Using jieba for Chinese support (as seen in original code)
            # It works reasonably well for English too
            seg_list = jieba.cut(title)
            for word in seg_list:
                if len(word.strip()) > 1: # Filter out single chars/spaces
                    words.append(word.strip())

        counter = Counter(words)
        return counter.most_common(limit)

    def get_recent_entries(self, feed_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        results = self.db.query(Entry, UserEntry)\
            .join(UserEntry, UserEntry.ref_id == Entry.id)\
            .filter(UserEntry.feed_id == feed_id, UserEntry.owner_uid == self.user_id)\
            .order_by(desc(Entry.date_entered))\
            .limit(limit)\
            .all()

        return [
            {
                "title": r.Entry.title,
                "date": r.Entry.date_entered,
                "unread": r.UserEntry.unread,
                "marked": r.UserEntry.marked
            }
            for r in results
        ]
