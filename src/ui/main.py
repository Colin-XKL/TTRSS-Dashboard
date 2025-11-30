import streamlit as st
from streamlit_option_menu import option_menu

from src.database import get_db
from src.ui.dashboard import render_dashboard
from src.ui.analysis import render_analysis

def main():
    st.set_page_config(
        page_title="TTRSS Dashboard",
        page_icon="📰",
        layout="wide"
    )

    # Initialize DB Session
    # In a real app, we might want to handle session lifecycle better (e.g. per request)
    # For Streamlit, we can instantiate it at the start of the script run.
    try:
        db = get_db()
    except Exception as e:
        st.error(f"Could not connect to database: {e}")
        st.stop()

    with st.sidebar:
        st.title("TTRSS Analytics")
        selected = option_menu(
            menu_title="Navigation",
            options=["Dashboard", "Feed Analysis", "About"],
            icons=["speedometer2", "graph-up", "info-circle"],
            menu_icon="cast",
            default_index=0,
        )

        st.divider()
        st.caption("Connected to Database")

    if selected == "Dashboard":
        render_dashboard(db)
    elif selected == "Feed Analysis":
        render_analysis(db)
    elif selected == "About":
        st.header("About")
        st.markdown("""
        **TTRSS Dashboard** is a modern analytics interface for Tiny Tiny RSS.

        Built with:
        - [Streamlit](https://streamlit.io)
        - [SQLAlchemy](https://www.sqlalchemy.org/)
        - [Plotly](https://plotly.com/)
        """)

    db.close()

if __name__ == "__main__":
    main()
