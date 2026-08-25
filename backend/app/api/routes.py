from fastapi import APIRouter, HTTPException, Request
from app.api.rate_limit import RateLimiter
from app.api.schemas import (

    EvidenceResponse,
    QueryRequest,
    QueryResponse,
)
from app.query.modes import QueryMode
from app.query.orchestrator import QueryOrchestrator


router = APIRouter()
rate_limiter = RateLimiter(
    max_requests=14,
    window_seconds=60,
)

@router.post(
    "/query",
    response_model=QueryResponse,
)
async def query_medical_knowledge(
    request: QueryRequest,
    http_request: Request,
) -> QueryResponse:
    client_ip = (
        http_request.client.host
        if http_request.client
        else "unknown"
    )

    if not rate_limiter.allow(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later.",
        )
    orchestrator: QueryOrchestrator = (
        http_request.app.state.query_engine
    )

    result = orchestrator.execute(
        request.query,
        mode=QueryMode.AUTO,
    )

    return QueryResponse(
        success=result.success,
        query=result.query,
        answer=result.answer,
        evidence=[
            EvidenceResponse(
                source=str(
                    item.get(
                        "source",
                        "Kuzu medical graph",
                    )
                ),
                type=str(
                    item.get(
                        "type",
                        "graph",
                    )
                ),
                title=str(
                    item.get(
                        "title",
                        item.get(
                            "data",
                            {},
                        ).get(
                            "target",
                            "",
                        )
                        if isinstance(
                            item.get("data"),
                            dict,
                        )
                        else "",
                    )
                ),
                content=str(
                    item.get(
                        "content",
                        item.get(
                            "data",
                            "",
                        ),
                    )
                ),
            )
            for item in result.evidence
        ],
        error=result.error,
    )