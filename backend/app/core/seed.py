from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from app.core.security import get_password_hash
from app.models.user import User


DEMO_USER_PASSWORD = "123456"

DEMO_USERS = [
    {
        "FullName": "Nguy\u1ec5n V\u0103n An",
        "Email": "nguyenvanan@gmail.com",
        "PhoneNumber": "0901234567",
        "ZaloID": "zalo_001",
        "Role": "farmer",
        "Region": "H\u00e0 N\u1ed9i",
        "PlaceholderHash": "$2b$12$hashpassword1",
    },
    {
        "FullName": "Tr\u1ea7n Th\u1ecb M\u1ef9",
        "Email": "tranthimy2205@gmail.com",
        "PhoneNumber": "0912345678",
        "ZaloID": "zalo_002",
        "Role": "farmer",
        "Region": "TP.HCM",
        "PlaceholderHash": "$2b$12$hashpassword2",
    },
    {
        "FullName": "L\u00ea V\u0103n B\u00ecnh",
        "Email": "levanbinhfarmer@gmail.com",
        "PhoneNumber": "0923456789",
        "ZaloID": "zalo_003",
        "Role": "farmer",
        "Region": "C\u1ea7n Th\u01a1",
        "PlaceholderHash": "$2b$12$hashpassword3",
    },
    {
        "FullName": "Ph\u1ea1m Th\u1ecb Lan",
        "Email": "phamthilan@gmail.com",
        "PhoneNumber": "0934567890",
        "ZaloID": "zalo_004",
        "Role": "farmer",
        "Region": "\u0110\u00e0 L\u1ea1t",
        "PlaceholderHash": "$2b$12$hashpassword4",
    },
    {
        "FullName": "Admin H\u1ec7 th\u1ed1ng",
        "Email": "admin@agriAI.vn",
        "PhoneNumber": "0800000001",
        "ZaloID": None,
        "Role": "admin",
        "Region": "H\u00e0 N\u1ed9i",
        "PlaceholderHash": "$2b$12$hashpassword0",
    },
]


def _should_replace_password_hash(current_hash: str | None, placeholder_hash: str) -> bool:
    if not current_hash:
        return True
    return current_hash in {"mock-password", placeholder_hash}


def seed_demo_users(session_factory) -> None:
    db = session_factory()
    try:
        for seed in DEMO_USERS:
            email = seed["Email"].strip().lower()
            user = db.query(User).filter(func.lower(User.Email) == email).first()
            if user is None:
                user = User(
                    FullName=seed["FullName"],
                    Email=email,
                    PhoneNumber=seed["PhoneNumber"],
                    ZaloID=seed["ZaloID"],
                    PasswordHash=get_password_hash(DEMO_USER_PASSWORD),
                    Role=seed["Role"],
                    Region=seed["Region"],
                    IsActive=True,
                    IsVerified=False,
                )
                db.add(user)
                continue

            user.FullName = seed["FullName"]
            user.PhoneNumber = seed["PhoneNumber"]
            user.ZaloID = seed["ZaloID"]
            user.Role = seed["Role"]
            user.Region = seed["Region"]
            user.IsActive = True
            if _should_replace_password_hash(user.PasswordHash, seed["PlaceholderHash"]):
                user.PasswordHash = get_password_hash(DEMO_USER_PASSWORD)
            db.add(user)

        db.commit()
    except SQLAlchemyError:
        db.rollback()
    finally:
        db.close()
