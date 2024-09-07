from pydantic import BaseModel, Field
from typing import Optional


class User(BaseModel):
    username: str
    email: str
    hashed_password: str
    role: str = "user"


class TokenData(BaseModel):
    username: Optional[str] = Field(None, description="The username of the user")
    role: Optional[str] = Field(None, description="The role of the user")


class UserRegistrationRequest(BaseModel):
    email: str = Field(..., max_length=50)
    password: str = Field(..., max_length=50)

class ThemeExtractionRequest(BaseModel):
    user_input: str = Field(..., max_length=1000)

class SimilarItemsRequest(BaseModel):
    text_input: str
