from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient
from asapi import Injected, bind

if TYPE_CHECKING:
    from httpx import AsyncClient

router = APIRouter()


@router.get("/test")
async def ping(client: Injected[AsyncClient]) -> str:
    resp = await client.get('http://example.com')
    resp.raise_for_status()
    return f"Got {len(resp.text)} bytes"

def create_app(client: AsyncClient) -> FastAPI:
    from httpx import AsyncClient

    app = FastAPI()
    bind(app, AsyncClient, client)
    app.include_router(router)
    return app


async def test() -> None:
    from httpx import AsyncClient

    async with AsyncClient() as client:
        app = create_app(client)
        client = TestClient(app)

        response = client.get("/test")
        assert response.status_code == 200, f"{response.status_code=}: {response.text=}"


if __name__ == "__main__":
    import anyio

    anyio.run(test)
