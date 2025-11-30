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

    # Charts
    st.subheader("Feeds Distribution")

    cat_data = service.get_feeds_by_category()
    if cat_data:
        df = pd.DataFrame(cat_data)

        # Two columns for charts
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
