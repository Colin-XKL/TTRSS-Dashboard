import pytest
from unittest.mock import MagicMock
from src.services import DashboardService
from src.models import Feed, UserEntry, Label

def test_global_stats():
    # Mock Database Session
    mock_db = MagicMock()

    # Setup return values for scalar() calls
    # We call scalar() 4 times in get_global_stats
    # Order: feed_count, unread_count, label_count, starred_count
    mock_db.query.return_value.filter.return_value.scalar.side_effect = [10, 5, 3, 2]

    service = DashboardService(db=mock_db, user_id=1)
    stats = service.get_global_stats()

    assert stats["feed_count"] == 10
    assert stats["unread_count"] == 5
    assert stats["label_count"] == 3
    assert stats["starred_count"] == 2

def test_get_feeds_by_category():
    mock_db = MagicMock()

    # Mock result objects
    row1 = MagicMock()
    row1.title = "Tech"
    row1.feed_count = 5

    row2 = MagicMock()
    row2.title = "News"
    row2.feed_count = 8

    mock_db.query.return_value.join.return_value.filter.return_value.group_by.return_value.all.return_value = [row1, row2]

    service = DashboardService(db=mock_db, user_id=1)
    results = service.get_feeds_by_category()

    assert len(results) == 2
    assert results[0]["category"] == "Tech"
    assert results[0]["count"] == 5
