import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class SystemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Chrome()
        cls.driver.implicitly_wait(5)
        cls.base_url = "http://127.0.0.1:5000"

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def test_register_and_login(self):
        driver = self.driver

        # Go to register page
        driver.get(f"{self.base_url}/register")

        # Fill registration form (adjust field names if needed)
        driver.find_element(By.NAME, "username").send_keys("seleniumuser")
        driver.find_element(By.NAME, "password").send_keys("testpassword")
        driver.find_element(By.NAME, "email").send_keys("selenium@example.com")
        driver.find_element(By.NAME, "nickname").send_keys("Selenium")
        # Optional fields: date_of_birth and sex (if present)
        try:
            driver.find_element(By.NAME, "date_of_birth").send_keys("2000-01-01")
        except:
            pass
        try:
            driver.find_element(By.NAME, "sex").send_keys("Other")
        except:
            pass
        driver.find_element(By.NAME, "submit").click()

        # Wait for redirect or success message
        WebDriverWait(driver, 5).until(
            lambda d: "index" in d.current_url or "login" in d.current_url
        )
        # After registration, you redirect to index, not login
        self.assertIn("index", driver.current_url)

        # Go to login page
        driver.get(f"{self.base_url}/login")
        driver.find_element(By.NAME, "email").send_keys("selenium@example.com")
        driver.find_element(By.NAME, "password").send_keys("testpassword")
        # If remember_me is a checkbox, you can click it (optional)
        try:
            driver.find_element(By.NAME, "remember_me").click()
        except:
            pass
        driver.find_element(By.NAME, "submit").click()

        # Wait for login to complete (should redirect to dashboard)
        WebDriverWait(driver, 5).until(
            lambda d: "dashboard" in d.current_url
        )
        self.assertIn("dashboard", driver.current_url)

if __name__ == "__main__":
    unittest.main()