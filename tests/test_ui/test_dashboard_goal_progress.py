import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestDashboardGoalProgress(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Chrome()
        cls.driver.implicitly_wait(5)
        cls.base_url = "http://127.0.0.1:5000"

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def test_dashboard_goal_progress(self):
        driver = self.driver

        # --- Register and login ---
        unique_id = str(int(time.time()))
        username = f"goaluser_{unique_id}"
        email = f"goal_{unique_id}@example.com"
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
        reg_form.find_element(By.NAME, "nickname").send_keys("GoalTest")
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

        # --- Go to dashboard ---
        driver.get(f"{self.base_url}/dashboard/")
        # Wait for the "My Goals" card to appear by looking for the "Add Goal" button
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".card-header .btn-add[data-bs-target='#addGoalModal']"))
        )

        # --- Add a goal ---
        add_goal_btn = driver.find_element(By.CSS_SELECTOR, ".card-header .btn-add[data-bs-target='#addGoalModal']")
        add_goal_btn.click()
        goal_modal = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "addGoalModal"))
        )
        goal_modal.find_element(By.NAME, "description").send_keys("Run 5km")
        goal_modal.find_element(By.NAME, "exercise_type").send_keys("Running")
        goal_modal.find_element(By.NAME, "metric").send_keys("distance")
        goal_modal.find_element(By.NAME, "target_value").send_keys("5")
        # The unit field is readonly and auto-filled
        goal_modal.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element_located((By.ID, "addGoalModal"))
        )

        # --- Add an exercise (Running 3km) ---
        driver.get(f"{self.base_url}/browse/")
        add_btn = driver.find_element(By.CSS_SELECTOR, ".btn-add")
        add_btn.click()
        modal = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "exerciseModal"))
        )
        modal.find_element(By.NAME, "type").send_keys("Running")
        date_input = modal.find_element(By.NAME, "date")
        driver.execute_script("arguments[0].value = arguments[1];", date_input, "2024-05-15")
        modal.find_element(By.NAME, "duration").clear()
        modal.find_element(By.NAME, "duration").send_keys("20")
        modal.find_element(By.NAME, "distance").clear()
        modal.find_element(By.NAME, "distance").send_keys("3")
        modal.find_element(By.NAME, "time").send_keys("12:00")
        modal.find_element(By.NAME, "timezone").send_keys("Australia/Perth")
        modal.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element_located((By.ID, "exerciseModal"))
        )

        # --- Add another exercise (Running 2km) ---
        add_btn = driver.find_element(By.CSS_SELECTOR, ".btn-add")
        add_btn.click()
        modal = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "exerciseModal"))
        )
        modal.find_element(By.NAME, "type").send_keys("Running")
        date_input = modal.find_element(By.NAME, "date")
        driver.execute_script("arguments[0].value = arguments[1];", date_input, "2024-05-16")
        modal.find_element(By.NAME, "duration").clear()
        modal.find_element(By.NAME, "duration").send_keys("15")
        modal.find_element(By.NAME, "distance").clear()
        modal.find_element(By.NAME, "distance").send_keys("2")
        modal.find_element(By.NAME, "time").send_keys("13:00")
        modal.find_element(By.NAME, "timezone").send_keys("Australia/Perth")
        modal.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element_located((By.ID, "exerciseModal"))
        )

        # --- Go back to dashboard and check goal progress ---
        driver.get(f"{self.base_url}/dashboard/")
        # Wait for at least one goal item to appear
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".goal-item"))
        )
        dashboard_html = driver.page_source
        print("Dashboard HTML after adding exercises:", dashboard_html)

        # Check that the goal is present and marked as completed
        self.assertIn("Run 5km", dashboard_html)
        self.assertTrue("Completed" in dashboard_html or "completed" in dashboard_html)

if __name__ == "__main__":
    unittest.main()