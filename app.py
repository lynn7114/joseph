import openai
import os
import json
import re
import docx
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from style import set_background, set_custom_fonts
from separate import separate_problems, parse_primary_level_questions, extract_units_individually_from_pdf, extract_units_from_excel
from pptx import Presentation

# API 키 로드
load_dotenv()
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# UI 세팅
set_background("anthony-delanoix-urUdKCxsTUI-unsplash.jpg")
set_custom_fonts("NanumBarunpenB.ttf", "NanumBarunpenB", "NanumBarunpenR.ttf", "NanumBarunpenR")

st.markdown("""
    <style>
    div.stButton > button {
        font-family: 'NanumBarunpenR', sans-serif;
        color: black !important;
        background-color: #85c1e9 !important;
        border: none;
        padding: 0.5em 1em;
        border-radius: 8px;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #aed6f1 !important;
        color: black !important;
    }
    div.stButton > button:active {
        background-color: #d6eaf8 !important;
        color: black !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <h1 style='font-family: NanumBarunpenB; font-size: 48px; color: black; text-align: center; margin-bottom: 30px;'>
        영어 변형 문제
    </h1>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": "너는 영어 문제를 변형해서 출제하는 도우미야."},
        {"role": "assistant", "content": "기출문제를 입력해주시면 변형 문제를 만들어드릴게요!"}
    ]

# 탭 구성
tab1, tab2, tab3, tab4 = st.tabs(["단어", "문법", "듣기", "원서 읽기"])

with tab1:
    st.markdown("<h3 style='font-family: NanumBarunpenB; color: black;'>단어 문제 생성</h3>", unsafe_allow_html=True)
    
    # 엑셀과 docx 업로드
    vocab_file = st.file_uploader("단어 엑셀 업로드 (xlsx)", type=["xlsx"], key="vocab_word_excel")
    primary_file = st.file_uploader("초등 문제지 업로드 (docx)", type=["docx"], key="primary_word")

    if vocab_file:
        vocab_file.seek(0)
        vocab_data = extract_units_from_excel(vocab_file)
        unit_list = sorted(
            vocab_data.keys(),
            key=lambda x: int(re.search(r'\d+', x).group())
        )

        for unit in unit_list:
            with st.expander(f"{unit} - 문제 생성"):
                if st.button(f"{unit} 문제 생성하기", key=unit):
                    if primary_file:
                        primary_file.seek(0)
                        doc = docx.Document(primary_file)
                        primary_example = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

                        context = f"""
                        [예시 형식]
                        {primary_example}

                        [단어 리스트 - {unit}]
                        {json.dumps(vocab_data[unit], ensure_ascii=False, indent=2)}
                        """

                        prompt = (
                            "너는 초등 영어 단어 문제를 만드는 선생님이야. "
                            "주어진 단어 리스트를 활용해, 아래 예시 형식처럼 단어 뜻 고르기, 문장 채우기, 철자 고르기 등의 문제를 만들어줘. "
                            "문제 형식은 반드시 예시를 따라야 하고, 출력은 100문제로 제한해줘."
                        )

                        with st.spinner(f"{unit} 문제 생성 중입니다..."):
                            try:
                                response = client.chat.completions.create(
                                    model="gpt-4o",
                                    messages=[
                                        {"role": "system", "content": prompt},
                                        {"role": "user", "content": context}
                                    ]
                                )
                                result = response.choices[0].message.content
                                st.success("변형 문제가 생성되었습니다!")
                                st.write(result)
                                st.download_button(f"{unit} 문제 다운로드", result, file_name=f"{unit}_문제.txt", key=f"{unit}_download")
                            except Exception as e:
                                st.error(f"오류 발생: {e}")
                    else:
                        st.warning("초등 문제지 파일을 업로드해주세요.")
    else:
        st.info("단어 엑셀 파일을 업로드해주세요.")

