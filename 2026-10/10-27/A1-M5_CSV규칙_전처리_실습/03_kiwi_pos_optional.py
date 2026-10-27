"""03. 선택형 Kiwi 실습. 설치: python -m pip install kiwipiepy"""
try:
    from kiwipiepy import Kiwi
except ImportError as exc:
    raise SystemExit("선택형 실습입니다. python -m pip install kiwipiepy") from exc

kiwi = Kiwi()
for sentence in ["배송이 빠르지 않습니다", "접근성이 좋지 않습니다", "메타정합검증 규칙을 검토합니다"]:
    print("\n원문:", sentence)
    print("형태소 (형태, 품사, 위치):")
    for token in kiwi.tokenize(sentence):
        print("  ", token.form, token.tag, token.start)
    print("명사만:", [t.form for t in kiwi.tokenize(sentence) if t.tag in {"NNG", "NNP"}])
    print("→ 부정·서술 표현이 손실됐는지 원문과 비교해 보세요.")
