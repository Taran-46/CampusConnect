from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


import re

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class IssueCategory(str, Enum):
    CLASSROOM = "Classroom"
    CAMPUS = "Campus"
    LOST_AND_FOUND = "Lost & Found"
    GENERAL = "General"


class IssueStatus(str, Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"


# -------------------------------------------------------------
# User Models
# -------------------------------------------------------------
class UserRegister(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100, description="Full name of student")
    email: str = Field(..., description="College or personal email address")
    password: str = Field(..., min_length=6, max_length=128, description="Password (at least 6 characters)")
    department: str = Field(..., min_length=2, max_length=100, description="Department and year, e.g., CS - 3rd Year")

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, value: str) -> str:
        clean = value.strip().lower()
        if not EMAIL_REGEX.match(clean):
            raise ValueError("Invalid email format. Please provide a valid address like user@campus.edu")
        return clean

    @field_validator("full_name", "department")
    @classmethod
    def strip_whitespace(cls, value: str) -> str:
        clean = value.strip()
        if not clean:
            raise ValueError("Field cannot be empty or whitespace only")
        return clean


class UserLogin(BaseModel):
    email: str = Field(..., description="Student's registered email")
    password: str = Field(..., min_length=1, description="Student's password")

    @field_validator("email")
    @classmethod
    def validate_login_email(cls, value: str) -> str:
        clean = value.strip().lower()
        if not EMAIL_REGEX.match(clean):
            raise ValueError("Invalid email format")
        return clean


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    department: str
    created_at: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# -------------------------------------------------------------
# Issue Models
# -------------------------------------------------------------
class IssueCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=150, description="Brief summary of the issue")
    description: str = Field(..., min_length=5, max_length=3000, description="Detailed explanation of the issue")
    category: IssueCategory = Field(..., description="Category: Classroom, Campus, Lost & Found, General")

    @field_validator("title", "description")
    @classmethod
    def strip_whitespace(cls, value: str) -> str:
        clean = value.strip()
        if not clean:
            raise ValueError("Field cannot be empty or whitespace only")
        return clean


class IssueStatusUpdate(BaseModel):
    status: IssueStatus = Field(..., description="Target status: Open, In Progress, Resolved")


class IssueResponse(BaseModel):
    id: int
    title: str
    description: str
    category: str
    status: str
    user_id: int
    submitted_by_name: Optional[str] = None
    submitted_by_department: Optional[str] = None
    created_at: str
    updated_at: str


class MessageResponse(BaseModel):
    message: str
