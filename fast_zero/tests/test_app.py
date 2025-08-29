# tests/test_db.py
from dataclasses import asdict
from http import HTTPStatus

from sqlalchemy import select

from fast_zero.models import User
from fast_zero.security import verify_password
from fast_zero.shemas import UserPublic


def test_create_user(session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(
            username='Alice',
            password='123123',
            email='test@test.com',
        )
        session.add(new_user)
        session.commit()

    user = session.scalar(select(User).where(User.username == 'Alice'))

    assert asdict(user) == {
        'id': 1,
        'username': 'Alice',
        'password': '123123',
        'email': 'test@test.com',
        'created_at': time,
        'updated_at': time,
    }


def test_list_users(client):
    response = client.get('/users/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_read_users_with_users(client, user):
    user_schema = UserPublic.model_validate(user).model_dump(mode='json')
    response = client.get('/users/')
    assert response.json() == {'users': [user_schema]}


def test_update_users(client, user, mock_db_time, session, token):
    with mock_db_time(model=User) as time:
        response = client.put(
            f'/users/{user.id}',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'username': 'bob',
                'email': 'bob@example.com',
                'password': 'mynewpassword',
            },
        )

    assert response.status_code == HTTPStatus.OK

    updated_user = session.scalar(select(User).where(User.id == user.id))

    assert updated_user.id == user.id
    assert updated_user.username == 'bob'
    assert updated_user.email == 'bob@example.com'
    assert updated_user.created_at == user.created_at
    assert updated_user.updated_at == time
    assert verify_password('mynewpassword', updated_user.password)


def test_update_integrity_error(client, user, token):
    client.post(
        '/users/',
        json={
            'username': 'fausto',
            'email': 'fausto@example.com',
            'password': 'secret',
        },
    )

    response_update = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'fausto',
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )

    assert response_update.status_code == HTTPStatus.CONFLICT
    assert response_update.json() == {
        'detail': 'Username ou Email already exists'
    }


def test_delete_user(client, user, session, token):
    response = client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    user_db = session.scalar(select(User).where(User.id == user.id))

    assert response.status_code == HTTPStatus.OK
    assert user_db is None


def test_get_token(client, user):
    response = client.post(
        '/token',
        data={'username': user.email, 'password': user.clean_password},
    )

    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert 'token_type' in token
