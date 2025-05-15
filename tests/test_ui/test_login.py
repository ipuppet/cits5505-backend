from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class TestLiveServer:
    def test_login_page(self, chrome_driver, live_server, test_user):

        chrome_driver.get(live_server.url("/?login=true"))

        WebDriverWait(chrome_driver, 10).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )

        email = chrome_driver.find_element(By.NAME, "email")
        password = chrome_driver.find_element(By.NAME, "password")
        form = chrome_driver.find_element(By.TAG_NAME, "form")

        email.send_keys(test_user.email)
        password.send_keys("testpass")
        form.submit()

        WebDriverWait(chrome_driver, 60).until(EC.title_contains("Dashboard"))

        assert "Logout" in chrome_driver.page_source

        screenshot_dir = Path(__file__).parent / "screenshots"
        screenshot_dir.mkdir(exist_ok=True)
        chrome_driver.save_screenshot(str(screenshot_dir / "login_success.png"))
