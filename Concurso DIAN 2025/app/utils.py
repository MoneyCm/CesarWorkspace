import streamlit as st
import os

def load_css(file_name="app/styles.css"):
    # Fix path if running from pages/
    if not os.path.exists(file_name) and os.path.exists(f"../{file_name}"):
        file_name = f"../{file_name}"
        
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def show_logo():
    # Use absolute path relative to this file (utils.py is in app/)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(base_dir, "assets", "dian_logo.svg")
    
    if os.path.exists(logo_path):
        # Read SVG content
        with open(logo_path, "r") as f:
            svg_content = f.read()
        # Render as HTML - cleaner and no path issues for browser
        st.sidebar.markdown(
            f"""
            <div class="dian-logo" style="display: flex; justify-content: center; margin-bottom: 40px; width: 100%;">
                {svg_content}
            </div>
            """, 
            unsafe_allow_html=True
        )
    else:
        # Fallback debug title
        st.sidebar.warning(f"Logo not found at: {logo_path}")
        st.sidebar.title("DIAN Sim")

def setup_page(title="DIAN Sim"):
    # st.set_page_config must be called first in the main script, so we assume it's called there.
    # But we can update title/icon dynamically if needed, though limited.
    load_css()
    show_logo()
