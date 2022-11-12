from typing import Optional
from fastapi import Form
from pydantic import BaseModel


class UserRegForm(BaseModel):
    username: Optional[str] = Form(...)
    phone: Optional[int] = Form(...)
    password: Optional[str] = Form(...)
    fullname: Optional[str] = Form(...)
    vehicle: Optional[str] = Form(...)
    status: Optional[str] = Form(...)
    yearvalid: Optional[int] = Form(...)
    admin: Optional[bool]

    class Config:
        orm_mode = True


class editForm(BaseModel):
    username: Optional[str] = Form(...)
    phone: Optional[int] = Form(...)
    fullname: Optional[str] = Form(...)
    vehicle: Optional[str] = Form(...)
    status: Optional[str] = Form(...)
    yearvalid: Optional[int] = Form(...)
    admin: Optional[bool]

    class Config:
        orm_mode = True


class EmailForm(BaseModel):
    username: Optional[str] = Form(...)
    phone: Optional[int] = Form(...)
    fullname: Optional[str] = Form(...)
    email: Optional[str] = Form(...)
    msg: Optional[str] = Form(...)

    class Config:
        orm_mode = True
