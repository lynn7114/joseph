import fitz
import re
from pptx import Presentation

def extract_units_individually_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    full_text = ""
    for page in doc:
        full_text += page.get_text() + "\n"

    units = {}
    current_unit = None
    current_words = []

    lines = full_text.split("\n")
    unit_pattern = re.compile(r"^Unit\s+(\d+)\b")
    word_pattern = re.compile(r"^([a-zA-Z\-']+)\s+\[.*?\]\s*(.*)")

    for line in lines:
        line = line.strip()

        # ✅ 'Review'와 'Practice'로 시작하는 페이지 무시
        if line.startswith("Review") or line.startswith("Practice"):
            continue

        # ✅ Unit 시작
        unit_match = unit_pattern.match(line)
        if unit_match:
            if current_unit and current_words:
                units[f"Unit {current_unit}"] = current_words
            current_unit = unit_match.group(1)
            current_words = []
            continue

        # ✅ 단어 + 뜻 추출
        word_match = word_pattern.match(line)
        if word_match:
            word = word_match.group(1)
            definition = word_match.group(2)
            current_words.append({"word": word, "definition": definition})

    # ✅ 마지막 유닛 저장
    if current_unit and current_words:
        units[f"Unit {current_unit}"] = current_words

    # 유닛별 단어와 뜻을 깔끔하게 출력
    for unit, words in units.items():
        print(f"{unit}:\n{'-' * len(unit)}")
        for idx, entry in enumerate(words, 1):
            word = entry['word']
            definition = entry['definition']
        print("\n")

    return units


def separate_problems(text: str):
    problem_pattern = re.compile(r"(?P<number>\[\d+\s*~\s*\d+\]|\d{1,2})\.\s*(?P<question>.+?)(?=\n|$)")
    choice_pattern = re.compile(r"(①|②|③|④|⑤)")

    lines = text.strip().split("\n")
    problems = []
    current_problem = {}
    buffer = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        problem_match = problem_pattern.match(line)
        if problem_match:
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
