from utils import random_str
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tests_selenium.utils import cleanup_driver


def test_registration(driver, live_server):
    cleanup_driver(driver, live_server)

    # Wchodzimy na stronę logowania
    driver.get(live_server + "/auth/register")
    assert "Register" in driver.page_source

    # Przygotowujemy dane
    name = f"test_{random_str()}"
    email = f"{name}@example.com"
    password = "Haslo123"

    # Wypełniamy formularz
    driver.find_element(By.NAME, "username").send_keys(name)
    driver.find_element(By.NAME, "email").send_keys(email)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.NAME, "password2").send_keys(password)

    driver.find_element(By.CSS_SELECTOR, "form input[type='submit']").click()

    WebDriverWait(driver, 5).until(EC.url_contains("/auth/login"))

    assert "Congratulations" in driver.page_source