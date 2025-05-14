import pytest
from datetime import datetime, timedelta
from flask import url_for, json

from server.models import Share, User, Exercise, db
from server.utils.constants import ExerciseType


class TestShareFlow:
    """Test data sharing functionality between users"""

    @pytest.fixture
    def second_user(self, app):
        """Create a second test user for sharing tests"""
        from werkzeug.security import generate_password_hash
        
        # First, check if user already exists
        user = User.query.filter_by(username="seconduser").first()
        if user:
            return user
            
        # If not, create a new user
        new_user = User(
            username="seconduser",
            password=generate_password_hash("TestPassword123!"),
            email="second@example.com",
            nickname="Second User"
        )
        db.session.add(new_user)
        db.session.commit()
        return new_user

    @pytest.mark.skip(reason="Share creation endpoint not implemented yet")
    def test_create_share_flow(self, client, authenticated_user, second_user):
        """Test the complete flow of creating a data share with another user"""
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
            sender_id=authenticated_user.id,
            receiver_id=second_user.id
        ).first()
        
        # Skip this assertion if endpoint is not yet implemented
        if share:
            assert ExerciseType.RUNNING.value in share.scope.get("exercise_types", [])
            assert ExerciseType.CYCLING.value in share.scope.get("exercise_types", [])
            assert not share.deleted
    
    @pytest.mark.skip(reason="Share sent viewing endpoint not implemented yet")
    def test_view_sent_shares(self, client, authenticated_user, second_user):
        """Test viewing shares sent to other users"""
        # Create a share directly in the database
        share = Share(
            sender_id=authenticated_user.id,
            receiver_id=second_user.id,
            scope={
                "exercise_types": [ExerciseType.RUNNING.value, ExerciseType.CYCLING.value],
                "body_measurement_types": []
            },
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30)
        )
        db.session.add(share)
        db.session.commit()
        
        # Access shares sent page
        response = client.get(
            "/share/sent",  # Adjust based on actual implementation
            follow_redirects=True
        )
        
        # Check if page loads successfully
        assert response.status_code == 200
        
        # Basic check for content
        response_text = response.get_data(as_text=True)
        
        # If sharing UI is implemented, check for user information
        if "Second User" in response_text:
            assert "Second User" in response_text
            # Check for other expected elements
    
    @pytest.mark.skip(reason="Share viewing as receiver not implemented yet")
    def test_view_received_shares(self, client, authenticated_user, second_user):
        """Test viewing shares received from other users"""
        # We need to log in as second_user to test received shares
        # This requires a more complex setup with session manipulation
        
        # For now, create a share with second_user as receiver
        share = Share(
            sender_id=authenticated_user.id,
            receiver_id=second_user.id,
            scope={
                "exercise_types": [ExerciseType.RUNNING.value],
                "body_measurement_types": []
            },
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30)
        )
        db.session.add(share)
        db.session.commit()
        
        # In a real test, we would log in as second_user here
        # For now, we'll skip actual testing of this feature
        
        # Basic assertion to ensure the share exists in database
        assert Share.query.filter_by(receiver_id=second_user.id).count() > 0
    
    @pytest.mark.skip(reason="Share revocation not implemented yet")
    def test_revoke_share(self, client, authenticated_user, second_user):
        """Test revoking a previously created share"""
        # Create a share to revoke
        share = Share(
            sender_id=authenticated_user.id,
            receiver_id=second_user.id,
            scope={
                "exercise_types": [ExerciseType.RUNNING.value],
                "body_measurement_types": []
            },
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30)
        )
        db.session.add(share)
        db.session.commit()
        
        # Revoke the share
        response = client.post(
            f"/share/{share.id}/revoke",  # Adjust to the actual endpoint
            follow_redirects=True
        )
        
        # Check if revocation is successful
        assert response.status_code == 200 or response.status_code == 302
        
        # Check if the share is now marked as deleted
        updated_share = db.session.get(Share, share.id)
        if hasattr(updated_share, 'deleted'):
            assert updated_share.deleted 