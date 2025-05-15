import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestRegisterErrors(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Chrome()
        cls.driver.implicitly_wait(5)
        cls.base_url = "http://127.0.0.1:5000"

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def test_register_errors(self):
        driver = self.driver

        # First, register a user with a unique email
        unique_id = str(int(time.time()))
        username = f"erroruser_{unique_id}"
        email = f"error_{unique_id}@example.com"
        password = "testpassword"

        driver.get(f"{self.base_url}/user/register")
        reg_form = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "main form"))
        )
        reg_form.find_element(By.NAME, "username").send_keys(username)
        reg_form.find_element(By.NAME, "password").send_keys(password)
        reg_form.find_element(By.ID, "confirm_password").send_keys(password)
        reg_form.find_element(By.NAME, "email").send_keys(email)
        reg_form.find_element(By.NAME, "nickname").send_keys("ErrorTest")
        reg_form.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        WebDriverWait(driver, 10).until(
            lambda d: d.current_url != f"{self.base_url}/user/register"
        )

        # Try to register again with the same email (should fail)
        driver.get(f"{self.base_url}/user/register")
        reg_form = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "main form"))
        )
        reg_form.find_element(By.NAME, "username").send_keys(username + "2")
        reg_form.find_element(By.NAME, "password").send_keys(password)
        reg_form.find_element(By.ID, "confirm_password").send_keys(password)
        reg_form.find_element(By.NAME, "email").send_keys(email)  # same email
        reg_form.find_element(By.NAME, "nickname").send_keys("ErrorTest2")
        reg_form.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Wait for the page to reload and check for error message
        WebDriverWait(driver, 10).until(
            lambda d: d.current_url == f"{self.base_url}/user/register"
        )
        page_source = driver.page_source
        print("Duplicate email registration page source:\n", page_source)
        self.assertTrue(
            "already registered" in page_source.lower() or "already exists" in page_source.lower(),
            "Expected error message for duplicate email not found."
        )

        # Try to register with missing required fields (should fail)
        driver.get(f"{self.base_url}/user/register")
        reg_form = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "main form"))
        )
        # Leave username and password blank
        reg_form.find_element(By.NAME, "email").send_keys(f"missing_{unique_id}@example.com")
        reg_form.find_element(By.NAME, "nickname").send_keys("MissingFields")
        reg_form.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        WebDriverWait(driver, 10).until(
            lambda d: d.current_url == f"{self.base_url}/user/register"
        )
        page_source = driver.page_source
        print("Missing fields registration page source:\n", page_source)
        self.assertTrue(
            "required" in page_source.lower() or "this field is required" in page_source.lower(),
            "Expected error message for missing fields not found."
        )

if __name__ == "__main__":
    unittest.main()