from typing import List, Dict, Any, Tuple
from sqlalchemy import func, desc, case, text
from sqlalchemy.orm import Session
import jieba
from collections import Counter
from datetime import datetime, timedelta
import pandas as pd

from src.models import Feed, UserEntry, FeedCategory, Label, Entry

class DashboardService:
    def __init__(self, db: Session, user_id: int = 1):
        self.db = db
        self.user_id = user_id

    def get_global_stats(self) -> Dict[str, int]:
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
        entries = self.db.query(Entry.title)\
            .join(UserEntry, UserEntry.ref_id == Entry.id)\
            .filter(UserEntry.feed_id == feed_id, UserEntry.owner_uid == self.user_id)\
            .order_by(desc(Entry.date_entered))\
            .limit(200)\
            .all()

        titles = [e.title for e in entries]
        words = []
        for title in titles:
            seg_list = jieba.cut(title)
            for word in seg_list:
                if len(word.strip()) > 1:
                    words.append(word.strip())
        return Counter(words).most_common(limit)

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

    # --- New Metrics ---

    def get_feed_activity_stats(self, days: int = 30) -> pd.DataFrame:
        """
        Returns number of new articles per feed in the last X days.
        """
        import pandas as pd
        cutoff_date = datetime.now() - timedelta(days=days)

        results = self.db.query(
            Feed.title.label('feed_title'),
            FeedCategory.title.label('category_title'),
            func.count(UserEntry.int_id).label('new_articles_count')
        ).join(UserEntry, UserEntry.feed_id == Feed.id)\
         .join(Entry, UserEntry.ref_id == Entry.id)\
         .outerjoin(FeedCategory, Feed.cat_id == FeedCategory.id)\
         .filter(
             UserEntry.owner_uid == self.user_id,
             Entry.date_entered >= cutoff_date
         )\
         .group_by(Feed.id, Feed.title, FeedCategory.title)\
         .order_by(desc('new_articles_count'))\
         .all()

        return pd.DataFrame(results, columns=['feed_title', 'category_title', 'new_articles_count'])

    def get_dormant_feeds(self, threshold_days: int = 180) -> pd.DataFrame:
        """
        Returns feeds that haven't had a new article in over X days.
        """
        import pandas as pd

        # Subquery to get max date per feed
        subquery = self.db.query(
            UserEntry.feed_id,
            func.max(Entry.date_entered).label('last_entry_date')
        ).join(Entry, UserEntry.ref_id == Entry.id)\
         .filter(UserEntry.owner_uid == self.user_id)\
         .group_by(UserEntry.feed_id)\
         .subquery()

        cutoff_date = datetime.now() - timedelta(days=threshold_days)

        results = self.db.query(
            Feed.title.label('feed_title'),
            subquery.c.last_entry_date
        ).outerjoin(subquery, Feed.id == subquery.c.feed_id)\
         .filter(
             Feed.owner_uid == self.user_id,
             (subquery.c.last_entry_date < cutoff_date) | (subquery.c.last_entry_date == None)
         )\
         .order_by(subquery.c.last_entry_date.asc())\
         .all()

        return pd.DataFrame(results, columns=['feed_title', 'last_entry_date'])

    def get_read_ratio_recent(self, days: int = 30) -> pd.DataFrame:
        """
        Calculates the read ratio (read / total) for articles from the last X days per feed.
        """
        import pandas as pd
        cutoff_date = datetime.now() - timedelta(days=days)

        # Count total and read
        # sum(case unread=false then 1 else 0) / count(*)

        results = self.db.query(
            Feed.title.label('feed_title'),
            func.count(UserEntry.int_id).label('total_articles'),
            func.sum(case((UserEntry.unread == False, 1), else_=0)).label('read_articles')
        ).join(UserEntry, UserEntry.feed_id == Feed.id)\
         .join(Entry, UserEntry.ref_id == Entry.id)\
         .filter(
             UserEntry.owner_uid == self.user_id,
             Entry.date_entered >= cutoff_date
         )\
         .group_by(Feed.id, Feed.title)\
         .having(func.count(UserEntry.int_id) > 0)\
         .all()

        data = []
        for r in results:
            total = r.total_articles
            read = r.read_articles or 0
            ratio = (read / total) * 100 if total > 0 else 0
            data.append({
                "feed_title": r.feed_title,
                "total_articles": total,
                "read_articles": read,
                "read_ratio": ratio
            })

        return pd.DataFrame(data).sort_values(by='read_ratio', ascending=False)

    def get_engagement_metrics(self, days: int = 90) -> pd.DataFrame:
        """
        Analyzes time-to-read latency.
        Only considers articles that have been marked as read.
        """
        import pandas as pd
        cutoff_date = datetime.now() - timedelta(days=days)

        # We need dialect specific timestamp diff usually, but python post-processing is safer for cross-db
        # Fetch raw dates for read articles
        results = self.db.query(
            Feed.title.label('feed_title'),
            Entry.date_entered,
            UserEntry.last_read
        ).join(UserEntry, UserEntry.feed_id == Feed.id)\
         .join(Entry, UserEntry.ref_id == Entry.id)\
         .filter(
             UserEntry.owner_uid == self.user_id,
             UserEntry.unread == False,
             UserEntry.last_read.isnot(None),
             Entry.date_entered >= cutoff_date
         ).all()

        # Process in Python
        feed_stats = {}

        for r in results:
            title = r.feed_title
            entered = r.date_entered
            read = r.last_read

            if read < entered:
                continue # Should not happen usually, maybe system clock issues

            diff_hours = (read - entered).total_seconds() / 3600.0

            if title not in feed_stats:
                feed_stats[title] = []
            feed_stats[title].append(diff_hours)

        data = []
        for title, diffs in feed_stats.items():
            avg_hours = sum(diffs) / len(diffs)
            data.append({
                "feed_title": title,
                "read_count": len(diffs),
                "avg_hours_to_read": avg_hours
            })

        return pd.DataFrame(data).sort_values(by='avg_hours_to_read', ascending=True)
