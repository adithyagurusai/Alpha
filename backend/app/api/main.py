from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.dependencies import build_query_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.query_engine = build_query_engine()

    yield

    app.state.query_engine = None


def create_app() -> FastAPI:
    app = FastAPI(
        title="Alpha Medical Knowledge API",
        version="0.1.0",
        description=(
            "Graph-first medical knowledge API powered by Kuzu "
            "with external FDA evidence support"
        ),
        lifespan=lifespan,
    )

    app.include_router(router)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {
            "status": "ok",
        }

    return app


app = create_app()