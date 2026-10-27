"""01. 작은 문장부터 정제·정규화의 효과와 위험을 확인."""
import unicodedata
from cleaner import clean_text

raw = "  [공지]  WCAG 2.4.4\n  aria-label 을   확인하세요.  "
clean = clean_text(raw)
print("원본:", repr(raw))
print("정제:", repr(clean))
print("식별자 보존:", "WCAG 2.4.4" in clean, "aria-label" in clean)
print("NFC / NFKC:", unicodedata.normalize("NFC", "①"), unicodedata.normalize("NFKC", "①"))
print("의미 보존 확인:", clean_text("접근할 수 없다"))
