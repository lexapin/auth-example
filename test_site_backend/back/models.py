import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.future import select

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from .enums import ActionEnum

database_url = "postgresql+asyncpg://backend:backend@postgres_backend:5432/backend_db"
# database_url = "postgresql+asyncpg://partner:partner@localhost:5432/test_teachu"
engine = create_async_engine(database_url,
                             # pool_size=20,
                             # max_overflow=0,
                            )
session_maker = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
BaseModel = declarative_base()


async def get_database_session():
    global session_maker
    async with session_maker() as session:
        try:
            yield session
            await session.commit()
        finally:
            await session.close()


class UserModel(BaseModel):
    __tablename__ = "users"
    id = sa.Column(sa.Integer, primary_key=True)
    email = sa.Column(sa.String(128), unique=True, index=True)
    is_active = sa.Column(sa.Boolean, nullable=False, server_default='TRUE')
    permissions = sa.Column(sa.Integer, nullable=False, server_default='0')

    def generate_token(self):
        s = Serializer("secret-key", expires_in=3600)
        return s.dumps({"email": self.email})

    @classmethod
    async def get_user_by_token(cls, async_session: AsyncSession, token: str):
        s = Serializer("secret-key")
        try:
            data = s.loads(token)
            email = data["email"]
            user = (await async_session.execute(select(UserModel).filter(
                UserModel.email == email
            ))).scalars().first()
        except BaseException as err:
            return None
        else:
            return user

    @property
    def principals(self):
        return [item.value for item in ActionEnum if item & self.permissions]
