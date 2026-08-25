from fastapi import APIRouter, Request

from app.api.schemas import (
    EvidenceResponse,
    QueryRequest,
    QueryResponse,
)
from app.query.modes import QueryMode
from app.query.orchestrator import QueryOrchestrator


router = APIRouter()


@router.post(
    "/query",
    response_model=QueryResponse,
)
async def query_medical_knowledge(
    request: QueryRequest,
    http_request: Request,
) -> QueryResponse:

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