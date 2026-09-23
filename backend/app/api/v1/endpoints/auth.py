"""
Authentication Endpoints for WeatherGPT (SIH PS 26068)
Provides persistent database registration, salted password verification, and session tokens.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_token, decode_token
from app.models.user import User
from app.schemas.user import UserSignUp, UserSignIn, UserResponse, UserListResponse

router = APIRouter()

# Default seed users for SIH evaluation
DEFAULT_SEED_USERS = [
    {
        "name": "Animesh Roy (Farmer)",
        "email": "citizen@weathergpt.gov.in",
        "password": "Password123!",
        "role": "citizen",
        "preferred_language": "bn",
    },
    {
        "name": "SDMA Ops Director",
        "email": "disaster_officer@weathergpt.gov.in",
        "password": "Password123!",
        "role": "disaster_officer",
        "preferred_language": "en",
    },
    {
        "name": "Debjit Das",
        "email": "debjit@weathergpt.gov.in",
        "password": "Password123!",
        "role": "citizen",
        "preferred_language": "en",
    },
]


async def ensure_seed_users(db: AsyncSession):
    """Ensures default SIH demo accounts exist in the database."""
    try:
        for seed in DEFAULT_SEED_USERS:
            stmt = select(User).where(func.lower(User.email) == seed["email"].lower())
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            if not existing:
                new_user = User(
                    name=seed["name"],
                    email=seed["email"].lower(),
                    hashed_password=hash_password(seed["password"]),
                    role=seed["role"],
                    preferred_language=seed["preferred_language"],
                )
                db.add(new_user)
        await db.commit()
    except Exception as e:
        await db.rollback()
        print(f"Warning seeding users: {e}")


@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user and store credentials securely in PostgreSQL",
)
async def sign_up(payload: UserSignUp, db: AsyncSession = Depends(get_db)):
    """Registers a new user with salted hashed password stored in the database."""
    clean_email = payload.email.strip().lower()

    # Check if email exists
    stmt = select(User).where(func.lower(User.email) == clean_email)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists. Please switch to Sign In.",
        )

    # Hash password with random salt
    hashed = hash_password(payload.password)

    user = User(
        name=payload.name.strip(),
        email=clean_email,
        hashed_password=hashed,
        role=payload.role or "citizen",
        preferred_language=payload.preferred_language or "en",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_token({"user_id": user.id, "email": user.email, "role": user.role})

    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role,
        preferred_language=user.preferred_language,
        created_at=user.created_at,
        token=token,
    )


@router.post(
    "/signin",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate user against database credentials",
)
async def sign_in(payload: UserSignIn, db: AsyncSession = Depends(get_db)):
    """Authenticates user against stored credentials in PostgreSQL."""
    # Pre-seed default users if table is empty
    await ensure_seed_users(db)

    clean_email = payload.email.strip().lower()

    # Query user by email
    stmt = select(User).where(func.lower(User.email) == clean_email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No account found with this email. Please check your email or click 'Create Account'.",
        )

    # Verify salted password hash
    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Password does not match. Please verify your password and try again.",
        )

    token = create_token({"user_id": user.id, "email": user.email, "role": user.role})

    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role,
        preferred_language=user.preferred_language,
        created_at=user.created_at,
        token=token,
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile from bearer token",
)
async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """Validates session token and returns active user record."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authentication token.",
        )
    token = authorization.split("Bearer ", 1)[1].strip()
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has expired or is invalid. Please sign in again.",
        )

    stmt = select(User).where(User.id == payload.get("user_id"))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User no longer exists in database.",
        )

    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role,
        preferred_language=user.preferred_language,
        created_at=user.created_at,
        token=token,
    )


@router.get(
    "/users",
    response_model=UserListResponse,
    summary="List all registered database accounts (passwords excluded)",
)
async def list_users(db: AsyncSession = Depends(get_db)):
    """Returns list of registered users in the database."""
    await ensure_seed_users(db)
    stmt = select(User).order_by(User.id.desc())
    result = await db.execute(stmt)
    users = result.scalars().all()
    return UserListResponse(
        total=len(users),
        users=[
            UserResponse(
                id=u.id,
                name=u.name,
                email=u.email,
                role=u.role,
                preferred_language=u.preferred_language,
                created_at=u.created_at,
            )
            for u in users
        ],
    )
