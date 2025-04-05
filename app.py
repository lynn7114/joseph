import openai
import os
from openai import OpenAI
import streamlit as st
from dotenv import load_dotenv
from style import set_background

set_background()

openai.api_key = os.getenv("OPENAI_API_KEY")
st.title("영어 변형 문제")

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
uploaded_file = st.file_uploader("기출문제 파일을 업로드하세요 (.txt)", type=["txt"])
num_questions = st.number_input("몇 개의 변형 문제를 만들까요?", min_value=1, max_value=100, value=10)

# 버튼 눌렀을 때 처리
if st.button("기출문제 추가하기") and uploaded_file:
    input_text = uploaded_file.read().decode("utf-8")
    st.session_state["past_questions"].append(input_text)
    st.success("기출문제가 저장되었습니다!")

# 현재까지 저장된 기출문제 보기
if st.session_state["past_questions"]:
    st.markdown("### 🧾 누적된 기출문제")
    for i, qset in enumerate(st.session_state["past_questions"], 1):
        st.markdown(f"**{i}.**\n```\n{qset.strip()}\n```")

# 변형문제 생성
if st.button("변형 문제 생성하기"):
    if not st.session_state["past_questions"]:
        st.warning("먼저 기출문제를 업로드해 주세요.")
    else:
        # 모든 기출문제 합치기
        full_context = "\n".join(st.session_state["past_questions"])
        with st.spinner("GPT가 문제를 만들고 있어요..."):
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "너는 영어 기출문제를 바탕으로 변형 문제를 만들어주는 전문가야."},
                    {"role": "user", "content": f"이전까지 업로드된 기출문제를 바탕으로 {num_questions}개의 변형 문제를 만들어줘:\n\n{full_context}"}
                ]
            )
            result = response.choices[0].message.content
            st.success("변형 문제가 생성되었습니다!")
            st.write(result)

            st.download_button("변형 문제 다운로드", result, file_name="변형문제.txt")

