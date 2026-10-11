from fastapi.testclient import TestClient
from qdrant_client.http.exceptions import ResponseHandlingException

import app.main as m
from ask_the_docs.models import AskResponse

client = TestClient(m.app)


def test_question_vide_422():
    assert client.post("/ask", json={"question": ""}).status_code == 422


def test_qdrant_injoignable_503(monkeypatch):
    monkeypatch.setattr(m, "deps", lambda: (None, None, None, None))

    def panne(*args):
        raise ResponseHandlingException(Exception("down"))

    monkeypatch.setattr(m, "ask_avec_contexte", panne)
    assert client.post("/ask", json={"question": "x"}).status_code == 503


def test_reponse_200(monkeypatch):
    monkeypatch.setattr(m, "deps", lambda: (None, None, None, None))
    ok = AskResponse(answer="ok", citations=[], confidence=0.9, flags=[])
    monkeypatch.setattr(m, "ask_avec_contexte", lambda *args: (ok, []))
    r = client.post("/ask", json={"question": "x"})
    assert r.status_code == 200
    assert r.json()["answer"] == "ok"
