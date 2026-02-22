"""
Authentication router.

Provides:
- User registration
- Login and JWT generation
- Token validation dependency

Uses OAuth2PasswordBearer with JWT-based authentication.
"""

from datetime import timedelta, datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from app.db import SessionDep
from app.models import User, UserCreate, UserPublic, Token
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

# Use this to hash the user's password
bcrypt_context = CryptContext(schemes=["bcrypt"])
# When a route needs authentication, look for a Bearer token in the request header
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token", auto_error=False)



@router.post("/", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def create_user(
    user: UserCreate,
    session: SessionDep
) -> User:
    """Register a new user account.

    Creates a user with a hashed password and stores it in the database.
    Usernames must be unique.

    Args:
        user (UserCreate): Incoming user data containing username and password.
        session (SessionDep): Database session injected by FastAPI.

    Returns:
        UserPublic: The created user without the password.

    Raises:
        HTTPException(409): If the username already exists.
    """
        
    existing = session.exec(select(User).where(User.username == user.username)).first()

    # Usernames must be unique, so if the username is being used, raise an exception
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


@router.post("/token", response_model=Token)
def login_for_access_token(
    user: UserCreate,
    session: SessionDep
):
    """Login as a user.

    Authenticates a user and returns a JWT access token.
    If the credentials are valid, a signed token containing user
    identity information is returned.

    Args:
        user (UserCreate): Incoming user data containing username and password.
        session (SessionDep): Database session injected by FastAPI.

    Returns:
        Token: JWT access token response.

    Raises:
        HTTPException(401): If the username or password is incorrect.
    """

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


def authenticate_user(
    username: str,
    password: str,
    session: SessionDep
) -> User:
    """Authenticates a user.

    The user to be logged in is grabbed from the db.
    The user's password is then verified.

    Args:
        username (str): The username being used to log in.
        password (str): The password being used to log in.
        session (SessionDep): Database session injected by FastAPI.

    Returns:
        User | bool: The authenticated user object, or False if authentication fails.

    Raises:
        None
    """

    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()

    if not user:
        return False

    if not bcrypt_context.verify(password, user.hashed_password):
        return False

    return user


def create_access_token(
    username: str,
    user_id: int,
    expires_delta: timedelta
) -> str:
    """Creates an access token.

    User information is stored in a dictionary, along with an expiration for the token.
    The token is created using the dictionary and SECRET_KEY.

    Args:
        username (str): The username of the logged in user
        user_id (int): The id of the logged in user.
        expires_delta (timedelta): How long the token should last.

    Returns:
        A JWT

    Raises:
        None
    """
    encode = {"sub": username, "id": user_id}
    expires = datetime.utcnow() + expires_delta
    encode.update({"exp": expires})
    
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


# FastAPI runs oauth2_bearer (a dependency) to extract the Bearer token
# from the Authorization header, then passes the token string into this function.
async def get_current_user(
    token: Annotated[str | None, Depends(oauth2_bearer)]
) -> dict:
    """Returns the user currently logged in.

    The token for the current user is decoded, and the user's info is stored, then returned.

    Args:
        token: The JWT for the user currently logged in.

    Returns:
        A dictionary containing the user's info

    Raises:
        HTTPException(401): if no one is logged in (there is no JWT).
        HTTPException(401): if the token did not contain the required user information.
        JWTError: if jwt.decode() fails
    """

    # If there is no token, then no one is signed in
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You must be logged in"
        )
    
    try:
        # jwt.decode() ensures that the token is valid
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")

        # Make sure the token payload contains "sub" (username) and "id".
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Username or id is not present"
            )
        
        return {"username": username, "id": user_id}
    
    # This runs if jwt.decode() fails -> occurs when the token
    # is expired OR its signature/payload has been modified (invalid)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


# UserDep is a dependency alias that tells FastAPI to run get_current_user()
# and inject the returned user dictionary into route parameters.
UserDep = Annotated[dict, Depends(get_current_user)]