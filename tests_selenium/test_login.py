from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tests_selenium.utils import cleanup_driver, register_user


def test_login(driver, live_server):
    cleanup_driver(driver, live_server)

    # Tworzymy użytkownika
    username, password = register_user(driver, live_server)

    # Wchodzimy na stronę logowania
    driver.get(live_server + "/auth/login")
    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)

    # Klikamy przycisk zatwierdzania
    driver.find_element(By.CSS_SELECTOR, "form input[type='submit']").click()

    # Czekamy na pojawienie się logout, jest widoczny tylko dla zalogowanych
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Logout"))
    )

    # Sprawdzamy czy pojawiło się powitanie po zalogowaniu
    assert f"Hi, {username}" in driver.page_source