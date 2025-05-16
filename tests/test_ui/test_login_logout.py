from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tests.conftest import save_screenshot


class TestUserLoginLogout:
    def test_login(self, chrome_driver, live_server, test_user):
        chrome_driver.get(live_server.url())
        WebDriverWait(chrome_driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "dropdown"))
        )

        dropdown = chrome_driver.find_element(By.ID, "login")
        dropdown.click()

        email = chrome_driver.find_element(By.NAME, "email")
        password = chrome_driver.find_element(By.NAME, "password")
        form = chrome_driver.find_element(By.TAG_NAME, "form")

        email.send_keys(test_user.email)
        password.send_keys(test_user.plain_password)
        form.submit()

        WebDriverWait(chrome_driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "toast"))
        )

        assert f"Hello, {test_user.nickname}!" in chrome_driver.page_source

        save_screenshot(chrome_driver, "login_success.png")

    def test_logout(self, chrome_driver, chrome_login, live_server, test_user):
        chrome_driver.get(live_server.url())
        WebDriverWait(chrome_driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[text()='Logout']"))
        )

        nav_button = chrome_driver.find_element(
            By.XPATH, f"//*[contains(text(), 'Hello, {test_user.nickname}!')]"
        )
        nav_button.click()
        logout_link = chrome_driver.find_element(By.XPATH, "//*[text()='Logout']")
        logout_link.click()

        WebDriverWait(chrome_driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "toast"))
        )

        assert "You have been logged out." in chrome_driver.page_source
