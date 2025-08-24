from dataclasses import asdict

from sqlalchemy import select

from fast_zero.models import User


def test_create_user(session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(
            username='Alice', password='123123', email='test@test.com'
        )
        session.add(new_user)
        session.commit()  # saveasync do aspnet

    # Scala -> querys
    user = session.scalar(select(User).where(User.username == 'Alice'))

    assert asdict(user) == {
        'id': 1,
        'username': 'Alice',
        'password': '123123',
        'email': 'test@test.com',
        'created_at': time,
    }

    # Isso faz com que durante o commit, quando os objetos são persistido
    # s da sessão para o banco de dados, o evento de before_insert seja
    #  executado para cada objeto do modelo passado em mock_db_time
    # (model=*MODEL*).
