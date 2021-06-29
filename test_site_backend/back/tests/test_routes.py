import pytest
from sqlalchemy.util import concurrency

from ..models import UserModel
from ..enums import ActionEnum


@pytest.mark.asyncio
async def test_auth(database_session, fastapi_client):
    user_model = UserModel(
        email="some@email.com",
        permissions=ActionEnum.VIEW | ActionEnum.EDIT | ActionEnum.CREATE
    )

    database_session.add(user_model)
    await database_session.commit()

    response = await fastapi_client.get("/users")
    assert response.status_code == 401

    response = await fastapi_client.post(
        "/users/auth",
        json={
           "email": "some@email.com"
        })
    assert response.status_code == 200
    token = response.json()

    response = await fastapi_client.get(
        "/users",
        headers={
            "Authorization": token
        })
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_new_user(database_session, fastapi_client):
    user_model = UserModel(
        email="some@email.com",
        permissions=ActionEnum.VIEW | ActionEnum.EDIT | ActionEnum.CREATE
    )
    database_session.add(user_model)
    await database_session.commit()

    token = await concurrency.greenlet_spawn(user_model.generate_token)

    response = await fastapi_client.post(
        "/users/",
        headers={
            "Authorization": token.decode("utf-8")
        },
        json={
            "email": "some@email.com",
            "is_active": True,
            "permissions": ActionEnum.VIEW
        })
    assert response.status_code == 403

    response = await fastapi_client.post(
        "/users/",
        headers={
            "Authorization": token.decode("utf-8")
        },
        json={
            "email": "some_new@email.com",
            "is_active": True,
            "permissions": 1
        })
    assert response.status_code == 201

    response = await fastapi_client.get(
        "/users",
        headers={
            "Authorization": token.decode("utf-8")
        })
    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_edit_user(fastapi_client, database_session):
    user_model = UserModel(
        email="some@email.com",
        permissions=ActionEnum.VIEW | ActionEnum.EDIT
    )
    database_session.add(user_model)
    await database_session.commit()
    token = await concurrency.greenlet_spawn(user_model.generate_token)

    response = await fastapi_client.post(
        "/users/",
        headers={
            "Authorization": token.decode("utf-8")
        },
        json={
            "email": "some_new@email.com",
            "is_active": True,
            "permissions": ActionEnum.VIEW
        })
    assert response.status_code == 403

    response = await fastapi_client.put(
        "/users/",
        headers={
            "Authorization": token.decode("utf-8")
        },
        json={
            "id": user_model.id,
            "email": user_model.email,
            "is_active": True,
            "permissions": ActionEnum.VIEW | ActionEnum.EDIT | ActionEnum.CREATE
        })
    assert response.status_code == 200

    response = await fastapi_client.post(
        "/users/",
        headers={
            "Authorization": token.decode("utf-8")
        },
        json={
            "email": "some_new@email.com",
            "is_active": True,
            "permissions": ActionEnum.VIEW
        })
    assert response.status_code == 201
