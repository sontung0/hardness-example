from pydantic import BaseModel


class RegisterRequest(BaseModel):
    username: str
    password: str
    name: str


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    username: str
    name: str


class UpdateProfileRequest(BaseModel):
    name: str | None = None


class ErrorResponse(BaseModel):
    detail: str
