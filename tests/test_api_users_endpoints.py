import pytest
from app.models import User


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


@pytest.fixture
def auth_headers(user, session):
    """
    Generujemy tutaj nagłówki potrzebne do autoryzacji w API
    i pobieramy token dla użytkownika z fixturki user
    """
    token = user.get_token()
    # Zapisujemy wygenerowany token w bazie
    session.commit()
    return {
        'Authorization': f'Bearer {token}'
    }


def test_api_create_user(client, session):
    # Wysyłamy żądanie POST z danymi nowego użytkownika
    response = client.post('/api/users', json={
        'username': 'testowy_user',
        'email': 'testowy_user@example.com',
        'password': 'haslo123'
    })

    # Sprawdzamy czy dostaliśmy kod 201, sukces
    assert response.status_code == 201
    data = response.get_json()
    # Sprawdzamy czy nazwa się zgadza
    assert data['username'] == 'testowy_user'

    # Sprawdzamy w bazie danych czy hasło nie jest tekstowe
    u = session.get(User, data['id'])
    assert u is not None
    assert u.check_password('haslo123')


def test_api_get_user(client, user, auth_headers):
    # Wykonujemy zapytanie GET
    response = client.get(f'/api/users/{user.id}', headers=auth_headers)

    assert response.status_code == 200
    data = response.get_json()
    assert data['username'] == user.username


def test_api_update_user(client, session, user, auth_headers):
    # Wysyłamy żądanie PUT, aby zmienić pole 'about_me'
    response = client.put(f'/api/users/{user.id}', headers=auth_headers, json={
        'about_me': 'Nowy opis'
    })

    assert response.status_code == 200
    # Sprawdzamy, czy API zwróciło zaktualizowane dane w odpowiedzi
    assert response.get_json()['about_me'] == 'Nowy opis'

    # Weryfikujemy w bazie danych
    session.refresh(user)
    assert user.about_me == 'Nowy opis'


def test_api_followers_following(client, session, users_pair):
    """ Sprawdzamy endpointy get followers i get following """
    active_user, static_user = users_pair

    # Ustawiamy relację
    active_user.follow(static_user)
    session.commit()

    # Generujemy token i nagłówek dla active_user
    token = active_user.get_token()
    session.commit()
    headers = {'Authorization': f'Bearer {token}'}

    # Sprawdzamy kogo obserwuje active_user
    resp_following = client.get(f'/api/users/{active_user.id}/following', headers=headers)
    assert resp_following.status_code == 200
    assert resp_following.get_json()['items'][0]['username'] == static_user.username

    # Sprawdzamy kto obserwuje static_user
    resp_followers = client.get(f'/api/users/{static_user.id}/followers', headers=headers)
    assert resp_followers.status_code == 200
    assert resp_followers.get_json()['items'][0]['username'] == active_user.username