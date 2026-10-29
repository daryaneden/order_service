from fastapi import FastAPI
from app.presentation.api.routers.create_order import router as create_order

app = FastAPI()

app.include_router(create_order)