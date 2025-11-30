import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
from sqlalchemy.orm import Session
from src.services import DashboardService

def render_analysis(db: Session):
    st.title("Deep Analysis")

    service = DashboardService(db)

    tabs = st.tabs(["Single Feed Analysis", "Engagement & Quality"])

    # --- Tab 1: Original Single Feed Analysis ---
    with tabs[0]:
        # 1. Select Category
        categories = service.get_all_categories()
        if not categories:
            st.warning("No categories found.")
            return

        cat_options = {c.title: c.id for c in categories}
        selected_cat_name = st.selectbox("Select Category", list(cat_options.keys()))
        selected_cat_id = cat_options[selected_cat_name]

        # 2. Select Feed
        feeds = service.get_feeds_in_category(selected_cat_id)
        if not feeds:
            st.info("No feeds in this category.")
        else:
            feed_options = {f.title: f.id for f in feeds}
            selected_feed_name = st.selectbox("Select Feed", list(feed_options.keys()))
            selected_feed_id = feed_options[selected_feed_name]

            st.markdown("---")
            st.subheader(f"Analysis: {selected_feed_name}")

            subtabs = st.tabs(["Word Frequency", "Recent Articles"])

            with subtabs[0]:
                freq_data = service.get_feed_word_frequency(selected_feed_id)
                if freq_data:
                    word_dict = dict(freq_data)
                    wc = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(word_dict)
                    st.image(wc.to_array(), caption="Word Cloud of Recent Headlines", use_container_width=True)

                    df_freq = pd.DataFrame(freq_data, columns=["Word", "Count"]).head(20)
                    fig = px.bar(df_freq, x='Word', y='Count', title="Top 20 Words")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Not enough data for word frequency analysis.")

            with subtabs[1]:
                recent = service.get_recent_entries(selected_feed_id)
                if recent:
                    df_recent = pd.DataFrame(recent)
                    st.dataframe(df_recent, use_container_width=True)
                else:
                    st.info("No recent articles found.")

    # --- Tab 2: Engagement & Quality (New) ---
    with tabs[1]:
        st.header("Engagement & Reading Habits")

        # 1. Read Ratio
        st.subheader("Read Ratio (Last 30 Days)")
        st.caption("Percentage of new articles marked as read.")

        ratio_df = service.get_read_ratio_recent(days=30)

        if not ratio_df.empty:
            # Scatter plot: Volume vs Ratio
            fig_scatter = px.scatter(
                ratio_df,
                x='total_articles',
                y='read_ratio',
                hover_name='feed_title',
                size='total_articles',
                title="Read Ratio vs Volume",
                labels={'total_articles': 'Total Articles', 'read_ratio': 'Read Ratio (%)'}
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

            # Table
            st.dataframe(ratio_df, use_container_width=True)
        else:
            st.info("No data available for read ratio analysis.")

        st.markdown("---")

        # 2. Reading Latency
        st.subheader("Reading Latency (Interest Level)")
        st.caption("Average time between article arrival and you reading it (for read articles).")

        latency_df = service.get_engagement_metrics(days=90)

        if not latency_df.empty:
            c1, c2 = st.columns(2)

            with c1:
                st.markdown("##### High Interest (Quickest to Read)")
                st.dataframe(latency_df.head(10), use_container_width=True)

            with c2:
                st.markdown("##### Low Interest / Backlog (Slowest to Read)")
                st.dataframe(latency_df.tail(10).iloc[::-1], use_container_width=True) # Reverse to show slowest first
        else:
            st.info("No reading history found in the last 90 days.")
