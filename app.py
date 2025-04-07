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
from separate import extract_vocab_from_pdf
from pptx import Presentation
from separate import extract_text_from_pptx

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

# 탭 구분
tab1, tab2, tab3, tab4 = st.tabs(["\ud83d\udcd8 \ub2e8\uc5b4", "\ud83d\udcd7 \ubb38\ub960", "\ud83d\udcd9 \ub4e4\uae30", "\ud83d\udcd5 \uc6d0\uc11c \uc77d\uae30"])

with tab1:
    st.markdown("### \ud83d\udcd8 \ub2e8\uc5b4 \ubb38\uc81c \uc0dd\uc131")

    vocab_file = st.file_uploader("\ub2e8\uc5b4 PDF \uc5c5\ub85c\ub4dc", type=["pdf"], key="vocab_word")
    primary_file = st.file_uploader("\ucd08\ub4f1 \ubb38\uc81c\uc9c0 \uc5c5\ub85c\ub4dc", type=["docx"], key="primary_word")

    if vocab_file:
        vocab_data = extract_vocab_from_pdf(vocab_file)
        unit_list = list(vocab_data.keys())
        selected_unit = st.selectbox("\ud83d\udcc2 Unit\uc744 \uc120\ud0dd\ud558\uc138\uc694", unit_list)

    if st.button("\ud83d\udcd7 \ub2e8\uc5b4 \ubb38\uc81c \uc0dd\uc131\ud558\uae30"):
        if not (vocab_file and primary_file):
            st.warning("\ub2e8\uc5b4 PDF\uc640 \ucd08\ub4f1 \ubb38\uc81c\uc9c0\ub97c \ubaa8\ub450 \uc5c5\ub85c\ub4dc\ud574\uc8fc\uc138\uc694.")
        else:
            from docx import Document
            doc = Document(primary_file)
            primary_example = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

            context = f"""
            [\uc608\uc2dc \ud615\uc2dd]
            {primary_example}

            [\ub2e8\uc5b4 \ub9ac\uc2a4\ud2b8 - {selected_unit}]
            {json.dumps(vocab_data[selected_unit], ensure_ascii=False, indent=2)}
            """

            prompt = (
                "\ub108\ub294 \ucd08\ub4f1 \uc601\uc5b4 \ub2e8\uc5b4 \ubb38\uc81c\ub97c \ub9cc\ub4e4\uc5b4\uc8fc\ub294 \uc120\uc0dd\ub2d8\uc774\uc57c. "
                "\uc8fc\uc5b4\uc9c4 \ub2e8\uc5b4 \ub9ac\uc2a4\ud2b8\ub97c \ud65c\uc6a9\ud574, \uc544\ub798 \uc608\uc2dc \ud615\uc2dd\ucc98\ub7fc \ub2e8\uc5b4 \ubaa8\uc74c \uace0\ub974\uae30, \ubb38\uc7a5 \ucc44\uc6cc\ub123\uae30, \uccb4\uc790 \uace0\ub974\uae30 \ub4f1\uc758 \ubb38\uc81c\ub97c \ub9cc\ub4e4\uc5b4\uc918. "
                "\ubb38\uc81c \ud615\uc2dd\uc740 \xeb°%bd\uc2dc\ub97c \ub530\ub77c\uc57c \ud558\uace0, \ucc38\uace0\ub294 10\ubb38\uc81c\ub85c \ud574\uc918."
            )

            with st.spinner("GPT\uac00 \ub2e8\uc5b4 \ubb38\uc81c\ub97c \uc0dd\uc131 \uc911\uc785\ub2c8\ub2e4..."):
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": context}
                    ]
                )

                result = response.choices[0].message.content
                st.success("\u2705 \ub2e8\uc5b4 \ubb38\uc81c\uac00 \uc0dd\uc131\ub418\uc5c8\uc2b5\ub2c8\ub2e4!")
                st.write(result)
                st.download_button("\ud83d\udcc5 \ub2e8\uc5b4 \ubb38\uc81c \ub2e4\uc6b4\ub85c\ub4dc", result, file_name=f"{selected_unit}_\ubb38\uc81c_\uc0dd\uc131\uacb0\uacfc.txt")

# ''' 이하 기존 코드 유지 (주석 처리된 영역은 수정하지 않음)
'''


# 업로드 박스 3개
st.markdown('<div class="custom-title">📘 교과서 업로드</div>', unsafe_allow_html=True)
with st.container():
    textbook_file = st.file_uploader("", type=["pptx"], key="textbook", label_visibility="collapsed")

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
    if not (textbook_file and primary_file):
        st.warning("교과서와 초등 문제지를 모두 업로드해주세요.")
    else:
        # 📖 교과서 읽기
        # 🧾 교과서 내용 추출
        textbook_text = extract_text_from_pptx(textbook_file)


        # 📕 초등 문제지 읽기 (.docx)
        from docx import Document
        doc = Document(primary_file)
        primary_example = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

        # 프롬프트 구성
        system_prompt = (
            "너는 초등학생을 위한 영어 문제를 만드는 전문가야. "
            "사용자가 제공한 교과서 내용을 바탕으로 아래 예시 형식을 따라서 문제를 만들어줘. "
            "형식은 반드시 그대로 따라야 하며, 문제 유형, 개수, 구조, 표현 등을 참고해서 유사하게 구성해줘. "
            "단, 새 문제의 내용은 교과서를 기반으로 해야 해."
        )

        user_prompt = f"""
        [예시 형식: 실제 문제지 문서에서 추출된 내용]
        {primary_example}

        [교과서 내용]
        {textbook_text}
        """

        with st.spinner("GPT가 초등 문제를 생성 중입니다..."):
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )

            result = response.choices[0].message.content
            st.success("초등 문제 생성이 완료되었습니다!")
            st.write(result)

            st.download_button("초등 문제 다운로드", result, file_name="초등문제_생성결과.txt")



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
'''
