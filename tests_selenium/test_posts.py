from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tests_selenium.utils import cleanup_driver, register_user, login_user


def test_create_post(driver, live_server):
    cleanup_driver(driver, live_server)

    # Rejestrujemy i logujemy nowego uzytkownika
    user, password = register_user(driver, live_server)
    login_user(driver, live_server, user, password)

    post_text = f"Testowy post w selenium 123"

    # Wpisujemy treść wiadomości na stronie głównej
    driver.find_element(By.NAME, "post").send_keys(post_text)

    # Klikamy submit w formularzu
    driver.find_element(By.NAME, "post").find_element(By.XPATH, "./ancestor::form//input[@type='submit']").click()

    # Weryfikujemy czy post pojawił się na stronie po odświeżeniu i czy pojawiło się powiadomienie o dodaniu posta
    WebDriverWait(driver, 5).until(EC.text_to_be_present_in_element((By.TAG_NAME, "body"), post_text))
    assert "Your post is now live!" in driver.page_source