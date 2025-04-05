import openai
import os
from openai import OpenAI
import streamlit as st
from dotenv import load_dotenv
from style import set_background
from style import set_custom_fonts

set_background("anthony-delanoix-urUdKCxsTUI-unsplash.jpg")
set_custom_fonts("NanumBarunpenB.ttf", "NanumBarunpenB", "NanumBarunpenR.ttf", "NanumBarunpenR")

st.markdown(
    """
    <style>
    div.stButton > button {
        font-family: 'NanumBarunpenR', sans-serif;
        color: black !important;
        background-color: #85c1e9 !important;  /* 하늘색 배경 */
        border: none;
        padding: 0.5em 1em;
        border-radius: 8px;
        transition: 0.3s;
    }

    div.stButton > button:hover {
        background-color: #aed6f1 !important;  /* 더 연한 하늘색 */
        color: black !important;
    }

    div.stButton > button:active {
        background-color: #d6eaf8 !important;  /* 클릭 시 가장 연한 하늘색 */
        color: black !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)



openai.api_key = os.getenv("OPENAI_API_KEY")
st.markdown(
    f"""
    <h1 style='
        font-family: NanumBarunpenB;
        font-size: 48px;
        color: black;
        text-align: center;
        margin-bottom: 30px;
    '>영어 변형 문제</h1>
    """,
    unsafe_allow_html=True
)

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": "너는 영어 문제를 변형해서 출제하는 도우미야."},
        {"role": "assistant", "content": "기출문제를 입력해주시면 변형 문제를 만들어드릴게요!"}
    ]

# 세션 상태에 누적된 기출문제 저장용 리스트 초기화
if "past_questions" not in st.session_state:
    st.session_state["past_questions"] = []

# 업로드 및 개수 입력
# 스타일 먼저 적용
st.markdown(
    """
    <style>
    .custom-title {
        font-family: 'NanumBarunpenB', sans-serif;
        font-size: 28px;
        margin-top: 30px;
        margin-bottom: 10px;
        color: black;
    }
    .upload-box {
        background-color: rgba(255, 255, 255, 0.6);
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 25px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 업로드 3개 항목
st.markdown('<div class="custom-title">📘 교과서 업로드</div>', unsafe_allow_html=True)
with st.container():
    textbook_file = st.file_uploader("", type=["txt"], key="textbook", label_visibility="collapsed")

st.markdown('<div class="custom-title">📗 모의고사 업로드</div>', unsafe_allow_html=True)
with st.container():
    mock_file = st.file_uploader("", type=["txt"], key="mock", label_visibility="collapsed")

st.markdown('<div class="custom-title">📙 기출문제 업로드</div>', unsafe_allow_html=True)
with st.container():
    past_file = st.file_uploader("", type=["txt"], key="past", label_visibility="collapsed")

num_questions = st.number_input("몇 개의 변형 문제를 만들까요?", min_value=1, max_value=100, value=10)

num_questions = st.number_input("몇 개의 변형 문제를 만들까요?", min_value=1, max_value=100, value=10)

st.markdown("""
    <style>
    div.stButton > button {
        background-color: white;
        color: black;
        border: 2px solid black;
        border-radius: 8px;
        padding: 10px 24px;
        font-family: 'NanumBarunpenR';
        font-size: 18px;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #add8e6;
        color: black;
    }
    </style>
""", unsafe_allow_html=True)

# 변형문제 생성 버튼
if st.button("변형 문제 생성하기"):
    if not (textbook_file and mock_file and past_file):
        st.warning("모든 파일을 업로드해주세요.")
    else:
        textbook_text = textbook_file.read().decode("utf-8")
        mock_text = mock_file.read().decode("utf-8")
        past_text = past_file.read().decode("utf-8")

        context = f"""
        교과서 내용:
{textbook_text}

        모의고사 내용:
{mock_text}

        기출문제:
{past_text}
        """

        with st.spinner("GPT가 변형 문제를 생성 중입니다..."):
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "너는 영어 기출문제를 바탕으로 변형 문제를 만들어주는 전문가야. 기출문제가 교과서와 모의고사를 바탕으로 만들어졌음을 고려해 변형 문제를 출제해줘."},
                    {"role": "user", "content": f"아래의 자료들을 참고해서 {num_questions}개의 변형 문제를 만들어줘:\n\n{context}"}
                ]
            )

            result = response.choices[0].message.content
            st.success("변형 문제가 생성되었습니다!")
            st.write(result)

            st.download_button("변형 문제 다운로드", result, file_name="변형문제.txt")

