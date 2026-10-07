import hashlib
import math
import re
from functools import lru_cache

from app.config import EMBEDDING_MODEL_NAME, FALLBACK_EMBEDDING_DIM


TOKEN_RE = re.compile(r"[a-zA-Z0-9_.$:-]+")


class EmbeddingService:
    def __init__(self, model_name: str = EMBEDDING_MODEL_NAME):
        self.model_name = model_name
        self._model = None
        self._model_loaded = False

    def _load_model(self):
        if self._model_loaded:
            return

        self._model_loaded = True

        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(
                self.model_name,
                device="cpu"
            )
        except Exception:
            self._model = None

    def embed(self, texts: list[str]) -> list[list[float]]:
        self._load_model()

        if self._model is not None:
            vectors = self._model.encode(
                texts,
                normalize_embeddings=True
            )
            return [vector.tolist() for vector in vectors]

        return [self._fallback_embed(text) for text in texts]

    def _fallback_embed(self, text: str) -> list[float]:
        vector = [0.0] * FALLBACK_EMBEDDING_DIM

        for token in TOKEN_RE.findall(text.lower()):
            digest = hashlib.sha256(token.encode("utf-8")).digest()

            index = (
                int.from_bytes(digest[:4], "big")
                % FALLBACK_EMBEDDING_DIM
            )

            sign = 1.0 if digest[4] % 2 == 0 else -1.0

            vector[index] += sign

        norm = math.sqrt(
            sum(value * value for value in vector)
        ) or 1.0

        return [
            value / norm
            for value in vector
        ]


@lru_cache(maxsize=1)
def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()

