"""App factory — FastAPI application with route registration."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from routes import router


def create_app() -> FastAPI:
    app = FastAPI(title="Simple REST API — Auth")

    # Custom validation error handler: map Pydantic 422 → 400 with {"detail": str}
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = exc.errors()
        if errors:
            first = errors[0]
            loc = first.get("loc", [])
            field = loc[-1] if loc else "input"
            msg = first.get("msg", "Validation error")
            detail = f"{field}: {msg}"
        else:
            detail = "Validation error"
        return JSONResponse(
            status_code=400,
            content={"detail": detail},
        )

    app.include_router(router)
    return app


app = create_app()
