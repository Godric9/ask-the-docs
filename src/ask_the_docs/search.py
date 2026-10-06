import re
from functools import lru_cache

from fastembed import TextEmbedding
from qdrant_client import QdrantClient
from rank_bm25 import BM25Okapi

from .config import COLLECTION


def dense_search(
    question: str, client: QdrantClient, modele: TextEmbedding, k: int = 5
):
    vecteur = list(modele.embed([question]))[0]
    return client.query_points(
        collection_name=COLLECTION, query=vecteur, limit=k
    ).points


def tokeniser(texte: str) -> list[str]:
    return re.findall(r"\w+", texte.lower())


@lru_cache(maxsize=1)
def _index(client: QdrantClient):
    points, offset = [], None
    while True:
        page, offset = client.scroll(
            collection_name=COLLECTION, limit=256, offset=offset, with_payload=True
        )
        points += page
        if offset is None:
            break
    return BM25Okapi([tokeniser(p.payload["text"]) for p in points]), points


def bm25_search(question: str, client: QdrantClient, k: int = 5):
    bm25, points = _index(client)
    scores = bm25.get_scores(tokeniser(question))
    return [points[i] for i in scores.argsort()[-k:][::-1] if scores[i] > 0]
