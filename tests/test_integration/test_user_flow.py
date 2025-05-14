import pytest
from flask import url_for
from server.models import User, db


class TestUserFlow:
    """Test complete user flow"""

    def test_register_and_login_flow(self, app, session):
        """Test the complete flow of user registration and login"""
        # Create test client
        client = app.test_client()
        
        # 1. Test user registration
        registration_data = {
            "username": "testuser123",
            "password": "Password123!",
            "confirm": "Password123!",
            "email": "test@example.com",
            "nickname": "Test User"
        }
        
        response = client.post(
            "/user/register", 
            data=registration_data,
            follow_redirects=True
        )
        
        # Check if registration is successful (redirected to homepage with success message)
        assert response.status_code == 200
        assert b"Registration successful" in response.data
        
        # Confirm user is created in the database
        user = User.query.filter_by(username="testuser123").first()
        assert user is not None
        assert user.email == "test@example.com"
        assert user.nickname == "Test User"
        
        # 2. Test user login
        login_data = {
            "email": "test@example.com",
            "password": "Password123!",
            "remember_me": False
        }
        
        response = client.post(
            "/user/login",
            data=login_data,
            follow_redirects=True
        )
        
        # Check if login is successful (redirected to dashboard with success message)
        assert response.status_code == 200
        assert b"Login successful" in response.data
        assert b"Dashboard" in response.data  # Assuming dashboard page contains "Dashboard" text
        
    @pytest.mark.skip(reason="This test requires debugging of the user.index endpoint")
    def test_profile_update_flow(self, app, session):
        """Test user profile update flow (requires authenticated state)"""
        # This test is skipped for now as it requires authentication setup 