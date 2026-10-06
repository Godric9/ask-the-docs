from typing import Annotated, Literal

from pydantic import AfterValidator, BaseModel


def is_tronced(value: float):
    if value < 0 or value > 1:
        raise ValueError(f"{value} is not between 0 and 1")
    return value


class Citation(BaseModel):
    n: int
    source: str
    section: str
    supported: bool


class AskResponse(BaseModel):
    answer: str
    citations: list[Citation]
    confidence: Annotated[float, AfterValidator(is_tronced)]
    flags: list[str]


class GoldenCase(BaseModel):
    id: str
    question: str
    reference_answer: str
    sources: list[str]
    type: Literal["simple", "multihop", "no_answer", "ambiguous"]
    difficulty: int
