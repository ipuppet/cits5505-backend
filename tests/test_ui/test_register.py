from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class TestUserRegister:
    def test_register(self, chrome_driver, live_server):
        chrome_driver.get(live_server.url("/user/register"))
        reg_form = WebDriverWait(chrome_driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "main form"))
        )
        reg_form.find_element(By.NAME, "username").send_keys("testregister")
        reg_form.find_element(By.NAME, "password").send_keys("testregister_pwd")
        reg_form.find_element(By.ID, "confirm_password").send_keys("testregister_pwd")
        reg_form.find_element(By.NAME, "email").send_keys("testregister@example.com")
        reg_form.find_element(By.NAME, "nickname").send_keys("Test Register")
        reg_form.submit()

        # Wait for the page to reload and check for error message
        WebDriverWait(chrome_driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "toast"))
        )
        assert f"Registration successful Test Register!" in chrome_driver.page_source

    def test_register_missing_fields(self, chrome_driver, live_server):
        chrome_driver.get(live_server.url("/user/register"))
        reg_form = WebDriverWait(chrome_driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "main form"))
        )
        # Leave username and password blank
        reg_form.find_element(By.NAME, "email").send_keys("missing@example.com")
        reg_form.find_element(By.NAME, "nickname").send_keys("nickname")
        reg_form.find_element(By.NAME, "password").send_keys("testregister_pwd")
        reg_form.find_element(By.ID, "confirm_password").send_keys("testregister_pwd")
        reg_form.submit()

        WebDriverWait(chrome_driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "toast"))
        )
        assert "{'username': ['This field is required.']}" in chrome_driver.page_source

    def test_register_same_email(self, chrome_driver, live_server, test_user):
        chrome_driver.get(live_server.url("/user/register"))
        reg_form = WebDriverWait(chrome_driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "main form"))
        )
        reg_form.find_element(By.NAME, "username").send_keys(test_user.username + "2")
        reg_form.find_element(By.NAME, "password").send_keys(test_user.plain_password)
        reg_form.find_element(By.ID, "confirm_password").send_keys(
            test_user.plain_password
        )
        reg_form.find_element(By.NAME, "email").send_keys(test_user.email)  # same email
        reg_form.submit()

        # Wait for the page to reload and check for error message
        WebDriverWait(chrome_driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "toast"))
        )
        assert (
            f"User with email '{test_user.email}' already exists."
            in chrome_driver.page_source
        )
