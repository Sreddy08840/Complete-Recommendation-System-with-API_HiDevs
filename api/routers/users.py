
from fastapi import APIRouter, Depends
from typing import List
from ..schemas import User, UserCreate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[User])
async def get_users():
    return []


@router.post("/", response_model=User)
async def create_user(user: UserCreate):
    return user

