import hashlib
import hmac
import secrets

from fastapi import HTTPException, Request

from vogue.settings import settings


async def verify_signature(
    request: Request,
) -> None:
    digester = hmac.new(key=settings.hmac_key.encode(), digestmod=hashlib.sha256)
    request_body = await request.body()
    digester.update(request_body)
    received_digest = request.headers.get("authorization")
    expected_digest = "hmac " + digester.hexdigest()
    if not secrets.compare_digest(received_digest, expected_digest):
        raise HTTPException(status_code=401, detail="Invalid signature")
