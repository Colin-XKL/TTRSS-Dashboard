import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy.orm import Session
from src.services import DashboardService

def render_dashboard(db: Session):
    st.title("Dashboard")

    service = DashboardService(db)
    stats = service.get_global_stats()

    # Top metrics row
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Feeds", stats["feed_count"])
    c2.metric("Unread Articles", stats["unread_count"])
    c3.metric("Labels", stats["label_count"])
    c4.metric("Starred", stats["starred_count"])

    st.markdown("---")

    # 1. Feeds Distribution
    st.subheader("Feeds Distribution")
    cat_data = service.get_feeds_by_category()
    if cat_data:
        df = pd.DataFrame(cat_data)
        col1, col2 = st.columns(2)
        with col1:
            st.caption("Feeds per Category (Bar)")
            fig_bar = px.bar(df, x='category', y='count', title="Feed Count by Category")
            st.plotly_chart(fig_bar, use_container_width=True)
        with col2:
            st.caption("Feeds per Category (Pie)")
            fig_pie = px.pie(df, values='count', names='category', title="Feed Distribution")
            st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("No category data found.")

    st.markdown("---")

    # 2. Activity Overview (New)
    st.subheader("Activity Overview (Last 30 Days)")

    activity_df = service.get_feed_activity_stats(days=30)
    if not activity_df.empty:
        # Top 10 Active Feeds
        top_active = activity_df.head(10)
        fig_active = px.bar(
            top_active,
            x='new_articles_count',
            y='feed_title',
            orientation='h',
            title="Top 10 Most Active Feeds",
            labels={'new_articles_count': 'New Articles', 'feed_title': 'Feed'}
        )
        fig_active.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_active, use_container_width=True)

        with st.expander("View Full Activity Data"):
            st.dataframe(activity_df, use_container_width=True)
    else:
        st.info("No activity detected in the last 30 days.")

    # 3. Dormant Feeds (New)
    st.subheader("Dormant Feeds (> 6 Months)")
    dormant_df = service.get_dormant_feeds(threshold_days=180)
    if not dormant_df.empty:
        st.warning(f"Found {len(dormant_df)} feeds with no updates in 6 months.")
        st.dataframe(dormant_df, use_container_width=True)
    else:
        st.success("No dormant feeds found. All feeds are healthy!")
