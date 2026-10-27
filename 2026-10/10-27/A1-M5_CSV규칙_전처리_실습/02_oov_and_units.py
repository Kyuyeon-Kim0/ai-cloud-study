"""02. OOV는 '어떤 사전 기준인가'에 의존한다. [UNK]를 강제로 만들지 않는다."""
from cleaner import whitespace_tokens, char_ngrams

sentence = "메타정합검증 규칙이 적용되지 않습니다"
known_words = {"규칙이", "적용되지", "않습니다"}  # 학습용 매우 작은 어휘 목록
words = whitespace_tokens(sentence)
print("공백 분할:", words)
print("이 예시 어휘 목록 기준 OOV:", [word for word in words if word not in known_words])
print("문자 2-gram(앞 12개):", char_ngrams(sentence)[:12])
print("기술 식별자:", whitespace_tokens("WCAG 2.4.4 aria-label COMP-LINK-001"))
print("주의: OOV는 단어가 없는 사전의 문제이며, 반드시 [UNK]로 매핑되지는 않습니다.")
