from fastapi import FastAPI
from app.presentation.api.routers.create_order import router as create_order
from app.presentation.api.routers.get_order import router as get_order_router
from app.presentation.api.routers.payment_callback import router as payment_router


app = FastAPI()

app.include_router(create_order)
app.include_router(get_order_router)
app.include_router(payment_router)