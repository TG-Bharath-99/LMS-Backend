from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
import re

class Signup(BaseModel):
    """Schema for user signup"""
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        # Allow letters (any language), spaces, hyphens, apostrophes, dots
        if len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters')
        return v.strip()

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v


class Login(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user response"""
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True


class CourseResponse(BaseModel):
    """Schema for course response"""
    id: int
    title: str

    class Config:
        from_attributes = True


class CourseTopicResponse(BaseModel):
    """Schema for course topic response"""
    id: int
    title: str
    link: str

    class Config:
        from_attributes = True