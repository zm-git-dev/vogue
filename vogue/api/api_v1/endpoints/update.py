#!/usr/bin/env python

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from urllib.parse import urlsplit, parse_qs, urlencode

router = APIRouter()


@router.get("/redirect")
async def update(request: Request, year: int):
    url = request.headers.get("referer")
    query = urlsplit(url).query
    params = parse_qs(query)
    params.update({"year": [year]})
    params_url = urlencode(params, doseq=True)

    return RedirectResponse(f"{url.split('?')[0]}?{params_url}")
