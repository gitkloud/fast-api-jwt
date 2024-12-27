from botocore.exceptions import ClientError
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from starlette.status import HTTP_401_UNAUTHORIZED
import jwt
import time
import uvicorn
import boto3
from app.appconfig import app_success_msg, user_create_msg

SECRET_KEY = "your_secret_key"

app = FastAPI()

class User(BaseModel):
    uid: str
    username: str
    fullName: str
    description: str | None = None

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_token(data: dict):
    to_encode = data.copy()
    expire = time.time() + 3000
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username != "admin" or form_data.password != "Password@1":
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_token({"sub": form_data.username})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/")
def read_secure_data(token: str = Depends(oauth2_scheme)):
    verify_token(token)
    return app_success_msg()

@app.post("/user/create")
def createuser(token: str = Depends(oauth2_scheme), form_data: OAuth2PasswordRequestForm = Depends()):
    verify_token(token)
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('gk_demo_table')
    item = User()
    item.uid = form_data.username
    item.username = form_data.username
    item.fullName = form_data.username
    item.description = form_data.password  # Assuming description is passed as password for simplicity
    try:
        response = table.put_item(
            Item={
                'id': item.uid,
                'name': item.username,
                'fullName': item.fullName,
                'description': item.description
            }
        )
        return user_create_msg()
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"Error creating item: {e}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="debug")
