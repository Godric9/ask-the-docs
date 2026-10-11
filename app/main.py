from functools import lru_cache

from anthropic import Anthropic
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastembed import TextEmbedding
from pydantic import BaseModel, Field
from qdrant_client.http.exceptions import ResponseHandlingException
from sentence_transformers import CrossEncoder

from ask_the_docs.config import MODEL_NAME, RERANKER_NAME
from ask_the_docs.generate import ask_avec_contexte
from ask_the_docs.ingest import get_client
from ask_the_docs.models import AskResponse

load_dotenv()
app = FastAPI()


class AskRequest(BaseModel):
    question: str = Field(min_length=1)


@lru_cache(maxsize=1)
def deps():
    return (
        Anthropic(),
        get_client(),
        TextEmbedding(model_name=MODEL_NAME),
        CrossEncoder(RERANKER_NAME),
    )


@app.post("/ask")
def ask_endpoint(request: AskRequest) -> AskResponse:
    try:
        reponse, _ = ask_avec_contexte(request.question, *deps())
    except ResponseHandlingException:
        raise HTTPException(status_code=503, detail="Qdrant injoignable")
    return reponse
