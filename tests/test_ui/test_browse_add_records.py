from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tests.conftest import save_screenshot


class TestBrowseAddRecords:
    def test_add_exercise(self, chrome_driver, chrome_login, live_server):
        chrome_driver.get(live_server.url("/browse"))
        WebDriverWait(chrome_driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".container"))
        )

        # --- Add exercise data ---
        add_btn = chrome_driver.find_element(By.CSS_SELECTOR, ".btn-add")
        add_btn.click()

        modal = WebDriverWait(chrome_driver, 10).until(
            EC.visibility_of_element_located((By.ID, "exerciseModal"))
        )

        # Fill in the exercise form in the modal
        modal.find_element(By.NAME, "type").send_keys("Cycling")
        date_input = modal.find_element(By.NAME, "date")

        chrome_driver.execute_script(
            "arguments[0].value = arguments[1];", date_input, "2024-05-15"
        )
        try:
            modal.find_element(By.NAME, "duration").clear()
            modal.find_element(By.NAME, "duration").send_keys("30")
            modal.find_element(By.NAME, "distance").clear()
            modal.find_element(By.NAME, "distance").send_keys("5")
            chrome_driver.execute_script(
                "arguments[0].dispatchEvent(new Event('change'));",
                modal.find_element(By.NAME, "duration"),
            )
            chrome_driver.execute_script(
                "arguments[0].dispatchEvent(new Event('change'));",
                modal.find_element(By.NAME, "distance"),
            )
        except Exception as e:
            print("Could not fill visible metric fields:", e)

        modal.find_element(By.NAME, "time").send_keys("12:00")
        modal.find_element(By.NAME, "timezone").send_keys("Australia/Perth")
        form = modal.find_element(By.TAG_NAME, "form")
        form.submit()

        # Wait for modal to close
        WebDriverWait(chrome_driver, 10).until(
            EC.invisibility_of_element_located((By.ID, "exerciseModal"))
        )

        # Reload the page to refresh the table
        chrome_driver.refresh()
        WebDriverWait(chrome_driver, 10).until(
            EC.presence_of_element_located((By.ID, "browseTableBody"))
        )

        # Print table HTML for debugging
        table_body = chrome_driver.find_element(By.ID, "browseTableBody")
        table_html = table_body.get_attribute("innerHTML")

        # Check for the new exercise
        assert "5" in table_html and "30" in table_html and "15/05/2024" in table_html

        # --- Switch to Chart view ---
        chart_label = chrome_driver.find_element(
            By.CSS_SELECTOR, "label[for='chartButton']"
        )
        chart_label.click()
        chart_card = WebDriverWait(chrome_driver, 10).until(
            EC.visibility_of_element_located((By.ID, "chartCard"))
        )

        assert "d-none" not in chart_card.get_attribute("class")
        save_screenshot(chrome_driver, "browse_chart.png")
