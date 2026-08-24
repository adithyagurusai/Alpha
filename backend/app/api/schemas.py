from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Natural-language medical query.",
    )


class EvidenceResponse(BaseModel):
    source: str
    type: str
    title: str
    content: str


class QueryResponse(BaseModel):
    success: bool
    query: str
    answer: str
    evidence: list[EvidenceResponse]
    error: str | None = None