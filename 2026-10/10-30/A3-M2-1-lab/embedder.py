import numpy as np
class Embedder:
    """문장 → 정규화된 float32 벡터. 기본은 e5 모델, 실패하면 글자 n-gram 해싱으로 대체."""
    def __init__(self, model_name="intfloat/multilingual-e5-small", fallback_dim=1024):
        self.model_name = model_name
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
            self.kind = model_name
            self.dim = self.model.get_sentence_embedding_dimension()
        except Exception as e:
            from sklearn.feature_extraction.text import HashingVectorizer
            self.model = HashingVectorizer(analyzer="char_wb", ngram_range=(2, 3),
                                           n_features=fallback_dim, alternate_sign=False, norm="l2")
            self.kind = f"fallback-char-ngram-{fallback_dim}"
            self.dim = fallback_dim
            print(f"(임베딩 모델을 불러오지 못해 대체 임베딩 사용: {type(e).__name__})")

    def encode(self, texts, kind="passage"):
        if self.kind.startswith("fallback"):
            v = self.model.transform(texts).toarray()
        else:
            prefix = "query: " if kind == "query" else "passage: "   # e5 규칙
            v = self.model.encode([prefix + t for t in texts], normalize_embeddings=True)
        return np.ascontiguousarray(v, dtype="float32")
