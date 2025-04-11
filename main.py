from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import os
import uuid

app = FastAPI()

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    # 고유한 이름으로 파일 저장
    filename = f"{uuid.uuid4().hex}_{file.filename}"
    input_path = os.path.join("input", filename)
    output_path = os.path.join("output", f"result_{filename}")

    # 업로드된 파일 저장
    with open(input_path, "wb") as f:
        f.write(await file.read())

    # 여기서 파일 처리 로직 삽입 (예시로 파일 복사만)
    with open(input_path, "rb") as src, open(output_path, "wb") as dst:
        dst.write(src.read())

    # 결과 파일 반환
    return FileResponse(output_path, filename=os.path.basename(output_path))
