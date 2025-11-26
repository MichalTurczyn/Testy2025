import sys
import os
import threading
import time
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app

PORT = 5010


@pytest.fixture(scope="session")
def live_server():
    """
    Fixturka imituje uruchomienie aplikacji. Scope=session oznacza, że jest uruchamiana raz na całe działanie testów.
    """
    app = create_app()
    app.testing = True

    def run():
        # Uruchomienie serwera bez reloadera, aby nie blokował wątku
        app.run(port=PORT, use_reloader=False)

    # Uruchamiamy serwer jako wątek-demon
    t = threading.Thread(target=run, daemon=True)
    t.start()

    # Czekamy aż serwer się uruchomi zanim zaczniemy testy
    time.sleep(1)

    # Zwracamy adres URL, pod którym dostępna jest aplikacja
    yield f"http://127.0.0.1:{PORT}"


@pytest.fixture(scope="session")
def driver():
    """
    Ta fixturka odpala i kontroluje przeglądarkę. Driver jest klientem ,który wchodzi na strone klika w linki, wpisuje tekst itd.
    """
    options = webdriver.ChromeOptions()

    # Działa bez okna graficznego
    options.add_argument("--headless=new")

    options.add_argument("--window-size=1280,800")

    # Instalujemy sterownik do Chrome
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    yield driver

    # Zamykamy okno przeglądarki po testach
    driver.quit()