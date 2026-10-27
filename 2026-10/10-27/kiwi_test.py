# 설치: python -m pip install kiwipiepy
from kiwipiepy import Kiwi

kiwi = Kiwi()
text = "배송이 빠르지 않습니다."

for token in kiwi.tokenize(text):
    print(token.form, token.tag, token.start, token.len)

nouns = [t.form for t in kiwi.tokenize(text) if t.tag in {"NNG", "NNP"}]
print("명사만:", nouns)
print("원본:", text)