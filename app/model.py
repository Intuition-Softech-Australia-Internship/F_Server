from pydantic_sqlalchemy import sqlalchemy_to_pydantic
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import text
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pydantic import BaseModel

# SQLAlchemy 모델 정의
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    email = Column(String, index=True)
    password = Column(String)

    def change_password(self, current_password: str, new_password: str):
        if verify_password(current_password, self.password):
            # 현재 비밀번호가 일치하면 새로운 비밀번호로 변경
            self.password = hash_password(new_password)
        else:
            raise HTTPException(status_code=400, detail="Current password is incorrect")

# Pydantic 모델 정의
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

# SQLAlchemy 세션 및 엔진 설정
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

UserCreate_Pydantic = sqlalchemy_to_pydantic(User, exclude=['id'])