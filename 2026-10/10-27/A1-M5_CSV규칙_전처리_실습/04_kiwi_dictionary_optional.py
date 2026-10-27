"""04. 선택형 사용자 사전: 원문을 바꾸지 않고 분석 후보만 추가한다."""
try:
    from kiwipiepy import Kiwi
except ImportError as exc:
    raise SystemExit("선택형 실습입니다. python -m pip install kiwipiepy") from exc

kiwi = Kiwi()
text = "메타정합검증 결과를 확인합니다"

def show() -> list[tuple[str,str]]:
    return [(t.form,t.tag) for t in kiwi.tokenize(text)]

print("원문:", text)
print("등록 전:", show())
print("등록 결과:", kiwi.add_user_word("메타정합검증", "NNP", score=5.0))
print("등록 후:", show())
print("주의: 반드시 개선된다는 보장은 없으며 분석기·사전 버전을 기록해야 합니다.")
