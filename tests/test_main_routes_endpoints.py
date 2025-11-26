import pytest
import sqlalchemy as sa
from app.models import User, Message


@pytest.fixture
def user(session):
    """ Tworzymy użytkownika 'john' i zapisujemy go w bazie. """
    u = User(username='john', email='john@example.com')
    u.set_password('cat')
    session.add(u)
    # po commit uzytkownik dostanie ID i będzie widoczny
    session.commit()
    return u


@pytest.fixture
def users_pair(session):
    """ Tworzymy parę użytkowników """
    u1 = User(username='u1', email='u1@test.com')
    u2 = User(username='u2', email='u2@test.com')
    session.add_all([u1, u2])
    session.commit()
    return u1, u2


def login(client, username, password='cat'):
    """ Funkcja przyspieszająca logowanie użytkownika """
    return client.post('/auth/login', data={
        'username': username,
        'password': password
    }, follow_redirects=True)


def test_create_post(client, session, user):
    """ Testujemy publikowanie posta przez formularz """
    login(client, user.username, 'cat')

    # Przesyłamy post
    response = client.post('/index', data={'post': 'Pierwszy post'}, follow_redirects=True)

    # Sprawdzamy odpowiedź serwera w kodzie i treści html
    assert response.status_code == 200
    assert b'Your post is now live!' in response.data
    assert b'Pierwszy post' in response.data

    # Sprawdzamy liczbę postów w bazie
    session.expire(user)
    assert user.posts_count() == 1


def test_follow_route(client, session, users_pair):
    active_user, static_user = users_pair
    active_user.set_password('1')
    session.commit()

    login(client, active_user.username, '1')

    # active_user zaczyna obserwować static_user
    response = client.post(f'/follow/{static_user.username}', follow_redirects=True)

    assert response.status_code == 200
    assert f'You are following {static_user.username}'.encode('utf-8') in response.data

    # Sprawdzamy czy active_user obserwuje statycznego uzytkiwnika
    assert active_user.is_following(static_user)


def test_unfollow_route(client, session, users_pair):
    active_user, static_user = users_pair
    active_user.set_password('haslo')
    # obserwujemy
    active_user.follow(static_user)
    session.commit()

    login(client, active_user.username, 'haslo')
    # wysyłamy wiadomość o przestaniu obserwowania uzytkownika static_user
    response = client.post(f'/unfollow/{static_user.username}', follow_redirects=True)

    assert response.status_code == 200
    assert f'You are not following {static_user.username}'.encode('utf-8') in response.data
    # sprawdzamy czy uzytkownik nie jest już obserwowany
    assert not active_user.is_following(static_user)


def test_send_message_route(client, session, users_pair):
    """ Testujemy wysyłanie wiadomości prywatnej """
    sender, recipient = users_pair
    # ustawiamy hasło
    sender.set_password('jakies haslo')
    session.commit()

    # logujemy się
    login(client, sender.username, 'jakies haslo')

    # wysyłamy wiadomość do użytkownika recipient
    response = client.post(f'/send_message/{recipient.username}',
                           data={'message': 'Tajny kod'}, follow_redirects=True)

    # sprawdzamy powodzenie i czy w kodzie html zwróconym przez serwer jest dane powiadomienie
    assert response.status_code == 200
    assert b'Your message has been sent' in response.data

    # weryfikujemy zapis wiadomości w bazie
    msg = session.scalar(sa.select(Message))
    assert msg is not None
    assert msg.body == 'Tajny kod'
    assert msg.recipient_id == recipient.id