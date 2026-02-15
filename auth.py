from datetime import timedelta, datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from db import SessionDep
from models import User, UserCreate, UserPublic, Token
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlmodel import select


router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

SECRET_KEY = "vw07yui0LbRUWTzj5Qyx7gJ5K5ADVqz86ReYeZgoFUw"
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=["bcrypt"])
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")



@router.post("/", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def create_user(
    user: UserCreate,
    session: SessionDep
):
    existing = session.exec(select(User).where(User.username == user.username)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists"
        )
    
    create_user_model = User(
        username=user.username,
        hashed_password=bcrypt_context.hash(user.password),
    )

    session.add(create_user_model)
    session.commit()
    session.refresh(create_user_model)

    return create_user_model

# form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
@router.post("/token", response_model=Token)
async def login_for_access_token(user: UserCreate,
                                 session: SessionDep):
    log_user = authenticate_user(user.username, user.password, session)

    if not log_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    token = create_access_token(log_user.username, log_user.id, timedelta(minutes=20))

    return {
        "access_token": token,
        "token_type": "bearer"
    } 


def authenticate_user(username: str, password: str, session: SessionDep):
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()

    if not user:
        return False

    if not bcrypt_context.verify(password, user.hashed_password):
        return False

    return user


def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {"sub": username, "id": user_id}
    expires = datetime.utcnow() + expires_delta
    encode.update({"exp": expires})
    
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")

        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate user"
            )
        
        return {"username": username, "id": user_id}
    
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate user"
        )
    

UserDep = Annotated[dict, Depends(get_current_user)]