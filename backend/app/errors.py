from __future__ import annotations

from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: dict[str, Any] | None = None


class ApiError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(message)


async def api_error_handler(_: Request, exc: ApiError) -> JSONResponse:
    payload = ErrorResponse(code=exc.code, message=exc.message, details=exc.details)
    return JSONResponse(status_code=exc.status_code, content=payload.model_dump(exclude_none=True))


async def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    errors: list[dict[str, Any]] = []
    for error in exc.errors():
        sanitized = dict(error)
        if "ctx" in sanitized:
            sanitized["ctx"] = {key: str(value) for key, value in sanitized["ctx"].items()}
        errors.append(sanitized)
    if any("URL invalida ou protocolo nao permitido" in str(error.get("msg", "")) for error in errors):
        payload = ErrorResponse(
            code="invalid_url",
            message="URL invalida ou protocolo nao permitido.",
            details={"field": "url"},
        )
        return JSONResponse(status_code=400, content=payload.model_dump(exclude_none=True))
    payload = ErrorResponse(
        code="validation_error",
        message="Requisicao invalida.",
        details={"errors": errors},
    )
    return JSONResponse(status_code=422, content=payload.model_dump(exclude_none=True))


async def unhandled_error_handler(_: Request, exc: Exception) -> JSONResponse:
    payload = ErrorResponse(code="internal_error", message="Erro interno inesperado.")
    return JSONResponse(status_code=500, content=payload.model_dump(exclude_none=True))
