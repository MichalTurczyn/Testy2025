from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tests_selenium.utils import cleanup_driver, register_user, login_user


def test_following(driver, live_server):
    # Czyści stan przeglądarki (wylogowanie, usunięcie ciasteczek)
    cleanup_driver(driver, live_server)

    # Rejestrujemy dwóch niezależnych użytkowników: active_user i followed_user
    active_user, active_user_pass = register_user(driver, live_server)
    followed_user, _ = register_user(driver, live_server)

    # Logujemy się do systemu
    login_user(driver, live_server, active_user, active_user_pass)

    # Przechodzimy na strone profilowa
    driver.get(live_server + f"/user/{followed_user}")

    # Klikamy przycisk follow
    follow_btn = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@value='Follow']"))
    )
    follow_btn.click()

    # Czekamy aż przycisk zostanie usunięty po odswiezeniu strony
    WebDriverWait(driver, 5).until(EC.staleness_of(follow_btn))

    # Sprawdzamy czy wyświetlił się komunikat potwierdzający zaobserwowanie
    assert f"You are following {followed_user}" in driver.page_source

    # Sprawdzamy czy przycisk zmienił treść na unfollow
    assert len(driver.find_elements(By.XPATH, "//input[@value='Unfollow']")) > 0