from datetime import datetime, timedelta
from urllib.request import Request
from fastapi.middleware.cors import CORSMiddleware
from connexion.middleware.swagger_ui import SwaggerUIMiddleware
from fastapi import FastAPI, Depends, HTTPException, Form
from fastapi.openapi.utils import get_openapi
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app import crud, model, schemas
from app.crud import get_user, verify_password, create_user
from app.database import SessionLocal, engine, get_db
from app.model import UserCreate_Pydantic
from app.security import create_access_token, SECRET_KEY, ALGORITHM, oauth2_scheme, get_current_user
from typing import Any


app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class Login(BaseModel):
    email: str
    password: str

@app.post("/token")
async def login_for_access_token(login: Login, db: Session = Depends(get_db)):
    email = login.email
    password = login.password

    if not email or not password:
        raise HTTPException(status_code=422, detail="Email and password are required")

    user = get_user(db, email)
    if user is None or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # 토큰 만료 시간 설정
    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expires = datetime.utcnow() + expires_delta

    # 액세스 토큰 생성
    access_token = create_access_token(data={"sub": user.username, "exp": expires})

    return {"access_token": access_token, "token_type": "bearer"}


# @app.get("/users/me", response_model=schemas.User_Pydantic)
# async def read_users_me(current_user: schemas.User_Pydantic = Depends(get_current_user)):
#     return current_user


# User creation endpoint
@app.post("/users/", response_model=UserCreate_Pydantic)
def create_user_route(user: UserCreate_Pydantic, db: Session = Depends(get_db)):
    return create_user(db=db, user=user)


@app.post("/change-password/")
async def change_password(
        current_password: str = Form(..., title="Current password"),
        new_password: str = Form(..., title="New password"),
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    # 사용자 모델에서 비밀번호 변경 메서드 호출
    user.change_password(current_password, new_password)

    # 변경된 사용자 정보를 저장
    db.commit()
    db.refresh(user)

    return {"message": "Password changed successfully"}


# Custom OpenAPI URL
custom_openapi_url = "/custom_openapi.json"

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Your App Name",
        version="1.0.0",
        description="Your app description",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return openapi_schema


# OpenAPI 문서 엔드포인트
@app.get("/openapi.json")
async def get_openapi_endpoint():
    return custom_openapi()

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:4000",
    "http://localhost:19006"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SwaggerUIMiddleware)