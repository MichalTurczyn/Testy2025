import pytest
import sqlalchemy as sa
from datetime import datetime, timedelta
from app.models import User, Post, Message


@pytest.fixture
def user(session):
    """ Tworzymy użytkownika 'john' i zapisujemy go w bazie. """
    u = User(username='john', email='john@example.com')
    u.set_password('cat')
    session.add(u)
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


def test_create_post_model(session, user):
    """ Sprawdza logikę tworzenia posta i relacji z autorem """
    p = Post(body='Wpis 1234', author=user)
    session.add(p)
    session.commit()

    # sprawdzamy czy post nie ma pustej daty
    assert p.timestamp is not None
    assert user.posts_count() == 1

    # Pobieramy wszytskie posty użytkownika
    posts = session.scalars(sa.select(Post).filter_by(user_id=user.id)).all()
    assert p in posts


def test_message_relationships(session, users_pair):
    """ Weryfikujemy, czy wiadomości trafiają do właściwych skrzynek """
    u1, u2 = users_pair

    msg = Message(author=u1, recipient=u2, body="Prywatna wiadomość")
    session.add(msg)
    session.commit()

    # Pobieramy wszytskie otrzymane wiadomości dla u2
    msgs_received = session.scalars(sa.select(Message).filter_by(recipient_id=u2.id)).all()
    assert len(msgs_received) == 1
    assert msgs_received[0].body == "Prywatna wiadomość"


def test_unread_message_count(session, users_pair):
    """ Testujemy licznik nieprzeczytanych wiadomości """
    u1, u2 = users_pair

    session.add(Message(author=u1, recipient=u2, body="Wiad 1"))
    session.add(Message(author=u1, recipient=u2, body="Wiad 2"))
    session.commit()
    # wiadomości wyświetlają się jako nieprzeczytane, jeśli ich czas
    # jest większy niż czas ostatniego odczytu
    assert u2.unread_message_count() == 2

    # Sprawdzamy czy wiadomości przestaną wyśwuetlać się jako nieprzeczytane,
    # jeśli ich czas będzie mniejszy od czasu ostatniego odczytu
    # (sekunda po ich przyjściu)
    u2.last_message_read_time = datetime.utcnow() + timedelta(seconds=1)
    session.commit()

    assert u2.unread_message_count() == 0


def test_follow(session, users_pair):
    """ Sprawdzamy logikę obserwowania użytkownika """
    u1, u2 = users_pair
    u1.follow(u2)
    session.commit()

    assert u1.is_following(u2) is True
    assert u2.is_following(u1) is False


def test_unfollow(session, users_pair):
    """ Testujemy logikę anulowania obserwacji """
    u1, u2 = users_pair
    u1.follow(u2)
    session.commit()

    u1.unfollow(u2)
    session.commit()
    assert u1.is_following(u2) is False


def test_is_following(session, users_pair):
    """ Weryfikujemy metodę sprawdzającą status relacji """
    u1, u2 = users_pair
    assert u1.is_following(u2) is False

    # Ręcznie dodajemy u2 do listy obserwowanych u1
    u1.following.add(u2)
    session.commit()
    assert u1.is_following(u2) is True


def test_following_posts(session, users_pair):
    """ Testujemy logikę tablicy postów """
    u1, u2 = users_pair
    u3 = User(username='u3', email='u3@test.com')
    session.add(u3)

    now = datetime.utcnow()
    p1 = Post(body="Post u2", author=u2, timestamp=now + timedelta(seconds=1))
    p2 = Post(body="Post u1", author=u1, timestamp=now + timedelta(seconds=4))
    p3 = Post(body="Post u3", author=u3, timestamp=now + timedelta(seconds=2))
    session.add_all([p1, p2, p3])

    u1.follow(u2)
    session.commit()

    # Pobieramy własne posty i osób obserwowanych
    posts = session.scalars(u1.following_posts()).all()

    # sprawdzamy czy są 2 posty: nasz i obserwowanego użytkownika
    assert len(posts) == 2
    assert p2 in posts
    assert p1 in posts
    assert p3 not in posts
    # sprawdzamy czy post p2 wyświetli sie na samej górze, bo był dodany najpóźniej
    assert posts[0] == p2