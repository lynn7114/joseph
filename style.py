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

def set_custom_fonts(bold_font_file, bold_font_name, regular_font_file, regular_font_name):
    with open(bold_font_file, "rb") as f1:
        bold_encoded = base64.b64encode(f1.read()).decode()

    with open(regular_font_file, "rb") as f2:
        regular_encoded = base64.b64encode(f2.read()).decode()

    st.markdown(
        f"""
        <style>
        /* Bold 폰트 */
        @font-face {{
            font-family: '{bold_font_name}';
            src: url(data:font/ttf;base64,{bold_encoded}) format('truetype');
            font-weight: bold;
            font-style: normal;
        }}

        /* Regular 폰트 */
        @font-face {{
            font-family: '{regular_font_name}';
            src: url(data:font/ttf;base64,{regular_encoded}) format('truetype');
            font-weight: normal;
            font-style: normal;
        }}

        /* 전체 텍스트 기본은 Regular */
        html, body, .stApp {{
            font-family: '{regular_font_name}', sans-serif;
            color: black;
        }}

        /* 제목은 Bold 폰트 적용 */
        h1, h2, h3 {{
            font-family: '{bold_font_name}', sans-serif;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
