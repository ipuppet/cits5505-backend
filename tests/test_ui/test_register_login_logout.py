import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class SystemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Chrome()
        cls.driver.implicitly_wait(5)
        cls.base_url = "http://127.0.0.1:5000"

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def test_register_login_logout(self):
        driver = self.driver

        # --- Use unique username/email for each test run ---
        unique_id = str(int(time.time()))
        username = f"seleniumuser_{unique_id}"
        email = f"selenium_{unique_id}@example.com"
        password = "testpassword"

        # --- Register ---
        driver.get(f"{self.base_url}/user/register")
        try:
            reg_form = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "main form"))
            )

            reg_form.find_element(By.NAME, "username").send_keys(username)
            reg_form.find_element(By.NAME, "password").send_keys(password)
            reg_form.find_element(By.ID, "confirm_password").send_keys(password)
            reg_form.find_element(By.NAME, "email").send_keys(email)
            reg_form.find_element(By.NAME, "nickname").send_keys("Selenium")

            try:
                reg_form.find_element(By.NAME, "date_of_birth").send_keys("2000-01-01")
            except Exception:
                pass
            try:
                reg_form.find_element(By.NAME, "sex").send_keys("Other")
            except Exception:
                pass

            reg_form.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

            # Wait for redirect (not assuming "index" in URL)
            WebDriverWait(driver, 10).until(
                lambda d: d.current_url != f"{self.base_url}/user/register"
            )
            print("After registration, current URL:", driver.current_url)
            print("After registration, page source:\n", driver.page_source)

        except Exception as e:
            driver.save_screenshot("register_debug.png")
            print("Registration page source:\n", driver.page_source)
            raise e

        # --- Login ---
        driver.get(f"{self.base_url}/user/logout")
        WebDriverWait(driver, 10).until(
            lambda d: d.current_url.rstrip('/') == f"{self.base_url}"
            )
        print("After logout, current URL:", driver.current_url)
        
        
        login_btn = driver.find_element(By.ID, "login")
        login_btn.click()
        time.sleep(0.5)  # Wait for dropdown animation
        try:
            # Open the login dropdown
            
            # Find the main login form (not the navbar dropdown)
            login_form = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.dropdown-menu form"))
            )
            # Wait for CSRF token to be ready
            time.sleep(1)
            # Print CSRF token for debug
            csrf_token = login_form.find_element(By.NAME, "csrf_token").get_attribute("value")
            print("CSRF token used for login:", csrf_token)

            login_form.find_element(By.NAME, "email").send_keys(email)
            login_form.find_element(By.NAME, "password").send_keys(password)

            try:
                login_form.find_element(By.NAME, "remember_me").click()
            except Exception:
                pass

            login_form.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

            # Wait for redirect (not assuming dashboard in URL)
            WebDriverWait(driver, 10).until(
                lambda d: d.current_url != f"{self.base_url}/user/login"
            )
            print("After login, current URL:", driver.current_url)
            print("After login, page source:\n", driver.page_source)

        except Exception as e:
            driver.save_screenshot("login_debug.png")
            print("Login page source:\n", driver.page_source)
            raise e

        # --- Optionally, check for dashboard ---
        self.assertIn("/dashboard/", driver.current_url)

        # --- Logout ---
        driver.get(f"{self.base_url}/user/logout")
        WebDriverWait(driver, 10).until(
            lambda d: d.current_url.rstrip('/') == f"{self.base_url}"
        )
        self.assertEqual(driver.current_url.rstrip('/'), f"{self.base_url}")
        
if __name__ == "__main__":
    unittest.main()