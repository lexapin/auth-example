from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi_permissions import Allow
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from .models import *
from .schemas import CreateNewUserSchema, GetAndEditUserSchema, AuthSchema
from .utils import check_user_auth
from .enums import ActionEnum
from .permissions import Permission

router = APIRouter()


@router.get("/users/", tags=["users"], dependencies=[Depends(check_user_auth)],
            response_model=List[GetAndEditUserSchema])
async def read_users(
        acls: list = Permission("all", [(Allow, ActionEnum.VIEW, "all"), ]),
        session: AsyncSession = Depends(get_database_session)):
    return (await session.execute(select(UserModel))).scalars().all()  # тут нужна пагинация (я ее не делал)


@router.post("/users/", tags=["users"], dependencies=[Depends(check_user_auth)],
             response_model=GetAndEditUserSchema)
async def create_user(new_user_data: CreateNewUserSchema, response: Response,
                      acls: list = Permission("all", [(Allow, ActionEnum.CREATE, "all"), ]),
                      async_session: AsyncSession = Depends(get_database_session)):
    user_model = (await async_session.execute(select(UserModel).filter(
        UserModel.email == new_user_data.email
    ))).scalars().first()
    if user_model:
        raise HTTPException(403)
    user_model = UserModel(**new_user_data.dict())
    async_session.add(user_model)
    await async_session.flush()
    response.status_code = 201
    return user_model


@router.put("/users/", tags=["users"], dependencies=[Depends(check_user_auth)],
            response_model=GetAndEditUserSchema)
async def edit_user(user_params: GetAndEditUserSchema,
                    acls: list = Permission("all", [(Allow, ActionEnum.EDIT, "all"), ]),
                    async_session: AsyncSession = Depends(get_database_session)):
    user_model = (await async_session.execute(select(UserModel).filter(
        UserModel.email == user_params.email,
        UserModel.id == user_params.id
    ))).scalars().first()
    if not user_model:
        raise HTTPException(404)
    user_model.is_active = user_params.is_active
    user_model.permissions = user_params.permissions
    await async_session.flush()
    return user_model


@router.post("/users/auth", tags=["auth"], response_model=bytes)
async def auth(auth_data: AuthSchema,
               async_session: AsyncSession = Depends(get_database_session)):
    stmt = select(UserModel).filter(UserModel.email == auth_data.email)
    user_model = (await async_session.execute(stmt)).scalars().first()
    if not user_model:
        return HTTPException(404)
    return user_model.generate_token()
