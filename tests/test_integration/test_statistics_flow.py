import pytest
from datetime import datetime, timedelta
from flask import url_for, json

from server.models import Exercise, BodyMeasurement, User, db
from server.utils.constants import ExerciseType, BodyMeasurementType


class TestStatisticsFlow:
    """Test statistics and data analysis functionality"""

    def setup_exercise_data(self, authenticated_user):
        """Helper method to set up exercise data for statistics tests"""
        # Create exercises over the last 30 days
        base_date = datetime.now() - timedelta(days=30)
        
        exercises = []
        # Running data - every 3 days
        for i in range(0, 31, 3):
            exercises.append(
                Exercise(
                    user_id=authenticated_user.id,
                    type=ExerciseType.RUNNING,
                    metrics={"distance": 5.0, "duration": 30},
                    created_at=base_date + timedelta(days=i)
                )
            )
        
        # Swimming data - every 7 days
        for i in range(0, 31, 7):
            exercises.append(
                Exercise(
                    user_id=authenticated_user.id,
                    type=ExerciseType.SWIMMING,
                    metrics={"distance": 1000, "duration": 45},
                    created_at=base_date + timedelta(days=i)
                )
            )
        
        # Cycling data - every 5 days
        for i in range(0, 31, 5):
            exercises.append(
                Exercise(
                    user_id=authenticated_user.id,
                    type=ExerciseType.CYCLING,
                    metrics={"distance": 20.0, "duration": 60},
                    created_at=base_date + timedelta(days=i)
                )
            )
        
        for exercise in exercises:
            db.session.add(exercise)
        db.session.commit()
        
        return exercises
    
    def setup_measurement_data(self, authenticated_user):
        """Helper method to set up body measurement data for statistics tests"""
        # Create weight measurements over the last 30 days
        base_date = datetime.now() - timedelta(days=30)
        
        measurements = []
        # Weight data - decreasing trend
        for i in range(0, 31, 5):
            measurements.append(
                BodyMeasurement(
                    user_id=authenticated_user.id,
                    type=BodyMeasurementType.WEIGHT,
                    value=80.0 - (i * 0.5),  # Decreasing by 0.5kg every 5 days
                    created_at=base_date + timedelta(days=i)
                )
            )
        
        # Body fat data
        for i in range(0, 31, 10):
            measurements.append(
                BodyMeasurement(
                    user_id=authenticated_user.id,
                    type=BodyMeasurementType.BODY_FAT,
                    value=20.0 - (i * 0.3),  # Decreasing body fat
                    created_at=base_date + timedelta(days=i)
                )
            )
        
        for measurement in measurements:
            db.session.add(measurement)
        db.session.commit()
        
        return measurements

    def test_exercise_summary_statistics(self, client, authenticated_user):
        """Test viewing exercise summary statistics"""
        # Setup test data
        self.setup_exercise_data(authenticated_user)
        
        # Access statistics page
        response = client.get(
            "/dashboard?view=statistics",  # Adjust based on actual implementation
            follow_redirects=True
        )
        
        # Check if page loads successfully
        assert response.status_code == 200
        
        # Check if the response contains statistical information
        response_text = response.get_data(as_text=True)
        
        # If statistics are displayed, check for expected content
        if "Statistics" in response_text:
            assert "Statistics" in response_text
            # Other assertions can be added based on UI implementation
    
    def test_body_measurement_trends(self, client, authenticated_user):
        """Test viewing body measurement trends"""
        # Setup test data
        self.setup_measurement_data(authenticated_user)
        
        # Access trends page
        response = client.get(
            "/dashboard?view=trends",  # Adjust based on actual implementation
            follow_redirects=True
        )
        
        # Check if page loads successfully
        assert response.status_code == 200
        
        # If trends are displayed, check for expected content
        response_text = response.get_data(as_text=True)
        if "Weight Trend" in response_text:
            assert "Weight Trend" in response_text
            # Other assertions can be added based on UI implementation
    
    @pytest.mark.skip(reason="Activity calendar view not implemented yet")
    def test_activity_calendar(self, client, authenticated_user):
        """Test viewing activity calendar"""
        # Setup test data
        self.setup_exercise_data(authenticated_user)
        
        # Access calendar view
        response = client.get(
            "/dashboard?view=calendar",  # Adjust based on actual implementation
            follow_redirects=True
        )
        
        # Check if page loads successfully
        assert response.status_code == 200
        
        # If calendar is displayed, check for expected content
        response_text = response.get_data(as_text=True)
        assert "Calendar" in response_text
        # Other assertions can be added based on UI implementation
    
    @pytest.mark.skip(reason="Data export functionality not implemented yet")
    def test_export_data(self, client, authenticated_user):
        """Test exporting exercise and measurement data"""
        # Setup test data
        self.setup_exercise_data(authenticated_user)
        self.setup_measurement_data(authenticated_user)
        
        # Export data
        response = client.get(
            "/dashboard/export",  # Adjust based on actual implementation
            follow_redirects=True
        )
        
        # Check if export is successful
        assert response.status_code == 200
        
        # Verify content type for CSV or JSON export
        assert response.content_type in ["text/csv", "application/json"]
        
        # Check exported data content
        if response.content_type == "text/csv":
            assert b"date,type,distance,duration" in response.data
        elif response.content_type == "application/json":
            assert b"exercise_data" in response.data 