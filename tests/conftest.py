import time
from http.cookies import SimpleCookie
from pathlib import Path

import pytest
from flask import url_for
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from server.app import create_app
from server.models import db, User
from server.utils.security import hash_password


@pytest.fixture(scope="session")
def app():
    app = create_app(config_class="server.config.TestingConfig")
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def db_session(app):
    yield db.session
    db.session.rollback()
    db.session.remove()


@pytest.fixture(autouse=True)
def reset_db(app):
    yield
    with app.app_context():
        db.drop_all()
        db.create_all()


@pytest.fixture
def test_user(app, db_session):
    plain_password = "testpass"

    user = User(
        username="testuser",
        nickname="Tester",
        email="test@example.com",
        password=hash_password(plain_password),
    )
    db_session.add(user)
    db_session.commit()

    user.plain_password = plain_password

    yield user


@pytest.fixture
def test_receiver(app, db_session):
    plain_password = "testpass_receiver"

    receiver = User(
        username="testreceiver",
        nickname="Receiver",
        email="receiver@example.com",
        password=hash_password(plain_password),
    )
    db_session.add(receiver)
    db_session.commit()

    receiver.plain_password = plain_password

    yield receiver


@pytest.fixture(scope="session")
def chrome_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--timezone=Australia/Perth")

    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()


@pytest.fixture(autouse=True)
def reset_chrome_driver_state(chrome_driver):
    chrome_driver.delete_all_cookies()
    chrome_driver.get("about:blank")
    yield
    chrome_driver.delete_all_cookies()
    chrome_driver.get("about:blank")


@pytest.fixture
def chrome_login(app, chrome_driver, live_server, test_user):
    with app.test_client() as client:
        response = client.post(
            url_for("user.login"),
            data={"email": test_user.email, "password": test_user.plain_password},
            content_type="application/x-www-form-urlencoded",
        )
        cookie_str = response.headers.get("Set-Cookie")
        cookie = SimpleCookie()
        cookie.load(cookie_str)
        chrome_driver.get(live_server.url())
        chrome_driver.add_cookie(
            {
                "name": cookie["session"].key,
                "value": cookie["session"].value,
                "path": cookie["session"]["path"] or "/",
                "domain": cookie["session"]["domain"] or "localhost",
                "httpOnly": "HttpOnly" in cookie_str,
                "secure": "Secure" in cookie_str,
            }
        )


def save_screenshot(
    driver: webdriver.Chrome, filename: str, subdir: str = "test_ui/screenshots"
) -> str:
    screenshot_dir = Path(__file__).parent / subdir
    screenshot_dir.mkdir(exist_ok=True)

    screenshot_path = str(screenshot_dir / filename)
    time.sleep(2)
    driver.save_screenshot(screenshot_path)
    return screenshot_path
