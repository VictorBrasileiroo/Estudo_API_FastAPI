from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_session
from ..models import User
from ..security import (
    get_current_user,
    get_password_hash,
)
from ..shemas import UserList, UserPublic, UserSchema

router = APIRouter(prefix='/users', tags=['users'])


app = FastAPI()

database = []


SessionDep = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session: SessionDep):
    user_db = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    if user_db:
        if user_db.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Username already exists',
            )
        if user_db.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT, detail='Email already exists'
            )

    user_db = User(
        username=user.username,
        password=get_password_hash(user.password),
        email=user.email,
    )

    session.add(user_db)
    session.commit()

    return user_db


@router.get('/', response_model=UserList)
def read_users(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
):
    # offset -> pular registros
    # limit -> num max de registros
    users = session.scalars(select(User).offset(skip).limit(limit)).all()
    return {'users': users}


@router.put('/{user_id}', response_model=UserPublic)
def update_user(
    user_id: int,
    user: UserSchema,
    session: SessionDep,
    current_user: CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )

    try:
        current_user.username = user.username
        current_user.password = get_password_hash(user.password)
        current_user.email = user.email
        session.commit()
        session.refresh(current_user)

        return current_user

    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username ou Email already exists',
        )


@router.delete('/{user_id}', response_model=UserPublic)
def delete_user(
    user_id: int,
    session: SessionDep,
    current_user: CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )

    session.delete(current_user)
    session.commit()

    user_info = UserPublic.model_validate(current_user)

    return user_info
