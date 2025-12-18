# main.py
from fastapi import FastAPI
from web.routes import router

app = FastAPI()

# ルーターをインクルード
app.include_router(router)
