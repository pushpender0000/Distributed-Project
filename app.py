from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
import httpx
import os

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:8001")
ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL", "http://order-service:8002")

app = FastAPI(title="Distributed Shop – API Gateway")

@app.get("/healthz")
async def healthz():
    return {"status": "ok", "service": "gateway"}

# Simple proxy helper
async def proxy(request: Request, base_url: str, path: str):
    url = f"{base_url}{path}"
    method = request.method
    headers = dict(request.headers)
    # Remove hop-by-hop headers if any (basic cleanup for demo)
    headers.pop("host", None)

    body = await request.body()
    params = dict(request.query_params)

    async with httpx.AsyncClient(follow_redirects=True) as client:
        resp = await client.request(method, url, headers=headers, content=body, params=params, timeout=30.0)
        return Response(content=resp.content, status_code=resp.status_code, headers=dict(resp.headers))

# Routes to services
@app.api_route("/users{full_path:path}", methods=["GET", "POST"])
async def users_proxy(full_path: str, request: Request):
    return await proxy(request, USER_SERVICE_URL, f"/users{full_path}")

@app.api_route("/orders{full_path:path}", methods=["GET", "POST"])
async def orders_proxy(full_path: str, request: Request):
    return await proxy(request, ORDER_SERVICE_URL, f"/orders{full_path}")
