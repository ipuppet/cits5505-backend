import pytest
from server.models import BodyMeasurement
from server.utils.constants import BodyMeasurementType


class TestBodyMeasurementModel:
    def test_create_body_measurement(self, db_session, test_user):
        """Test creating a body measurement"""
        bm = BodyMeasurement(
            user_id=test_user.id, type=BodyMeasurementType.WEIGHT, value=70.5
        )
        db_session.add(bm)
        db_session.commit()

        assert bm.id is not None
        assert bm.user_id == test_user.id
        assert bm.type == BodyMeasurementType.WEIGHT
        assert bm.value == 70.5
        assert bm.created_at is not None

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
