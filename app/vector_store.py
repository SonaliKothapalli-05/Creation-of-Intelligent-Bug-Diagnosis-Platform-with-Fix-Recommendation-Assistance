import json
import math
from pathlib import Path
from typing import Any

from app.config import COLLECTION_NAME, VECTOR_STORE_DIR
from app.models import BugChunk, SimilarBug


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left)) or 1.0
    right_norm = math.sqrt(sum(b * b for b in right)) or 1.0
    return dot / (left_norm * right_norm)


class JsonVectorStore:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _read(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _write(self, records: list[dict[str, Any]]) -> None:
        self.path.write_text(json.dumps(records, indent=2), encoding="utf-8")

    def reset(self) -> None:
        self._write([])

    def add(self, chunks: list[BugChunk], embeddings: list[list[float]]) -> None:
        existing = {record["id"]: record for record in self._read()}
        for chunk, embedding in zip(chunks, embeddings):
            existing[chunk.chunk_id] = {
                "id": chunk.chunk_id,
                "document": chunk.text,
                "metadata": chunk.metadata,
                "embedding": embedding,
            }
        self._write(list(existing.values()))

    def query(self, embedding: list[float], top_k: int) -> list[SimilarBug]:
        scored = []
        for record in self._read():
            scored.append((cosine_similarity(embedding, record["embedding"]), record))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [_to_similar_bug(record, score) for score, record in scored[:top_k]]


class ChromaVectorStore:
    def __init__(self, persist_dir: Path):
        import chromadb

        persist_dir.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(persist_dir))
        self.collection = self.client.get_or_create_collection(COLLECTION_NAME)

    def reset(self) -> None:
        try:
            self.client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass
        self.collection = self.client.get_or_create_collection(COLLECTION_NAME)

    def add(self, chunks: list[BugChunk], embeddings: list[list[float]]) -> None:
        if not chunks:
            return
        self.collection.upsert(
    ids=[chunk.chunk_id for chunk in chunks],
    documents=[chunk.text for chunk in chunks],
    metadatas=[chunk.metadata for chunk in chunks],
    embeddings=embeddings,
)
    def query(self, embedding: list[float], top_k: int) -> list[SimilarBug]:
        result = self.collection.query(query_embeddings=[embedding], n_results=top_k)
        matches: list[SimilarBug] = []
        ids = result.get("ids", [[]])[0]
        docs = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]
        for chunk_id, document, metadata, distance in zip(ids, docs, metadatas, distances):
            record = {"id": chunk_id, "document": document, "metadata": metadata or {}}
            matches.append(_to_similar_bug(record, 1.0 / (1.0 + float(distance))))
        return matches


def _to_similar_bug(record: dict[str, Any], score: float) -> SimilarBug:
    metadata = record.get("metadata") or {}
    return SimilarBug(
        chunk_id=record["id"],
        bug_id=str(metadata.get("bug_id", "")),
        title=str(metadata.get("title", "")),
        component=str(metadata.get("component", "")),
        severity=str(metadata.get("severity", "")),
        priority=str(metadata.get("priority", "")),
        status=str(metadata.get("status", "")),
        resolution=str(metadata.get("resolution", "")),
        score=round(float(score), 4),
        text=record.get("document", ""),
    )


def get_vector_store(force_json: bool = False):
    if not force_json:
        try:
            return ChromaVectorStore(VECTOR_STORE_DIR / "chroma")
        except Exception:
            pass
    return JsonVectorStore(VECTOR_STORE_DIR / "fallback_collection.json")

