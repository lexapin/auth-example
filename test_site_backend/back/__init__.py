from fastapi import FastAPI
from .routes import router


def create_app(mode=None):
    app = FastAPI()

    app.include_router(
        router,
    )
    return app
