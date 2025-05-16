import time
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tests.conftest import save_screenshot


class TestDashboardGoalProgress:
    def test_dashboard_goal_progress(self, chrome_driver, chrome_login, live_server):
        chrome_driver.get(live_server.url("/dashboard"))
        WebDriverWait(chrome_driver, 10).until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    ".card-header .btn-add[data-bs-target='#addGoalModal']",
                )
            )
        )

        # --- Add a goal ---
        add_goal_btn = chrome_driver.find_element(
            By.CSS_SELECTOR, ".card-header .btn-add[data-bs-target='#addGoalModal']"
        )
        add_goal_btn.click()
        goal_modal = WebDriverWait(chrome_driver, 10).until(
            EC.visibility_of_element_located((By.ID, "addGoalModal"))
        )
        goal_modal.find_element(By.NAME, "description").send_keys("Run 5km")
        goal_modal.find_element(By.NAME, "exercise_type").send_keys("Running")
        goal_modal.find_element(By.NAME, "metric").send_keys("distance")
        goal_modal.find_element(By.NAME, "target_value").send_keys("5")
        # The unit field is readonly and auto-filled
        goal_modal.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        WebDriverWait(chrome_driver, 10).until(
            EC.invisibility_of_element_located((By.ID, "addGoalModal"))
        )

        # --- Add an exercise (Running 3km) ---
        chrome_driver.get(live_server.url("/browse"))
        add_btn = chrome_driver.find_element(By.CSS_SELECTOR, ".btn-add")
        add_btn.click()
        modal = WebDriverWait(chrome_driver, 10).until(
            EC.visibility_of_element_located((By.ID, "exerciseModal"))
        )
        modal.find_element(By.NAME, "type").send_keys("Running")
        date_input = modal.find_element(By.NAME, "date")
        chrome_driver.execute_script(
            "arguments[0].value = arguments[1];", date_input, "2024-05-15"
        )
        modal.find_element(By.NAME, "duration").clear()
        modal.find_element(By.NAME, "duration").send_keys("20")
        modal.find_element(By.NAME, "distance").clear()
        modal.find_element(By.NAME, "distance").send_keys("3")
        modal.find_element(By.NAME, "time").send_keys("12:00")
        modal.find_element(By.NAME, "timezone").send_keys("Australia/Perth")
        modal.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
        WebDriverWait(chrome_driver, 10).until(
            EC.invisibility_of_element_located((By.ID, "exerciseModal"))
        )

        # --- Add another exercise (Running 2km) ---
        add_btn = chrome_driver.find_element(By.CSS_SELECTOR, ".btn-add")
        add_btn.click()
        modal = WebDriverWait(chrome_driver, 10).until(
            EC.visibility_of_element_located((By.ID, "exerciseModal"))
        )
        modal.find_element(By.NAME, "type").send_keys("Running")
        date_input = modal.find_element(By.NAME, "date")
        chrome_driver.execute_script(
            "arguments[0].value = arguments[1];", date_input, "2024-05-16"
        )
        modal.find_element(By.NAME, "duration").clear()
        modal.find_element(By.NAME, "duration").send_keys("15")
        modal.find_element(By.NAME, "distance").clear()
        modal.find_element(By.NAME, "distance").send_keys("2")
        modal.find_element(By.NAME, "time").send_keys("13:00")
        modal.find_element(By.NAME, "timezone").send_keys("Australia/Perth")
        modal.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
        WebDriverWait(chrome_driver, 10).until(
            EC.invisibility_of_element_located((By.ID, "exerciseModal"))
        )

        # --- Go back to dashboard and check goal progress ---
        chrome_driver.get(live_server.url("/dashboard"))
        WebDriverWait(chrome_driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".goal-item"))
        )
        dashboard_html = chrome_driver.page_source

        # Check that the goal is present and marked as completed
        assert "Run 5km" in dashboard_html
        assert "Completed" in dashboard_html or "completed" in dashboard_html
        save_screenshot(chrome_driver, "goal_completed.png")
