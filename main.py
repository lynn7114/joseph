from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import json
import docx
import re
import os
from openai import OpenAI
from dotenv import load_dotenv
from io import BytesIO
from utils import extract_units_from_excel, extract_units_from_docx, create_problem_and_answer_docs  # 기존 함수 모듈화 필요

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

class ProblemRequest(BaseModel):
    unit_title: str
    vocab_data: dict
    example_format: str


@app.post("/generate/vocab")
async def generate_vocab_problem(data: ProblemRequest):
    prompt = (
        "너는 초등 영어 단어 문제를 만드는 선생님이야. "
        "주어진 단어 리스트를 활용해, 아래 예시 형식처럼 단어 뜻 고르기, 문장 채우기, 철자 고르기 등의 문제를 만들어줘. "
        "문제 형식은 반드시 예시를 따라야 하고, 출력은 100문제로 제한해줘. "
        "**각 문제 뒤에 반드시 '정답:'이라는 텍스트로 정답을 따로 정리해서 제공해줘.** 예: 정답: 1. A 2. B"
    )

    context = f"""
    [예시 형식]
    {data.example_format}

    [단어 리스트 - {data.unit_title}]
    {json.dumps(data.vocab_data, ensure_ascii=False, indent=2)}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": context}
            ]
        )
        result = response.choices[0].message.content
        problem_file, answer_file = create_problem_and_answer_docs(result)

        return JSONResponse({
            "message": "문제가 생성되었습니다",
            "problem_file": problem_file.getvalue().decode('latin1'),  # Base64 인코딩 권장
            "answer_file": answer_file.getvalue().decode('latin1')
        })

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
