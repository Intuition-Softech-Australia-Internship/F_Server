from pydantic import BaseModel

class UserCreate_Pydantic(BaseModel):
    username: str
    email: str
    password: str

class User_Pydantic(BaseModel):
    username: str
    email: str

class Token(BaseModel):
    access_token: str
    token_type: str