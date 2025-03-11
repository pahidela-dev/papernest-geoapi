from fastapi import FastAPI
from routers.search import router

app = FastAPI()

app.include_router(router)
