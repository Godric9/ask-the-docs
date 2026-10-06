import argparse
import os
import sys

from anthropic import Anthropic
from dotenv import load_dotenv
from fastembed import TextEmbedding
from qdrant_client.http.exceptions import ResponseHandlingException
from sentence_transformers import CrossEncoder

from ask_the_docs.config import COLLECTION, MODEL_NAME, RERANKER_NAME
from ask_the_docs.generate import ask_avec_contexte
from ask_the_docs.ingest import get_client, ingest
from ask_the_docs.search import bm25_search, dense_search, hybrid_search


def construire_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ask_the_docs")
    sous = parser.add_subparsers(dest="commande", required=True)
    sous.add_parser("ingest").add_argument("--reset", action="store_true")
    search = sous.add_parser("search")
    search.add_argument("question")
    search.add_argument("--k", type=int, default=5)
    search.add_argument("--mode", choices=["dense", "bm25", "hybrid"], default="hybrid")
    sous.add_parser("ask").add_argument("question")
    return parser


def index_pret(client) -> bool:
    if not client.collection_exists(COLLECTION) or client.count(COLLECTION).count == 0:
        print(
            "Erreur : collection absente ou vide. Lance d'abord : ingest",
            file=sys.stderr,
        )
        return False
    return True


def cmd_ingest(args) -> int:
    if args.reset:
        if input(f"Supprimer la collection '{COLLECTION}' ? [y/N] ").lower() != "y":
            return 0
        client = get_client()
        if client.collection_exists(COLLECTION):
            client.delete_collection(COLLECTION)
    ingest()
    return 0


def cmd_search(args) -> int:
    client = get_client()
    if not index_pret(client):
        return 1
    modele = TextEmbedding(model_name=MODEL_NAME)
    if args.mode == "dense":
        points = dense_search(args.question, client, modele, args.k)
    elif args.mode == "bm25":
        points = bm25_search(args.question, client, args.k)
    else:
        points = hybrid_search(args.question, client, modele, k=args.k)
    for rang, p in enumerate(points, start=1):
        extrait = p.payload["text"][:100].replace("\n", " ")
        print(f"{rang}. {p.payload['source']} #{p.payload['chunk_id']}  {extrait!r}")
    return 0


def cmd_ask(args) -> int:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Erreur : ANTHROPIC_API_KEY absente. Vérifie ton .env.", file=sys.stderr)
        return 3
    client = get_client()
    if not index_pret(client):
        return 1
    reponse, _ = ask_avec_contexte(
        args.question,
        Anthropic(),
        client,
        TextEmbedding(model_name=MODEL_NAME),
        CrossEncoder(RERANKER_NAME),
    )
    print(reponse.answer)
    for c in reponse.citations:
        print(f"[{c.n}] {c.source} {c.section}".rstrip())
    for flag in reponse.flags:
        print(f"Avertissement : {flag}")
    return 0


COMMANDES = {"ingest": cmd_ingest, "search": cmd_search, "ask": cmd_ask}


def main(argv=None) -> int:
    args = construire_parser().parse_args(argv)  # argparse quitte déjà avec le code 2
    load_dotenv()
    try:
        return COMMANDES[args.commande](args)
    except ResponseHandlingException:
        print("Erreur : Qdrant injoignable.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
