import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestSharePageUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Chrome()
        cls.driver.implicitly_wait(5)
        cls.base_url = "http://127.0.0.1:5000"

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def test_share_page_ui(self):
        driver = self.driver

        # --- Register and login ---
        unique_id = str(int(time.time()))
        username = f"shareuser_{unique_id}"
        email = f"share_{unique_id}@example.com"
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
        reg_form.find_element(By.NAME, "nickname").send_keys("ShareTest")
        reg_form.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        WebDriverWait(driver, 10).until(
            lambda d: d.current_url != f"{self.base_url}/user/register"
        )

        # Login
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

        # --- Go to Share page ---
        driver.get(f"{self.base_url}/share/")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "friendShareForm"))
        )

        # Check Share with Friends form
        self.assertTrue(driver.find_element(By.ID, "friendShareForm").is_displayed())
        self.assertTrue(driver.find_element(By.ID, "searchFriend").is_displayed())
        self.assertTrue(driver.find_element(By.ID, "friendacSelect").is_displayed())
        self.assertTrue(driver.find_element(By.ID, "chartType").is_displayed())

        # Check Share Records section
        self.assertIn("Share Records", driver.page_source)
        self.assertIn("Sent Shares", driver.page_source)
        self.assertIn("Received Shares", driver.page_source)

        # Open Sent Shares modal
        sent_btn = driver.find_element(By.CSS_SELECTOR, "button[data-bs-target='#sharesSentModal']")
        sent_btn.click()
        WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.ID, "sharesSentModal"))
        )
        self.assertTrue(driver.find_element(By.ID, "sharesSentModal").is_displayed())

        # Close Sent Shares modal
        driver.find_element(By.CSS_SELECTOR, "#sharesSentModal .btn-close").click()
        WebDriverWait(driver, 5).until(
            EC.invisibility_of_element_located((By.ID, "sharesSentModal"))
        )

        # Open Received Shares modal
        recv_btn = driver.find_element(By.CSS_SELECTOR, "button[data-bs-target='#sharesReceivedModal']")
        recv_btn.click()
        WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.ID, "sharesReceivedModal"))
        )
        self.assertTrue(driver.find_element(By.ID, "sharesReceivedModal").is_displayed())

        # Close Received Shares modal
        driver.find_element(By.CSS_SELECTOR, "#sharesReceivedModal .btn-close").click()
        WebDriverWait(driver, 5).until(
            EC.invisibility_of_element_located((By.ID, "sharesReceivedModal"))
        )

        print("Share page UI elements and modals tested successfully.")

if __name__ == "__main__":
    unittest.main()