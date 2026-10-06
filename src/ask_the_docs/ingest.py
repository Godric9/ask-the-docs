import re
import uuid
from pathlib import Path

import numpy as np
from fastembed import TextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from .config import COLLECTION, MODEL_NAME


def get_client() -> QdrantClient:
    return QdrantClient(host="localhost", port=6333)


def ensure_collection(client: QdrantClient, dim: int) -> None:
    if not client.collection_exists(COLLECTION):
        client.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
        )


def fix_size_chunker(text: str, size: int, overlap: int = 0) -> list[str]:
    """Splitting text by fixed size."""

    assert size > overlap

    chunks = []

    pas = size - overlap
    for i in range(0, len(text), pas):
        chunks.append(text[i : i + size])

    return chunks


def similarite_cosinus(v1, v2) -> float:
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))


def semantic_chunker(
    text: str, model: TextEmbedding, seuil_percentile: float = 95
) -> list[str]:
    phrases = text.split(". ")
    if len(phrases) <= 1:
        return phrases

    vectors = list(model.embed(phrases))

    similarites = [
        similarite_cosinus(vectors[i], vectors[i + 1]) for i in range(len(vectors) - 1)
    ]
    seuil = np.percentile(similarites, 100 - seuil_percentile)

    chunks = []
    chunk_courant = phrases[0]
    for i in range(len(similarites)):
        if similarites[i] >= seuil:
            chunk_courant += ". " + phrases[i + 1]
        else:
            chunks.append(chunk_courant)
            chunk_courant = phrases[i + 1]
    chunks.append(chunk_courant)
    return chunks


SEPARATORS = ["\n\n", "\n", ".", "?", "!", " ", ""]


def recursif_token_chunker(
    text: str, chunk_size: int, separators: list[str] = SEPARATORS
) -> list[str]:
    """Splitting text by recursively look at characters.

    Recursively tries to split by different characters to find one
    that works.
    """

    if len(text) <= chunk_size or not separators:
        return [text]

    sep, smaller_separator = separators[0], separators[1:]

    if sep:
        splits = text.split(sep=sep)
    else:
        splits = [text]

    chunks = []
    current_chunks = ""

    for i, split in enumerate(splits):
        segment = current_chunks + (sep if current_chunks else "") + split

        if len(segment) <= chunk_size:
            current_chunks = segment
        else:
            if current_chunks:
                chunks.extend(
                    recursif_token_chunker(
                        text=current_chunks + sep,
                        separators=smaller_separator,
                        chunk_size=chunk_size,
                    )
                )
            current_chunks = split

    if current_chunks:
        chunks.extend(
            recursif_token_chunker(
                text=current_chunks, separators=smaller_separator, chunk_size=chunk_size
            )
        )
    return chunks


def clean(text: str) -> str:
    if text.startswith("---"):
        text = text.split("---", 2)[-1]
    return re.sub(r"\{\{<.*?>\}\}", "", text)


def read() -> dict[str, str]:
    return {
        str(path): clean(path.read_text(encoding="utf-8"))
        for path in Path("data").rglob("*.md")
    }


def ingest() -> None:
    model = TextEmbedding(model_name=MODEL_NAME)
    client = get_client()
    ensure_collection(client, dim=384)

    points = []
    reads = read()
    for source, texte in reads.items():
        chunks = recursif_token_chunker(texte, chunk_size=500)
        vecteurs = list(model.embed(chunks))
        for chunk_id, (chunk, vecteur) in enumerate(zip(chunks, vecteurs)):
            point_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{source}:{chunk_id}"))
            points.append(
                PointStruct(
                    id=point_id,
                    vector=vecteur,
                    payload={
                        "source": source,
                        "chunk_id": chunk_id,
                        "text": chunk,
                    },
                )
            )

    client.upsert(collection_name=COLLECTION, points=points)
    print(f"Ingested {len(points)} chunks from {len(reads)} files.")
