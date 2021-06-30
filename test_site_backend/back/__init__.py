from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import router
from .models import *


def create_app(mode=None):
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost",
            "http://localhost:8080",
            "http://localhost:9090",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    async def startup():
        # create db tables
        if mode == "TESTING":
            return

        async with engine.begin() as conn:
            await conn.run_sync(BaseModel.metadata.drop_all)
            await conn.run_sync(BaseModel.metadata.create_all)

        async with session_maker() as session:
            try:
                user_model = UserModel(
                    email="admin@admin.com",
                    permissions=ActionEnum.VIEW | ActionEnum.EDIT | ActionEnum.CREATE
                )

                session.add(user_model)
                await session.commit()
            finally:
                await session.close()

    app.include_router(
        router,
    )
    return app
