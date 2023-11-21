from sqlalchemy.orm import Session
import hashlib
from .model import User, UserCreate_Pydantic


def create_user(db: Session, user: UserCreate_Pydantic):
    db_user = User(username=user.username, email=user.email, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    sha256 = hashlib.sha256()
    sha256.update(password.encode("utf-8"))
    return sha256.hexdigest()


def verify_password(plain_password: str, password: str) -> bool:
    """Verify if the plain password matches the hashed password."""
    password = hash_password(password)
    return hash_password(plain_password) == password

