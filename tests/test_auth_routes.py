import pytest
import sqlalchemy as sa
from app.models import User


@pytest.fixture
def user(session):
    """ Tworzymy użytkownika 'john' i zapisujemy go w bazie """
    u = User(username='john', email='john@example.com')
    u.set_password('cat')
    session.add(u)
    # po commit uzytkownik dostanie ID i będzie widoczny
    session.commit()
    return u


def test_register_user_success(client, session):
    response = client.post('/auth/register', data={
        'username': 'nowy', 'email': 'john@example.com',
        'password': '123', 'password2': '123'
    }, follow_redirects=True)

    assert response.status_code == 200
    # Szukamy w odpowiedzi html jaką zwrócił serwer fragmentu o danej treści
    assert b'Congratulations' in response.data
    assert session.scalar(sa.select(User).filter_by(username='nowy')) is not None


def test_login_success(client, user):
    response = client.post('/auth/login', data={
        'username': 'john', 'password': 'cat'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Logout' in response.data


def test_login_invalid_password(client, user):
    response = client.post('/auth/login', data={
        'username': 'john', 'password': 'zle_haslo'
    }, follow_redirects=True)

    assert b'Invalid username or password' in response.data


def test_logout(client, user):
    client.post('/auth/login', data={'username': 'john', 'password': 'cat'})
    response = client.get('/auth/logout', follow_redirects=True)

    assert b'Sign In' in response.data