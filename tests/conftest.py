import sys
import os
import pytest

# Dodajemy katalog główny projektu do ścieżki systemowej.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "test-secret"
    WTF_CSRF_ENABLED = False
    LANGUAGES = ['en', 'es']
    ELASTICSEARCH_URL = None
    REDIS_URL = "redis://"
    POSTS_PER_PAGE = 3


@pytest.fixture(scope="function")
def app():
    """ Przygotowujemy instancję aplikacji dla każdego testu """
    app = create_app(TestConfig)

    # Tworzymy i aktywujemy konteksty
    app_context = app.app_context()
    request_context = app.test_request_context("/")

    app_context.push()
    request_context.push()

    # Tworzymy tabele w bazie danych
    db.create_all()

    yield app

    # Sprzątamy po teście
    db.session.remove()
    db.drop_all()
    request_context.pop()
    app_context.pop()


@pytest.fixture(scope="function")
def session(app):
    """ Udostępnia sesję bazy danych dla testów """
    return db.session


@pytest.fixture(scope="function")
def client(app):
    """ To jest testowy do symulowania zapytań HTTP (GET, POST) """
    return app.test_client()