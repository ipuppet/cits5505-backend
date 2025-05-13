from flask.json.provider import DefaultJSONProvider
from datetime import time

from server.models import db
from server.utils.constants import ExerciseType, BodyMeasurementType


class JSONProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, db.Model):
            return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
        elif hasattr(obj, "all") and callable(obj.all):
            return obj.all()
        elif isinstance(obj, time):
            return obj.isoformat()
        elif isinstance(obj, ExerciseType):
            return obj.name
        elif isinstance(obj, BodyMeasurementType):
            return obj.name
        return super().default(obj)
