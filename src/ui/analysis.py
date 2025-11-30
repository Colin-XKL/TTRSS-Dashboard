import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from sqlalchemy.orm import Session
from src.services import DashboardService

def render_analysis(db: Session):
    st.title("Feed Analysis")

    service = DashboardService(db)

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
        return

    feed_options = {f.title: f.id for f in feeds}
    selected_feed_name = st.selectbox("Select Feed", list(feed_options.keys()))
    selected_feed_id = feed_options[selected_feed_name]

    st.markdown("---")

    # Analysis
    st.subheader(f"Analysis: {selected_feed_name}")

    tab1, tab2 = st.tabs(["Word Frequency", "Recent Articles"])

    with tab1:
        freq_data = service.get_feed_word_frequency(selected_feed_id)
        if freq_data:
            # Word Cloud
            word_dict = dict(freq_data)
            wc = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(word_dict)

            st.image(wc.to_array(), caption="Word Cloud of Recent Headlines", use_container_width=True)

            # Bar Chart
            df_freq = pd.DataFrame(freq_data, columns=["Word", "Count"]).head(20)
            fig = px.bar(df_freq, x='Word', y='Count', title="Top 20 Words")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Not enough data for word frequency analysis.")

    with tab2:
        recent = service.get_recent_entries(selected_feed_id)
        if recent:
            df_recent = pd.DataFrame(recent)
            st.dataframe(df_recent, use_container_width=True)
        else:
            st.info("No recent articles found.")
