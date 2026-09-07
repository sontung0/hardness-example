"""HTTP endpoint handlers for /register, /login, /me."""

from fastapi import APIRouter, Depends, HTTPException

from auth import create_access_token, get_current_user
from models import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from services import authenticate_user, get_current_user_profile, register_user

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(req: RegisterRequest):
    try:
        register_user(req.username, req.password, req.name)
    except ValueError as e:
        status = 409 if "already exists" in str(e) else 400
        raise HTTPException(status_code=status, detail=str(e))

    token = create_access_token(req.username.lower())
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest):
    try:
        authenticate_user(req.username, req.password)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(req.username)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
def me(username: str = Depends(get_current_user)):
    try:
        profile = get_current_user_profile(username)
    except ValueError:
        raise HTTPException(status_code=401, detail="User not found")

    return UserResponse(**profile)
