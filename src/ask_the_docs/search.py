import math
import re
from collections import defaultdict
from functools import lru_cache

from fastembed import TextEmbedding
from qdrant_client import QdrantClient
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder

from .config import COLLECTION


def sigmoid(x):
    return 1 / (1 + math.exp(-x))

def dense_search(
    query: str, client: QdrantClient, model: TextEmbedding, k: int = 5
):
    vecteur = list(model.embed([query]))[0]
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


def bm25_search(query: str, client: QdrantClient, k: int = 5):
    bm25, points = _index(client)
    scores = bm25.get_scores(tokeniser(query))
    return [points[i] for i in scores.argsort()[-k:][::-1] if scores[i] > 0]


def fusion_rrf(liste_dense: list, liste_bm25: list, k: int = 60) -> list:
    scores : dict = defaultdict(float)
    par_id : dict = {}
    for liste in (liste_dense, liste_bm25):
        for rang, point in enumerate(liste, start=1):
            par_id[point.id] = point
            scores[point.id] += 1 / (k + rang)
    return [par_id[i] for i in sorted(scores, key=scores.get, reverse=True)]


def hybrid_search(query, client, modele, k=5, n=20):
    return fusion_rrf(dense_search(query, client, modele, n), bm25_search(query, client, n))[:k]

def rerank(query: str, candidats: list, cross_encoder: CrossEncoder, k: int = 5) -> list:
    paires = [(query, candidat.payload["text"]) for candidat in candidats]
    scores = cross_encoder.predict(paires)
    return sorted(zip(candidats, scores), key=lambda paire: paire[1], reverse=True)[:k]