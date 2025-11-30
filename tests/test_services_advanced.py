import pytest
from unittest.mock import MagicMock
from src.services import DashboardService
import pandas as pd
from datetime import datetime

def test_get_feed_activity_stats():
    mock_db = MagicMock()

    # Mock result list as tuples (feed_title, category_title, new_articles_count)
    # This matches the SQL query selection order
    row1 = ("TechCrunch", "Tech", 50)

    # Setup query chain mock
    mock_db.query.return_value.join.return_value.join.return_value.outerjoin.return_value.filter.return_value.group_by.return_value.order_by.return_value.all.return_value = [row1]

    service = DashboardService(db=mock_db, user_id=1)
    df = service.get_feed_activity_stats(days=30)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert df.iloc[0]['feed_title'] == "TechCrunch"
    assert df.iloc[0]['new_articles_count'] == 50

def test_get_dormant_feeds():
    mock_db = MagicMock()

    # Mock result list as tuples (feed_title, last_entry_date)
    row1 = ("Old Feed", datetime(2020, 1, 1))

    # Fix the comparison error:
    # subquery.c.last_entry_date returns a Column element in real SQLA, which supports < comparisons.
    # In Mock, it returns a Mock. We need to mock the *creation* of the subquery so that
    # the filter condition doesn't crash Python.

    # However, mocking the expression construction `subquery.c.last_entry_date < date` is hard.
    # Instead, we will mock the `subquery` method on the query object to return a special MagicMock
    # that implements __lt__ (less than).

    subquery_mock = MagicMock()
    subquery_mock.c.last_entry_date.__lt__.return_value = True # Return a truthy value or Expression mock
    subquery_mock.c.last_entry_date.__eq__.return_value = True # For None check

    # The first query() call creates the subquery definition
    mock_db.query.return_value.join.return_value.filter.return_value.group_by.return_value.subquery.return_value = subquery_mock

    # The second query() call (the main one) returns the results
    # We need to distinguish between the calls.
    # A simple way is to mock the final .all() return on the main chain.

    # The main chain is roughly: db.query().outerjoin().filter().order_by().all()
    mock_db.query.return_value.outerjoin.return_value.filter.return_value.order_by.return_value.all.return_value = [row1]

    service = DashboardService(db=mock_db, user_id=1)
    df = service.get_dormant_feeds()

    assert len(df) == 1
    assert df.iloc[0]['feed_title'] == "Old Feed"

def test_get_read_ratio_recent():
    mock_db = MagicMock()

    # Results are accessed as attributes (named tuples-like) in the service code for this method:
    # r.total_articles, r.read_articles
    row1 = MagicMock()
    row1.feed_title = "Popular Feed"
    row1.total_articles = 10
    row1.read_articles = 8

    mock_db.query.return_value.join.return_value.join.return_value.filter.return_value.group_by.return_value.having.return_value.all.return_value = [row1]

    service = DashboardService(db=mock_db, user_id=1)
    df = service.get_read_ratio_recent()

    assert len(df) == 1
    assert df.iloc[0]['read_ratio'] == 80.0
