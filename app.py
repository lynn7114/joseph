import openai
import os
import json
import re
import docx
import fitz
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from style import set_background, set_custom_fonts
from separate import separate_problems, parse_primary_level_questions, extract_units_individually_from_pdf, extract_units_from_excel, extract_units_from_docx
from pptx import Presentation

# 기본 설정
st.set_page_config(page_title="영어 변형 문제", layout="wide")

# API 키 로드
load_dotenv()
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# UI 세팅
set_background("anthony-delanoix-urUdKCxsTUI-unsplash.jpg")
set_custom_fonts("NanumBarunpenB.ttf", "NanumBarunpenB", "NanumBarunpenR.ttf", "NanumBarunpenR")

# 스타일 커스텀
st.markdown("""
    <style>
    .sidebar-title {
        font-size: 24px;
        font-family: 'NanumBarunpenB', sans-serif;
        font-weight: bold;
        color: #1f4e79;
        margin-bottom: 20px;
    }

    div.stButton > button {
        width: 100%;
        background-color: #ffffff;
        color: #1f4e79;
        border: 1px solid #85c1e9;
        border-radius: 8px;
        padding: 0.6em;
        margin-bottom: 10px;
        font-size: 16px;
        font-family: 'NanumBarunpenR', sans-serif;
        transition: 0.3s;
    }

    div.stButton > button:hover {
        background-color: #d6eaf8;
        color: black;
        border-color: #aed6f1;
    }
    </style>
""", unsafe_allow_html=True)

# 상태 저장
if "selected_menu" not in st.session_state:
    st.session_state["selected_menu"] = "단어"

# 선택 함수 정의
def select_menu(menu_name):
    st.session_state["selected_menu"] = menu_name

# HTML 버튼 스타일
st.sidebar.markdown("""
    <style>
    .menu-button {
        display: block;
        width: 100%;
        padding: 10px 20px;
        margin-bottom: 10px;
        background-color: #ffffff;
        color: #1f4e79;
        text-align: left;
        border: 2px solid #85c1e9;
        border-radius: 10px;
        font-size: 18px;
        font-family: 'NanumBarunpenB', sans-serif;
        cursor: pointer;
        transition: 0.3s;
    }

    .menu-button:hover {
        background-color: #d6eaf8;
    }
    </style>
""", unsafe_allow_html=True)

# 메뉴 버튼들
with st.sidebar:
    st.markdown('<div class="sidebar-title">메뉴 선택</div>', unsafe_allow_html=True)
    if st.button("단어", on_click=select_menu, args=("단어",)):
        pass
    if st.button("문법", on_click=select_menu, args=("문법",)):
        pass
    if st.button("듣기", on_click=select_menu, args=("듣기",)):
        pass
    if st.button("원서 읽기", on_click=select_menu, args=("원서 읽기",)):
        pass

# -------------------------------
# 메인 영역 컨텐츠 조건 분기
# -------------------------------
selected_tab = st.session_state["selected_menu"]

if selected_tab == "단어":
    # 단어 관련 코드 넣기
    st.markdown("""
        <h1 style='font-family: NanumBarunpenB; font-size: 48px; color: black; text-align: center; margin-bottom: 30px;'>
            영어 변형 문제
        </h1>
    """, unsafe_allow_html=True)
    
    # 세션 초기화
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "system", "content": "너는 영어 문제를 변형해서 출제하는 도우미야."},
            {"role": "assistant", "content": "기출문제를 입력해주시면 변형 문제를 만들어드릴게요!"}
        ]

    
    # 단어 업로드 타이틀
    st.markdown("""
        <h4 style='font-family: NanumBarunpenB; color: #1f4e79; text-align: center;'>
            단어 업로드
        </h4>
    """, unsafe_allow_html=True)
    vocab_file = st.file_uploader("", type=["xlsx"], key="vocab_word_excel")
    
    # 변형 문제 업로드 타이틀
    st.markdown("""
        <h4 style='font-family: NanumBarunpenB; color: #1f4e79; text-align: center;'>
            변형 문제 업로드
        </h4>
    """, unsafe_allow_html=True)
    primary_file = st.file_uploader("", type=["docx"], key="primary_word")


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

elif selected_tab == "문법":
    st.markdown("<h3 style='font-family: NanumBarunpenB; color: black;'>문법 문제 생성 (업데이트 예정)</h3>", unsafe_allow_html=True)
    st.info("문법 문제 기능은 준비 중이에요. 필요한 문법 유형이나 문제 스타일이 있다면 알려주세요!")

elif selected_tab == "듣기":
    st.markdown("""
        <h1 style='font-family: NanumBarunpenB; font-size: 40px; color: black; text-align: center; margin-bottom: 30px;'>
            듣기 변형 문제 생성
        </h1>
    """, unsafe_allow_html=True)

    st.markdown("""
        <h4 style='font-family: NanumBarunpenB; color: #1f4e79; text-align: center;'>
            듣기 교재 업로드
        </h4>
    """, unsafe_allow_html=True)
    listening_file = st.file_uploader("", type=["docx"], key="listening_docx")

    st.markdown("""
        <h4 style='font-family: NanumBarunpenB; color: #1f4e79; text-align: center;'>
            예시 문제 업로드
        </h4>
    """, unsafe_allow_html=True)
    example_file = st.file_uploader("", type=["docx"], key="listening_example")


    if listening_file:
        units = extract_units_from_docx(listening_file)
        unit_titles = sorted(units.keys(), key=lambda x: int(re.search(r'\d+', x).group()))

        for unit_title in unit_titles:
            with st.expander(f"{unit_title} - 문제 생성"):
                if st.button(f"{unit_title} 문제 생성하기", key=unit_title):
                    if example_file:
                        example_doc = docx.Document(example_file)
                        example_text = "\n".join([p.text for p in example_doc.paragraphs if p.text.strip()])

                        prompt = (
                            "너는 초등학생 영어 듣기 문제를 만드는 선생님이야. "
                            "예시 문제 형식을 참고해서, 주어진 지문으로 문제를 만들어줘. "
                            "문제 형식은 반드시 예시를 따라야 하고, 5~10문제 정도 만들어줘."
                        )

                        context = f"""
                        [예시 문제]
                        {example_text}

                        [지문 - {unit_title}]
                        {units[unit_title]}
                        """

                        with st.spinner(f"{unit_title} 문제 생성 중입니다..."):
                            try:
                                response = client.chat.completions.create(
                                    model="gpt-4o",
                                    messages=[
                                        {"role": "system", "content": prompt},
                                        {"role": "user", "content": context}
                                    ]
                                )
                                result = response.choices[0].message.content
                                st.success("변형 문제가 생성되었습니다.")
                                st.write(result)
                                st.download_button(f"{unit_title} 문제 다운로드", result, file_name=f"{unit_title}_듣기문제.txt", key=f"{unit_title}_download")
                            except Exception as e:
                                st.error(f"오류 발생: {e}")
                    else:
                        st.warning("예시 문제 파일을 업로드해주세요.")
    else:
        st.info("듣기 교재 docx 파일을 업로드해주세요.")



elif selected_tab == "원서 읽기":
    st.markdown("<h3 style='font-family: NanumBarunpenB; color: black;'>원서 독해 문제 생성 (업데이트 예정)</h3>", unsafe_allow_html=True)
    st.info("원서 기반 독해 문제 기능은 준비 중이에요. 읽고 싶은 원서 파일이 있다면 지금 올려주세요!")

