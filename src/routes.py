"""HTTP endpoint handlers for /register, /login, /me."""

from fastapi import APIRouter, Depends, HTTPException

from auth import create_access_token, get_current_user
from errors import NotFoundError
from models import LoginRequest, RegisterRequest, TokenResponse, UpdateProfileRequest, UserResponse
from services import authenticate_user, get_current_user_profile, register_user, update_user_profile

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(req: RegisterRequest):
    register_user(req.username, req.password, req.name)
    token = create_access_token(req.username.lower())
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest):
    authenticate_user(req.username, req.password)
    token = create_access_token(req.username)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
def me(username: str = Depends(get_current_user)):
    profile = get_current_user_profile(username)
    return UserResponse(**profile)


@router.patch("/me", response_model=UserResponse)
def update_me(req: UpdateProfileRequest, username: str = Depends(get_current_user)):
    if req.name is None:
        raise HTTPException(status_code=400, detail="At least one field must be provided")

    profile = update_user_profile(username, req.name)
    return UserResponse(**profile)
