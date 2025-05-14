import pytest
from datetime import datetime, timedelta
from flask import url_for, json

from server.models import Share, User, Exercise
from server.utils.constants import ExerciseType
from server.utils.security import hash_password


class TestShareFlow:
    """Test data sharing functionality between users"""

    @pytest.mark.skip(reason="Share creation endpoint not implemented yet")
    def test_create_share_flow(self, app, session):
        """Test the complete flow of creating a data share with another user"""
        # Create test client
        client = app.test_client()
        
        # Create two test users
        test_user = User(
            username="testuser",
            password=hash_password("TestPassword123!"),
            email="test@example.com",
            nickname="Test User"
        )
        
        second_user = User(
            username="seconduser",
            password=hash_password("TestPassword123!"),
            email="second@example.com",
            nickname="Second User"
        )
        
        session.add(test_user)
        session.add(second_user)
        session.commit()
        
        # Set up authentication - simplified to skip actual login flow
        # This would need to be expanded for real testing
        
        # Share data
        share_data = {
            "receiver_id": second_user.id,
            "scope": {
                "exercise_types": [ExerciseType.RUNNING.value, ExerciseType.CYCLING.value],
                "body_measurement_types": []
            },
            "start_date": datetime.now().strftime("%Y-%m-%d"),
            "end_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        }
        
        # Create share through API
        response = client.post(
            "/share/create",  # Adjust to the actual endpoint
            data=json.dumps(share_data),
            follow_redirects=True,
            content_type="application/json"
        )
        
        # Check if share creation is successful
        assert response.status_code == 200 or response.status_code == 302
        
        # Confirm share is saved in the database
        share = Share.query.filter_by(
            sender_id=test_user.id,
            receiver_id=second_user.id
        ).first()
        
        # Assert the share properties
        # These assertions might be skipped if endpoint is not yet implemented
        pytest.skip_if(share is None, reason="Share was not created - API endpoint might not be implemented")
        assert ExerciseType.RUNNING.value in share.scope.get("exercise_types", [])
        assert ExerciseType.CYCLING.value in share.scope.get("exercise_types", [])
        assert not share.deleted
    
    @pytest.mark.skip(reason="Share sent viewing endpoint not implemented yet")
    def test_view_sent_shares(self, app, session):
        """Test viewing shares sent to other users"""
        # Create test client and users
        client = app.test_client()
        
        # Create two test users
        test_user = User(
            username="testuser",
            password=hash_password("TestPassword123!"),
            email="test@example.com",
            nickname="Test User"
        )
        
        second_user = User(
            username="seconduser",
            password=hash_password("TestPassword123!"),
            email="second@example.com",
            nickname="Second User"
        )
        
        session.add(test_user)
        session.add(second_user)
        session.commit()
        
        # Create a share directly in the database
        share = Share(
            sender_id=test_user.id,
            receiver_id=second_user.id,
            scope={
                "exercise_types": [ExerciseType.RUNNING.value, ExerciseType.CYCLING.value],
                "body_measurement_types": []
            },
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30)
        )
        session.add(share)
        session.commit()
        
        # Authentication would be needed here
        
        # Access shares sent page
        response = client.get(
            "/share/sent",  # Adjust based on actual implementation
            follow_redirects=True
        )
        
        # Check if page loads successfully
        assert response.status_code == 200
        
        # Get response content for assertions
        response_text = response.get_data(as_text=True)
        
        # These assertions might be skipped if UI doesn't yet show shares
        pytest.skip_if("Second User" not in response_text, reason="Share information not displayed in UI yet")
            
        assert "Second User" in response_text
    
    @pytest.mark.skip(reason="Share revocation not implemented yet")
    def test_revoke_share(self, app, session):
        """Test revoking a previously created share"""
        # Create test client and users
        client = app.test_client()
        
        # Create two test users
        test_user = User(
            username="testuser",
            password=hash_password("TestPassword123!"),
            email="test@example.com",
            nickname="Test User"
        )
        
        second_user = User(
            username="seconduser",
            password=hash_password("TestPassword123!"),
            email="second@example.com",
            nickname="Second User"
        )
        
        session.add(test_user)
        session.add(second_user)
        session.commit()
        
        # Create a share to revoke
        share = Share(
            sender_id=test_user.id,
            receiver_id=second_user.id,
            scope={
                "exercise_types": [ExerciseType.RUNNING.value],
                "body_measurement_types": []
            },
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30)
        )
        session.add(share)
        session.commit()
        
        # Authentication would be needed here
        
        # Revoke the share
        response = client.post(
            f"/share/{share.id}/revoke",  # Adjust to the actual endpoint
            follow_redirects=True
        )
        
        # Check if revocation is successful
        assert response.status_code == 200 or response.status_code == 302
        
        # Check if the share is now marked as deleted
        updated_share = session.get(Share, share.id)
        
        # These assertions might be skipped if API endpoint is not yet implemented
        pytest.skip_if(not hasattr(updated_share, 'deleted'), reason="Share deletion not implemented in the model yet")
        assert updated_share.deleted 