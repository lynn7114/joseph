import openai
import os
import json
from openai import OpenAI
import streamlit as st
from dotenv import load_dotenv
from style import set_background
from style import set_custom_fonts
from separate import separate_problems
from separate import parse_primary_level_questions

set_background("anthony-delanoix-urUdKCxsTUI-unsplash.jpg")
set_custom_fonts("NanumBarunpenB.ttf", "NanumBarunpenB", "NanumBarunpenR.ttf", "NanumBarunpenR")

st.markdown(
    """
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

# 업로드 3개 항목 스타일 설정
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

# 업로드 박스 3개
st.markdown('<div class="custom-title">📘 교과서 업로드</div>', unsafe_allow_html=True)
with st.container():
    textbook_file = st.file_uploader("", type=["txt"], key="textbook", label_visibility="collapsed")

st.markdown('<div class="custom-title">📗 모의고사 업로드</div>', unsafe_allow_html=True)
with st.container():
    mock_file = st.file_uploader("", type=["txt"], key="mock", label_visibility="collapsed")


st.markdown('<div class="custom-title">📙 기출문제 업로드</div>', unsafe_allow_html=True)
with st.container():
    past_file = st.file_uploader("", type=["txt"], key="past", label_visibility="collapsed")

st.markdown('<div class="custom-title">📕 초등 문제지 업로드</div>', unsafe_allow_html=True)
with st.container():
    primary_file = st.file_uploader("", type=["docx", "txt"], key="primary", label_visibility="collapsed")

if st.button("초등 문제 생성하기"):
    if not primary_file:
        st.warning("초등 문제지를 업로드해주세요.")
    else:
        from docx import Document  # python-docx 필요
        doc = Document(primary_file)
        full_text = "\n".join([p.text for p in doc.paragraphs])
        
        parsed = parse_primary_level_questions(full_text)
        
        result = json.dumps(parsed, ensure_ascii=False, indent=2)
        st.success("초등 문제 파싱 결과입니다!")
        st.code(result, language="json")

        st.download_button("문제 다운로드", result, file_name="초등문제_파싱결과.json")


st.markdown(
    """
    <style>
    .custom-input-title {
        font-family: 'NanumBarunpenB', sans-serif;
        font-size: 28px;
        margin-top: 30px;
        margin-bottom: 10px;
        color: black;
    }
    .custom-input-box {
        background-color: rgba(255, 255, 255, 0.6);
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 25px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="custom-input-title">📝 몇 개의 변형 문제를 만들까요?</div>', unsafe_allow_html=True)
with st.container():
    num_questions = st.number_input("", min_value=1, max_value=100, value=10, key="num_questions", label_visibility="collapsed")


# 변형문제 생성 버튼
if st.button("변형 문제 생성하기"):
    if not (textbook_file and mock_file and past_file):
        st.warning("모든 파일을 업로드해주세요.")
    else:
        # 한 번만 읽어 변수에 저장
        textbook_text = textbook_file.read().decode("utf-8")
        mock_text = mock_file.read().decode("utf-8")
        past_text = past_file.read().decode("utf-8")
        
        # separate_problems로 파싱
        mock_file_parse = separate_problems(mock_text)
        past_file_parse = separate_problems(past_text)

        context = f"""
        교과서 내용:
{textbook_text}

        모의고사 내용 (형식: from separate.py 반환 형식):
{json.dumps(mock_file_parse, ensure_ascii=False, indent=2)}

        기출문제 내용 (형식 동일):
{json.dumps(past_file_parse, ensure_ascii=False, indent=2)}
        """

        system_prompt = (
            "너는 영어 기출문제를 바탕으로 변형 문제를 만들어주는 전문가야. "
            "아래 'separate.py'에서 반환한 문제 형식을 그대로 따라야 해. 즉, 각 문제는\n"
            "\"number\", \"question\", \"passage\", \"choices\" 키를 가진 딕셔너리 형식으로 생성되어야 해.\n"
            "형식 예시:\n"
            "[\n"
            "  {\n"
            "    \"number\": \"20\",\n"
            "    \"question\": \"다음 글에서 주장하는 바로 가장 적절한 것은?\",\n"
            "    \"passage\": \"Improving your gestural communication ...\",\n"
            "    \"choices\": [\n"
            "      \"① 메시지를 잘 전달하기 위해서 열린 마음을 지녀야 한다.\",\n"
            "      \"② 효과적인 의사소통을 위해 몸짓을 적절히 사용해야 한다.\",\n"
            "      \"③ 청중의 반응을 파악하기 위해 그들의 몸짓에 주목해야 한다.\",\n"
            "      \"④ 전달하고자 하는 것을 감추기보다 직접적으로 표현해야 한다.\",\n"
            "      \"⑤ 상대방을 설득하기 위해서는 메시지를 반복적으로 강조해야 한다.\"\n"
            "    ]\n"
            "  },\n"
            "  ...\n"
            "]\n"
            "반드시 이 형식을 지켜서 문제를 생성해."
        )

        user_prompt = f"아래 자료들을 참고해서 {num_questions}개의 변형 문제를 만들어줘:\n\n{context}"

        with st.spinner("GPT가 변형 문제를 생성 중입니다..."):
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )

            result = response.choices[0].message.content
            st.success("변형 문제가 생성되었습니다!")
            st.write(result)

            st.download_button("변형 문제 다운로드", result, file_name="변형문제.txt")
