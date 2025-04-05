import re

def separate_passages_and_choices(text):
    # 문제를 구분하는 기준: 숫자 + 점 또는 괄호 (예: 1., 2), 3) 등)
    questions = re.split(r'\n\s*\d+[\.\)]\s*', text)
    questions = [q.strip() for q in questions if q.strip()]  # 빈 문자열 제거

    separated = []
    for q in questions:
        # 선지 분리용 패턴: (a), ①, 1. 등 다양한 경우 대응
        choice_pattern = r'(\([a-dA-D]\)|[①②③④⑤⑥⑦⑧⑨]|^\d+\.)'
        parts = re.split(choice_pattern, q)
        
        # parts[0]은 지문, 나머지는 선지 구성
        passage = parts[0].strip()
        choices = []

        i = 1
        while i < len(parts) - 1:
            label = parts[i].strip()
            option = parts[i + 1].strip()
            choices.append(f"{label} {option}")
            i += 2

        separated.append({
            "passage": passage,
            "choices": choices
        })
    return separated
