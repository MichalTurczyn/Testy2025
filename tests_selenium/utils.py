import random
import string
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def random_str(length=6):
    """ Generujemy losowy ciąg żeby uniknąć konfilktów z nazwami użytkowników """
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def cleanup_driver(driver, live_server):
    """ Czyścimy sesję przed testem """
    driver.get(live_server + "/auth/logout")
    driver.delete_all_cookies()


def register_user(driver, live_server):
    username = f"user_{random_str()}"
    email = f"{username}@test.com"
    password = "Password123!"

    driver.get(live_server + "/auth/register")

    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "email").send_keys(email)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.NAME, "password2").send_keys(password)

    # Klikamy submit
    driver.find_element(By.CSS_SELECTOR, "form input[type='submit']").click()

    # Czekamy na przekierowanie na login
    WebDriverWait(driver, 5).until(EC.url_contains("/auth/login"))

    return username, password


def login_user(driver, live_server, username, password):
    driver.get(live_server + "/auth/login")

    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "form input[type='submit']").click()

    # Czekamy na załadowanie strony głównej (szukamy pola do wpisania posta)
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, "post")))