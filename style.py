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

import base64
import streamlit as st

def set_custom_fonts(bold_font_file, bold_font_name, regular_font_file, regular_font_name):
    with open(bold_font_file, "rb") as f1:
        bold_encoded = base64.b64encode(f1.read()).decode()

    with open(regular_font_file, "rb") as f2:
        regular_encoded = base64.b64encode(f2.read()).decode()

    st.markdown(
        f"""
        <style>
        /* ===== 폰트 임포트 ===== */
        @font-face {{
            font-family: '{bold_font_name}';
            src: url(data:font/ttf;base64,{bold_encoded}) format('truetype');
            font-weight: bold;
        }}
        @font-face {{
            font-family: '{regular_font_name}';
            src: url(data:font/ttf;base64,{regular_encoded}) format('truetype');
            font-weight: normal;
        }}

        /* ===== 전역 텍스트 스타일 ===== */
        html, body, .stApp, .block-container {{
            font-family: '{regular_font_name}', sans-serif;
            color: black;
            background-color: rgba(255, 255, 255, 0.0); /* 투명 배경 */
        }}

        /* 제목 스타일 - 볼드체 적용 */
        h1, h2, h3 {{
            font-family: '{bold_font_name}', sans-serif;
            font-weight: bold;
        }}

        /* 필요 시 다른 위젯 클래스 추가 커스터마이징 */
        .stMarkdown, .stTextInput, .stChatInput {{
            font-family: '{regular_font_name}', sans-serif;
            color: black;
            background-color: rgba(255, 255, 255, 0.6); /* 약간 투명한 흰 배경 */
            border-radius: 10px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
