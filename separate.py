import fitz  # PyMuPDF
import re

def extract_vocab_from_pdf(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()

    units = {}
    current_unit = None
    current_words = []

    lines = text.split("\n")
    for line in lines:
        line = line.strip()

        # ✅ 정규표현식으로 'Unit 1', 'Unit 2' 등만 인식 (묶음 제외)
        unit_match = re.match(r"^Unit\s+(\d+)$", line)
        if unit_match:
            if current_unit and current_words:
                units[current_unit] = current_words
            current_unit = f"Unit {unit_match.group(1)}"
            current_words = []
        elif line and "[" in line and "]" in line:
            parts = line.split("]")
            if len(parts) >= 2:
                word = parts[0].split("[")[0].strip()
                definition = parts[1].strip()
                current_words.append({"word": word, "definition": definition})

    if current_unit and current_words:
        units[current_unit] = current_words

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
