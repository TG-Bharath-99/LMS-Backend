from typing import Optional
from pydantic import BaseModel,EmailStr,Field
import re

class Signup(BaseModel):
    name:str
    email:EmailStr
    password:str=Field(min_length=8)

class Login(BaseModel):    
    email:EmailStr
    password:str

class UserResponse(BaseModel):
    id:int
    name:str
    email:EmailStr
    class Config:
        from_attributes=True    