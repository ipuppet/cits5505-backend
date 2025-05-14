import pytest
from server.models import BodyMeasurement, User
from server.utils.constants import BodyMeasurementType

class TestBodyMeasurementModel:
    def test_create_body_measurement(self, session):
        """Test creating a body measurement"""
        user = User(username="bmuser", password="pw", email="bm@ex.com", nickname="BM")
        session.add(user)
        session.commit()

        bm = BodyMeasurement(
            user_id=user.id,
            type=BodyMeasurementType.WEIGHT,
            value=70.5
        )
        session.add(bm)
        session.commit()

        assert bm.id is not None
        assert bm.user_id == user.id
        assert bm.type == BodyMeasurementType.WEIGHT
        assert bm.value == 70.5
        assert bm.created_at is not None

    def test_get_by_user(self, session):
        """Test get_by_user static method"""
        user = User(username="bmuser2", password="pw", email="bm2@ex.com", nickname="BM2")
        session.add(user)
        session.commit()

        bm1 = BodyMeasurement(user_id=user.id, type=BodyMeasurementType.HEIGHT, value=180)
        bm2 = BodyMeasurement(user_id=user.id, type=BodyMeasurementType.WEIGHT, value=75)
        session.add_all([bm1, bm2])
        session.commit()

        measurements = BodyMeasurement.get_by_user(user.id).all()
        assert len(measurements) == 2
        assert all(m.user_id == user.id for m in measurements)

    def test_get_by_user_no_user(self):
        """Test get_by_user raises ValueError if user_id is missing"""
        with pytest.raises(ValueError):
            BodyMeasurement.get_by_user(None)