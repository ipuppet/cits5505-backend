import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from server.app import create_app
from server.models import db
from server.utils.security import hash_password


@pytest.fixture(scope="session")
def app():
    app = create_app(config_class="server.config.TestingConfig")
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture(scope="function")
def db_session(app):
    with app.app_context():
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()
    yield db.session
    db.session.rollback()
    db.session.remove()


@pytest.fixture(scope="function")
def test_user(app, db_session):
    from server.models import User

    user = User(
        username="testuser",
        nickname="Tester",
        email="test@example.com",
        password=hash_password("testpass"),
    )
    db_session.add(user)
    db_session.commit()

    yield user

    db_session.delete(user)
    db_session.commit()


@pytest.fixture(scope="session")
def chrome_driver():
    options = Options()
    # options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()
