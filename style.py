import streamlit as st

def set_background():
    st.markdown("""
        <style>
        body {
            background-image: url("https://images.unsplash.com/photo-...");
            background-size: cover;
            background-attachment: fixed;
        }
        </style>
    """, unsafe_allow_html=True)
