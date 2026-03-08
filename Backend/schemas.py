from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
import re

class Signup(BaseModel):
    """Schema for user signup"""
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    
    # ✅ FIXED: Added validation for name
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        # Allow letters, spaces, and common characters
        if not re.match(r"^[a-zA-Z\s\-']{2,}$", v):
            raise ValueError('Name contains invalid characters')
        return v.strip()
    
    # ✅ FIXED: Added validation for password strength
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        # Optional: enforce stronger passwords
        # if not re.search(r'[A-Z]', v) or not re.search(r'[0-9]', v):
        #     raise ValueError('Password must contain uppercase and numbers')
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