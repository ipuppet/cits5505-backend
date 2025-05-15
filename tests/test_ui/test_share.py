from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

from server.models import BodyMeasurement
from server.utils.constants import BodyMeasurementType
from tests.conftest import save_screenshot


class TestShare:
    def test_add_share(
        self,
        db_session,
        chrome_driver,
        chrome_login,
        live_server,
        test_user,
        test_receiver,
    ):
        bm = BodyMeasurement(
            user_id=test_user.id, type=BodyMeasurementType.WEIGHT, value=70.5
        )
        db_session.add(bm)
        db_session.commit()

        chrome_driver.get(live_server.url("/share"))
        WebDriverWait(chrome_driver, 10).until(
            EC.presence_of_element_located((By.ID, "friendShareForm"))
        )
        # Fill in the form
        friend_input = chrome_driver.find_element(By.ID, "searchFriend")
        friend_input.send_keys(test_receiver.username[0])
        WebDriverWait(chrome_driver, 10).until(
            lambda drv: len(
                drv.find_elements(By.CSS_SELECTOR, "#friendacSelect option")
            )
            > 0
        )
        select_element = chrome_driver.find_element(By.ID, "friendacSelect")
        select = Select(select_element)
        select.select_by_index(0)
        select_element = chrome_driver.find_element(By.ID, "chartType")
        select = Select(select_element)
        select.select_by_index(2)  # Select "Body Measurement"
        checkbox = WebDriverWait(chrome_driver, 10).until(
            EC.element_to_be_clickable((By.ID, "body_measurements_weight"))
        )
        chrome_driver.execute_script("arguments[0].checked = true;", checkbox)

        form = chrome_driver.find_element(By.ID, "friendShareForm")
        form.submit()

        WebDriverWait(chrome_driver, 10).until(
            EC.presence_of_element_located((By.ID, "friendShareForm"))
        )

        assert "You have successfully shared 1 records." in chrome_driver.page_source

        save_screenshot(chrome_driver, "add_share_success.png")
