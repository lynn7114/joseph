import base64
import streamlit as st

def set_background(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def set_custom_font(font_file, font_family):
    with open(font_file, "rb") as f:
        encoded_font = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
        @font-face {{
            font-family: '{font_family}';
            src: url(data:font/ttf;base64,{encoded_font}) format('truetype');
            font-weight: normal;
            font-style: normal;
        }}

        html, body, .stApp {{
            font-family: '{font_family}', sans-serif;
            color: black; /* 글씨 색깔 검정 */
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
