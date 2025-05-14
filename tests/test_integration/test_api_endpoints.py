import pytest
import json
from flask import url_for
from datetime import datetime, timedelta

from server.models import User, Exercise, BodyMeasurement, db
from server.utils.constants import ExerciseType, BodyMeasurementType


class TestAPIEndpoints:
    """Test REST API endpoints"""

    def get_auth_headers(self, client, authenticated_user):
        """Helper method to get authentication headers"""
        # In a real API, we would need to get an auth token
        # For now, we assume the sessions from the authenticated_user fixture work
        return {}

    @pytest.mark.skip(reason="API exercise endpoint not implemented yet")
    def test_get_exercises_api(self, client, authenticated_user):
        """Test GET /api/exercises endpoint"""
        # Add some exercise data
        exercises = [
            Exercise(
                user_id=authenticated_user.id,
                type=ExerciseType.RUNNING,
                metrics={"distance": 5.0, "duration": 30},
                created_at=datetime.now() - timedelta(days=1)
            ),
            Exercise(
                user_id=authenticated_user.id,
                type=ExerciseType.SWIMMING,
                metrics={"distance": 1000, "duration": 45},
                created_at=datetime.now() - timedelta(days=2)
            )
        ]
        
        for exercise in exercises:
            db.session.add(exercise)
        db.session.commit()
        
        # Get exercises through API
        headers = self.get_auth_headers(client, authenticated_user)
        response = client.get(
            "/api/exercises",
            headers=headers
        )
        
        # Check API response
        assert response.status_code == 200
        assert response.content_type == "application/json"
        
        # Parse response data
        data = json.loads(response.data)
        
        # Verify content
        assert "exercises" in data
        assert len(data["exercises"]) >= 2
        
        # Check exercise data
        exercise_types = [ex["type"] for ex in data["exercises"]]
        assert ExerciseType.RUNNING.value in exercise_types
        assert ExerciseType.SWIMMING.value in exercise_types
    
    @pytest.mark.skip(reason="API exercise creation endpoint not implemented yet")
    def test_create_exercise_api(self, client, authenticated_user):
        """Test POST /api/exercises endpoint"""
        # Exercise data to create
        exercise_data = {
            "type": ExerciseType.RUNNING.value,
            "metrics": {
                "distance": 10.0,
                "duration": 60
            }
        }
        
        # Create exercise through API
        headers = self.get_auth_headers(client, authenticated_user)
        response = client.post(
            "/api/exercises",
            data=json.dumps(exercise_data),
            content_type="application/json",
            headers=headers
        )
        
        # Check API response
        assert response.status_code == 201  # Created
        assert response.content_type == "application/json"
        
        # Parse response data
        data = json.loads(response.data)
        
        # Verify returned data
        assert "id" in data
        assert data["type"] == ExerciseType.RUNNING.value
        assert data["metrics"]["distance"] == 10.0
        assert data["metrics"]["duration"] == 60
        
        # Verify in database
        exercise = db.session.get(Exercise, data["id"])
        assert exercise is not None
        assert exercise.type == ExerciseType.RUNNING
        assert exercise.metrics["distance"] == 10.0
    
    @pytest.mark.skip(reason="API body measurement endpoint not implemented yet")
    def test_get_body_measurements_api(self, client, authenticated_user):
        """Test GET /api/measurements endpoint"""
        # Add some body measurement data
        measurements = [
            BodyMeasurement(
                user_id=authenticated_user.id,
                type=BodyMeasurementType.WEIGHT,
                value=75.5,
                created_at=datetime.now() - timedelta(days=1)
            ),
            BodyMeasurement(
                user_id=authenticated_user.id,
                type=BodyMeasurementType.BODY_FAT,
                value=15.0,
                created_at=datetime.now() - timedelta(days=2)
            )
        ]
        
        for measurement in measurements:
            db.session.add(measurement)
        db.session.commit()
        
        # Get measurements through API
        headers = self.get_auth_headers(client, authenticated_user)
        response = client.get(
            "/api/measurements",
            headers=headers
        )
        
        # Check API response
        assert response.status_code == 200
        assert response.content_type == "application/json"
        
        # Parse response data
        data = json.loads(response.data)
        
        # Verify content
        assert "measurements" in data
        assert len(data["measurements"]) >= 2
        
        # Check measurement data
        measurement_types = [m["type"] for m in data["measurements"]]
        assert BodyMeasurementType.WEIGHT.value in measurement_types
        assert BodyMeasurementType.BODY_FAT.value in measurement_types
    
    @pytest.mark.skip(reason="API statistics endpoint not implemented yet")
    def test_get_statistics_api(self, client, authenticated_user):
        """Test GET /api/statistics endpoint"""
        # Add some exercise data for statistics
        base_date = datetime.now() - timedelta(days=30)
        
        # Add running exercises for 10 days
        for i in range(10):
            exercise = Exercise(
                user_id=authenticated_user.id,
                type=ExerciseType.RUNNING,
                metrics={"distance": 5.0, "duration": 30},
                created_at=base_date + timedelta(days=i)
            )
            db.session.add(exercise)
        
        db.session.commit()
        
        # Get statistics through API
        headers = self.get_auth_headers(client, authenticated_user)
        response = client.get(
            "/api/statistics",
            headers=headers
        )
        
        # Check API response
        assert response.status_code == 200
        assert response.content_type == "application/json"
        
        # Parse response data
        data = json.loads(response.data)
        
        # Verify statistics content
        assert "statistics" in data
        assert "total_exercises" in data["statistics"]
        assert data["statistics"]["total_exercises"] >= 10
        
        # Check specific statistics for running
        assert "exercise_types" in data["statistics"]
        assert ExerciseType.RUNNING.value in data["statistics"]["exercise_types"]
        assert data["statistics"]["exercise_types"][ExerciseType.RUNNING.value]["count"] >= 10
        assert "total_distance" in data["statistics"]["exercise_types"][ExerciseType.RUNNING.value]
        assert data["statistics"]["exercise_types"][ExerciseType.RUNNING.value]["total_distance"] >= 50.0  # 10 * 5.0
    
    @pytest.mark.skip(reason="API export endpoint not implemented yet")
    def test_export_data_api(self, client, authenticated_user):
        """Test GET /api/export endpoint"""
        # Add some data to export
        exercise = Exercise(
            user_id=authenticated_user.id,
            type=ExerciseType.RUNNING,
            metrics={"distance": 5.0, "duration": 30},
            created_at=datetime.now()
        )
        db.session.add(exercise)
        
        measurement = BodyMeasurement(
            user_id=authenticated_user.id,
            type=BodyMeasurementType.WEIGHT,
            value=75.5,
            created_at=datetime.now()
        )
        db.session.add(measurement)
        
        db.session.commit()
        
        # Test JSON export
        headers = self.get_auth_headers(client, authenticated_user)
        response = client.get(
            "/api/export?format=json",
            headers=headers
        )
        
        # Check API response
        assert response.status_code == 200
        assert response.content_type == "application/json"
        
        # Parse response data
        data = json.loads(response.data)
        
        # Verify export content
        assert "data" in data
        assert "exercises" in data["data"]
        assert "measurements" in data["data"]
        assert len(data["data"]["exercises"]) >= 1
        assert len(data["data"]["measurements"]) >= 1 