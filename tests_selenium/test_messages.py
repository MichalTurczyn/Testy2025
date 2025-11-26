from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tests_selenium.utils import cleanup_driver, register_user, login_user


def test_send_message(driver, live_server):
    cleanup_driver(driver, live_server)

    # Rejestrujemy użytkownika wysyłającego wiadomość i odbierającego
    sender, sender_pass = register_user(driver, live_server)
    recipient, _ = register_user(driver, live_server)

    # Logowanie do systemu jako sender
    login_user(driver, live_server, sender, sender_pass)

    # Przechodzimy na profil odbiorcy
    driver.get(live_server + f"/user/{recipient}")

    # Klikamy w link otwierający formularz wiadomości
    driver.find_element(By.PARTIAL_LINK_TEXT, "Send private message").click()

    # Czekamy na załadowanie formularza, wypełniamy i wysyłamy
    msg = "Jakas wiadomosc"
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.NAME, "message"))
    )
    driver.find_element(By.NAME, "message").send_keys(msg)
    driver.find_element(By.CSS_SELECTOR, "form input[type='submit']").click()

    # Czekamy na załadowanie strony po wysłaniu
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    # Sprawdzamy czy pokazał się komunikat potwierdzający wysłanie wiadomości
    assert "Your message has been sent" in driver.page_source