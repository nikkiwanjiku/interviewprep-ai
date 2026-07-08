from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    career_goal: str


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    career_goal: str

    class Config:
        from_attributes = True