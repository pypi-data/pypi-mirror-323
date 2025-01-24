import typer

types = {
    "ISTP": "백과사전형",
    "ISFP": "성인군자형",
    "ISTJ": "소금형",
    "ISFJ": "권력형",
    "INFJ": "예언자형",
    "INTJ": "과학자형",
    "INFP": "잔다르크형",
    "INTP": "아이디어형",
    "ESTP": "활동가형",
    "ESFP": "사교형",
    "ENFP": "스파크형",
    "ENTP": "발명가형",
    "ESTJ": "사업가형",
    "ESFJ": "친선도모형",
    "ENFJ": "언변능숙형",
    "ENTJ": "지도자형"
}

def check_type(mbti: str):
    return types[mbti]

def print_check_type(mbti: str):
    checked_type = check_type(mbti)
    print(checked_type)

def entry_point():
    typer.run(print_check_type)
