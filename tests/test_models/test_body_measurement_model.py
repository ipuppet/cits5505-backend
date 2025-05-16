import pytest
from server.models import BodyMeasurement
from server.utils.constants import BodyMeasurementType


class TestBodyMeasurementModel:
    
    @pytest.mark.parametrize(
        "measurement_type,valid_metrics",
        [
            (BodyMeasurementType.WEIGHT, 70.5),
            (BodyMeasurementType.HEIGHT, 180),
            (BodyMeasurementType.BODY_FAT, 15.0),
        ],
        ids=[
            "weight_measurement",
            "height_measurement",
            "body_fat_measurement",
        ],
    )
    def test_valid_body_measurement_creation(self, db_session, measurement_type, valid_metrics):
        """Test valid body measurement creation with correct metrics"""
        body_measurement = BodyMeasurement(
            user_id=1, type=measurement_type, value=valid_metrics
        )
        db_session.add(body_measurement)
        db_session.commit()

        assert body_measurement.id is not None
        assert body_measurement.created_at is not None
        assert body_measurement.value == valid_metrics
   
    @pytest.mark.parametrize(
        "measurement_type,invalid_metrics",
        [
            (BodyMeasurementType.WEIGHT,-10),
            (BodyMeasurementType.HEIGHT,"abc"),
            (BodyMeasurementType.BODY_FAT, 200),
        ],
        ids=[
            "weight_invalid_value",
            "height_invalid_value",
            "body_fat_invalid_value",
        ],
    )
    def test_invalid_body_measurement_creation(self, measurement_type, invalid_metrics):
        """Test invalid body measurement creation with incorrect metrics"""
        with pytest.raises(ValueError):
            BodyMeasurement(
                user_id=1, type=measurement_type, value=invalid_metrics
            )
    
    @pytest.mark.parametrize(
        "measurement_type,missing_metrics",
        [
            (BodyMeasurementType.WEIGHT, None),
            (BodyMeasurementType.HEIGHT, None),
            (BodyMeasurementType.BODY_FAT, None),
        ],
        ids=[
            "weight_missing_value",
            "height_missing_value",
            "body_fat_missing_value",
        ],
    )
    def test_invalid_metrics_validation(self, measurement_type, missing_metrics):
        # Test validation of required metrics fields
        with pytest.raises(ValueError):
            BodyMeasurement(
                user_id=1, type=measurement_type, value=missing_metrics
            )

    
    def test_get_by_user(self, db_session, test_user):
        """Test get_by_user static method"""
        bm1 = BodyMeasurement(
            user_id=test_user.id, type=BodyMeasurementType.HEIGHT, value=180
        )
        bm2 = BodyMeasurement(
            user_id=test_user.id, type=BodyMeasurementType.WEIGHT, value=75
        )
        db_session.add_all([bm1, bm2])
        db_session.commit()

        measurements = BodyMeasurement.get_by_user(test_user.id).all()
        assert len(measurements) == 2
        assert all(m.user_id == test_user.id for m in measurements)
    
    def test_get_by_user_no_user(self):
        """Test get_by_user raises ValueError if user_id is missing"""
        with pytest.raises(ValueError):
            BodyMeasurement.get_by_user(None)
