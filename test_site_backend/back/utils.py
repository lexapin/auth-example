from fastapi import Request, Header, Depends, HTTPException
from sqlalchemy.orm import Session
from .models import get_database_session, UserModel
from sqlalchemy.ext.asyncio import AsyncSession


async def check_user_auth(
        request: Request,
        authorization: str = Header(None),
        async_session: AsyncSession = Depends(get_database_session)):
    if authorization is None:
        raise HTTPException(401)
    user_model = await UserModel.get_user_by_token(async_session, authorization)
    if user_model is None:
        raise HTTPException(401)
    user_model.generate_token()
    request.state.user = user_model
