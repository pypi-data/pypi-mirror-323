from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

if TYPE_CHECKING:
    from httpx import AsyncClient

app = FastAPI()


@app.get("/test")
async def ping(client: Annotated[AsyncClient, Depends(lambda: AsyncClient())]) -> str:
    resp = await client.get('http://example.com')
    resp.raise_for_status()
    return f"Got {len(resp.text)} bytes"



async def test() -> None:
    from httpx import AsyncClient

    async with AsyncClient() as client:
        client = TestClient(app)

        response = client.get("/test")
        assert response.status_code == 200, f"{response.status_code=}: {response.text=}"


if __name__ == "__main__":
    import anyio

    anyio.run(test)
