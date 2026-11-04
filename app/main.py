import logging

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.presentation.api.routers.create_order import router as create_order
from app.presentation.api.routers.get_order import router as get_order_router
from app.presentation.api.routers.payment_callback import router as payment_router
from app.presentation.api.lifespan import lifespan

logger = logging.getLogger(__name__)

app = FastAPI(lifespan=lifespan)


app.include_router(create_order)
app.include_router(get_order_router)
app.include_router(payment_router)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    logger.error(
        "Request validation failed: %s",
        exc.errors(),
    )
    logger.error(
        "Request body: %s",
        exc.body,
    )

    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )