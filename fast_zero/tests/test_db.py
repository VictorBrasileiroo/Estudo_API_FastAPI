from dataclasses import asdict

from sqlalchemy import select

from fast_zero.models import User


async def test_create_user(session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(
            username='Alice',
            password='123123',
            email='test@test.com',
        )
        session.add(new_user)
        await session.commit()

    user = await session.scalar(select(User).where(User.username == 'Alice'))

    assert asdict(user) == {
        'id': 1,
        'username': 'Alice',
        'password': '123123',
        'email': 'test@test.com',
        'created_at': time,
        'updated_at': time,
    }
