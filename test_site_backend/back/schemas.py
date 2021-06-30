from pydantic import BaseModel as Schema, EmailStr


class CreateNewUserSchema(Schema):
    email: EmailStr
    is_active: bool = True
    permissions: int


class GetAndEditUserSchema(CreateNewUserSchema):
    id: int

    class Config:
        orm_mode = True


class AuthSchema(Schema):
    email: EmailStr
