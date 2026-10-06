import re

from .config import MAX_TOKENS, MODEL
from .models import AskResponse, Citation
from .search import hybrid_search, rerank

INSTRUCTIONS = """Réponds uniquement à partir des passages numérotés ci-dessous.
Après chaque affirmation, cite le passage qui la soutien, au format `[n]`.
Si les passages ne contiennent pas la réponse, dis le. N'invente rien.

"""


def extraire_numeros(reponse: str) -> list[int]:
    return list(dict.fromkeys(int(n) for n in re.findall(r"\[(\d+)\]", reponse)))


def construire_prompt(question: str, points: list) -> str:
    contexte = "\n".join(
        f"[{i + 1}] {chunk.payload['text']}" for i, chunk in enumerate(points)
    )
    prompt = f"{INSTRUCTIONS}\n\n{contexte}\n\nQuestion : {question}"
    return prompt


def ask_avec_contexte(
    question, client_llm, client_qdrant, modele, cross_encoder
) -> tuple[AskResponse, list[str]]:

    candidats = hybrid_search(question, client_qdrant, modele, k=20)
    classes = rerank(question, candidats, cross_encoder)
    points = [p for p, _ in classes]

    prompt = construire_prompt(question, points)

    reponse = client_llm.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}],
    )

    texte_reponse = reponse.content[0].text if reponse.content else ""

    numeros = extraire_numeros(texte_reponse)
    citations_valides = [
        Citation(
            n=n,
            source=points[n - 1].payload["source"],
            section=points[n - 1].payload.get("section", ""),
            supported=True,
        )
        for n in numeros
        if 1 <= n <= len(points)
    ]
    hors_contexte = [
        f"citation [{n}] hors contexte" for n in numeros if not 1 <= n <= len(points)
    ]

    return AskResponse(
        answer=texte_reponse,
        citations=citations_valides,
        confidence=1.0,
        flags=hors_contexte,
    ), [p.payload["text"] for p in points]
