import json
from wtforms import fields

from wtforms.validators import ValidationError


class JSONField(fields.StringField):
    def _value(self):
        return json.dumps(self.data) if self.data else ""

    def process_formdata(self, valuelist):
        if valuelist:
            try:
                self.data = json.loads(valuelist[0])
            except (ValueError, json.JSONDecodeError):
                raise ValidationError("Invalid JSON data")
        else:
            self.data = None

    def pre_validate(self, form):
        super().pre_validate(form)
        if self.data:
            try:
                json.dumps(self.data)
            except (TypeError, ValueError):
                raise ValidationError("Invalid JSON data")
