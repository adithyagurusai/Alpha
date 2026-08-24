from fastapi import APIRouter, Request

from app.api.schemas import (
    EvidenceResponse,
    QueryRequest,
    QueryResponse,
)
from app.query.engine import MedicalQueryEngine
from app.response.formatter import MedicalResponseFormatter


router = APIRouter()


@router.post(
    "/query",
    response_model=QueryResponse,
)
async def query_medical_knowledge(
    request: QueryRequest,
    http_request: Request,
) -> QueryResponse:

    engine: MedicalQueryEngine = (
        http_request.app.state.query_engine
    )

    result = engine.execute(
        request.query
    )

    formatter = MedicalResponseFormatter()

    response = formatter.format(
        request.query,
        result,
    )

    return QueryResponse(
        success=response.success,
        query=response.query,
        answer=response.answer,
        evidence=[
            EvidenceResponse(
                source=item.source,
                type=item.type,
                title=item.title,
                content=item.content,
            )
            for item in response.evidence
        ],
        error=response.error,
    )