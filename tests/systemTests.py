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

    def test_browse_add_exercise_and_visualize(self):
        driver = self.driver

        # --- Register and login ---
        unique_id = str(int(time.time()))
        username = f"browseuser_{unique_id}"
        email = f"browse_{unique_id}@example.com"
        password = "testpassword"

        # Register
        driver.get(f"{self.base_url}/user/register")
        reg_form = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "main form"))
        )
        reg_form.find_element(By.NAME, "username").send_keys(username)
        reg_form.find_element(By.NAME, "password").send_keys(password)
        reg_form.find_element(By.ID, "confirm_password").send_keys(password)
        reg_form.find_element(By.NAME, "email").send_keys(email)
        reg_form.find_element(By.NAME, "nickname").send_keys("BrowseTest")
        reg_form.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        WebDriverWait(driver, 10).until(
            lambda d: d.current_url != f"{self.base_url}/user/register"
        )

        # Logout and login via navbar dropdown
        driver.get(f"{self.base_url}/user/logout")
        WebDriverWait(driver, 10).until(
            lambda d: d.current_url.rstrip('/') == f"{self.base_url}"
        )
        login_btn = driver.find_element(By.ID, "login")
        login_btn.click()
        time.sleep(0.5)
        login_form = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "div.dropdown-menu form"))
        )
        login_form.find_element(By.NAME, "email").send_keys(email)
        login_form.find_element(By.NAME, "password").send_keys(password)
        login_form.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        WebDriverWait(driver, 10).until(
            lambda d: "/dashboard/" in d.current_url or d.current_url != f"{self.base_url}/user/login"
        )

        # --- Go to browse page ---
        driver.get(f"{self.base_url}/browse/")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".container"))
        )

        # --- Add exercise data ---
        add_btn = driver.find_element(By.CSS_SELECTOR, ".btn-add")
        add_btn.click()
        # Wait for modal to appear
        modal = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "exerciseModal"))
        )

        # Fill in the exercise form in the modal
        modal.find_element(By.NAME, "type").send_keys("Cycling")        
        date_input = modal.find_element(By.NAME, "date")
    
        driver.execute_script("arguments[0].value = arguments[1];", date_input, "2024-05-15")
        try:
            modal.find_element(By.NAME, "duration").clear()
            modal.find_element(By.NAME, "duration").send_keys("30")
            modal.find_element(By.NAME, "distance").clear()
            modal.find_element(By.NAME, "distance").send_keys("5")
            driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", modal.find_element(By.NAME, "duration"))
            driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", modal.find_element(By.NAME, "distance"))
            print("Filled visible metric fields.")
            # Print the value of the hidden metrics field before submit
            metrics_input = modal.find_element(By.ID, "exerciseForm.metrics")
            print("Metrics field value before submit:", metrics_input.get_attribute("value"))
        except Exception as e:
            print("Could not fill visible metric fields:", e)
        
        modal.find_element(By.NAME, "time").send_keys("12:00")
        modal.find_element(By.NAME, "timezone").send_keys("Australia/Perth")
        # Set metrics (use string values)
        # Set metrics (use numbers, not strings)
        print("Modal HTML after submit:\n", modal.get_attribute("outerHTML"))

        # Print form action, method, and CSRF token before submit
        form = modal.find_element(By.TAG_NAME, "form")
        print("Modal form action:", form.get_attribute("action"))
        print("Modal form method:", form.get_attribute("method"))
        csrf_input = modal.find_element(By.NAME, "csrf_token")
        print("CSRF token in modal before submit:", csrf_input.get_attribute("value"))
        # Submit the form
        modal.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
        time.sleep(1)  # Wait for possible error message

        # Try to print modal error messages if modal is still present
        try:
            error_divs = modal.find_elements(By.CLASS_NAME, "invalid-feedback")
            for div in error_divs:
                if div.is_displayed() and div.text.strip():
                    print("Modal error message:", div.text)
        except Exception as e:
            print("Could not check modal error messages (modal may be closed):", e)

        # Wait for modal to close
        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element_located((By.ID, "exerciseModal"))
        )

        # Reload the page to refresh the table
        driver.refresh()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "browseTableBody"))
        )

        # Print table HTML for debugging
        table_body = driver.find_element(By.ID, "browseTableBody")
        table_html = table_body.get_attribute("innerHTML")
        print("Table HTML after reload:", table_html)

        # Check for the new exercise
        found = "5" in table_html and "30" in table_html and "15/05/2024" in table_html
        self.assertTrue(found, "Exercise entry not found in table after reload.")

        # --- Switch to Chart view ---
        chart_label = driver.find_element(By.CSS_SELECTOR, "label[for='chartButton']")
        chart_label.click()
        # Wait for chart to be visible
        chart_card = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "chartCard"))
        )
        self.assertFalse("d-none" in chart_card.get_attribute("class"))
        print("Exercise added and chart displayed successfully on browse page.")
        
        
if __name__ == "__main__":
    unittest.main()