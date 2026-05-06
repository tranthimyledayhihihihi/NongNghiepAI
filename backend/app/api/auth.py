from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token, decode_access_token, get_password_hash, verify_password
from app.models.user import User
from app.schemas.auth_schema import AuthResponse, LoginRequest, RegisterRequest, UserRead

router = APIRouter(prefix="/api/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
oauth2_optional_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def _to_user_read(user: User) -> UserRead:
    return UserRead(
        user_id=user.UserID,
        full_name=user.FullName,
        email=user.Email,
        phone_number=user.PhoneNumber,
        zalo_id=user.ZaloID,
        role=user.Role,
        region=user.Region,
        is_active=user.IsActive,
        created_at=user.CreatedAt,
    )


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        parsed_user_id = int(user_id)
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    user = db.query(User).filter(User.UserID == parsed_user_id).first()
    if user is None or not user.IsActive:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="user not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_optional_current_user(
    token: str | None = Depends(oauth2_optional_scheme),
    db: Session = Depends(get_db),
) -> User | None:
    if not token:
        return None

    payload = decode_access_token(token)
    if not payload:
        return None

    try:
        user_id = int(payload.get("sub"))
    except (TypeError, ValueError):
        return None

    user = db.query(User).filter(User.UserID == user_id).first()
    if user is None or not user.IsActive:
        return None
    return user


def _is_placeholder_user(user: User) -> bool:
    return user.FullName == "API User" and user.PasswordHash == "mock-password"


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    email = request.email.strip().lower()
    existing_user = db.query(User).filter(func.lower(User.Email) == email).first()
    if existing_user is not None:
        if _is_placeholder_user(existing_user):
            existing_user.FullName = request.full_name.strip()
            existing_user.PhoneNumber = request.phone_number
            existing_user.ZaloID = request.zalo_id
            existing_user.PasswordHash = get_password_hash(request.password)
            existing_user.Role = existing_user.Role or "farmer"
            existing_user.Region = request.region
            existing_user.IsActive = True
            existing_user.IsVerified = False
            db.add(existing_user)
            db.commit()
            db.refresh(existing_user)
            return AuthResponse(
                access_token=create_access_token(existing_user.UserID),
                user=_to_user_read(existing_user),
            )
        raise HTTPException(status_code=409, detail="email already registered")

    user = User(
        FullName=request.full_name.strip(),
        Email=email,
        PhoneNumber=request.phone_number,
        ZaloID=request.zalo_id,
        PasswordHash=get_password_hash(request.password),
        Role="farmer",
        Region=request.region,
        IsActive=True,
        IsVerified=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return AuthResponse(access_token=create_access_token(user.UserID), user=_to_user_read(user))


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    email = request.email.strip().lower()
    user = db.query(User).filter(func.lower(User.Email) == email).first()
    if user is None or not verify_password(request.password, user.PasswordHash):
        raise HTTPException(status_code=401, detail="incorrect email or password")
    if not user.IsActive:
        raise HTTPException(status_code=403, detail="user is inactive")

    return AuthResponse(access_token=create_access_token(user.UserID), user=_to_user_read(user))


@router.get("/me", response_model=UserRead)
async def read_me(current_user: User = Depends(get_current_user)):
    return _to_user_read(current_user)
