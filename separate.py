import fitz  # PyMuPDF
import re

def extract_units_individually_from_pdf(file):
    """
    Streamlit에서 업로드된 단어 PDF 파일에서 Unit별로 단어와 정의를 추출합니다.
    각 Unit은 'Unit 1', 'Unit 2', ... 식으로 나눠서 반환됩니다.
    """
    doc = fitz.open(stream=file.read(), filetype="pdf")
    full_text = ""
    for page in doc:
        full_text += page.get_text() + "\n"

    units = {}
    current_unit = None
    current_words = []

    lines = full_text.split("\n")
    unit_pattern = re.compile(r"^Unit\s+(\d+)\b")  # Unit 1, Unit 2 등과 매칭
    word_pattern = re.compile(r"^([a-zA-Z\\-']+)\s+\\[.*?\\]\\s*(.*)")  # 단어 [품사] 정의

    for line in lines:
        line = line.strip()

        # 유닛 시작 라인 확인
        unit_match = unit_pattern.match(line)
        if unit_match:
            if current_unit and current_words:
                units[f"Unit {current_unit}"] = current_words
            current_unit = unit_match.group(1)
            current_words = []
            continue

        # 단어 라인 처리
        word_match = word_pattern.match(line)
        if word_match:
            word = word_match.group(1)
            meaning = word_match.group(2)
            current_words.append({"word": word, "definition": meaning})

    # 마지막 유닛 저장
    if current_unit and current_words:
        units[f"Unit {current_unit}"] = current_words

    return units


def separate_problems(text: str):
    problem_pattern = re.compile(r"(?P<number>\[\d+\s*~\s*\d+\]|\d{1,2})\.\s*(?P<question>.+?)(?=\n|$)")
    choice_pattern = re.compile(r"(①|②|③|④|⑤)")

    lines = text.strip().split("\n")
    problems = []
    current_problem = {}
    buffer = []

    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

        problem_match = problem_pattern.match(line)
        if problem_match:
            if current_problem:
                # 지문과 선지 나누기
                combined = "\n".join(buffer).strip()
                split_match = choice_pattern.search(combined)
                if split_match:
                    split_idx = split_match.start()
                    current_problem["passage"] = combined[:split_idx].strip()
                    current_problem["choices"] = combined[split_idx:].strip()
                else:
                    current_problem["passage"] = combined
                    current_problem["choices"] = ""
                problems.append(current_problem)
                buffer = []

            number = problem_match.group("number")
            question = problem_match.group("question")
            current_problem = {
                "number": number,
                "question": question,
                "passage": "",
                "choices": ""
            }
        else:
            buffer.append(line)

    # 마지막 문제 처리
    if current_problem:
        combined = "\n".join(buffer).strip()
        split_match = choice_pattern.search(combined)
        if split_match:
            split_idx = split_match.start()
            current_problem["passage"] = combined[:split_idx].strip()
            current_problem["choices"] = combined[split_idx:].strip()
        else:
            current_problem["passage"] = combined
            current_problem["choices"] = ""
        problems.append(current_problem)

    return problems

def parse_primary_level_questions(text: str):
    # 간단한 정규표현식으로 번호/선지 구분
    pattern = re.compile(r"(?P<number>\d+)\.\s*(?:\n)?(?P<choices>(?:[a-d]\).+?\n?)+)", re.MULTILINE)
    choice_pattern = re.compile(r"(a|b|c|d)\)\s*(.+)")
    problems = []

    for match in pattern.finditer(text):
        number = match.group("number")
        raw_choices = match.group("choices").strip().split("\n")
        parsed_choices = []
        for c in raw_choices:
            choice_match = choice_pattern.match(c.strip())
            if choice_match:
                parsed_choices.append(choice_match.group(2))
        problems.append({
            "number": number,
            "question": "보기 중 알맞은 단어를 고르세요.",
            "choices": parsed_choices
        })
    return problems

def extract_text_from_pptx(file):
    prs = Presentation(file)
    text = ""
    for slide in prs.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                text += shape.text + "\n"
    return text
