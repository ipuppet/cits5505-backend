import json
from wtforms import fields

from wtforms.validators import ValidationError


class JSONField(fields.Field):
    def _value(self):
        if self.data is not None:
            try:
                return json.dumps(self.data, ensure_ascii=False, indent=2)
            except TypeError:
                return ""
        else:
            return ""

    def process_data(self, value):
        if value is None:
            self.data = None
        elif isinstance(value, str):
            if not value:
                self.data = None
            else:
                try:
                    self.data = json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    self.data = value
        else:
            self.data = value

    def process_formdata(self, valuelist):
        if valuelist:
            value = valuelist[0]
            if not value:
                self.data = None
                return
            if isinstance(value, (dict, list)):
                self.data = value
                return

            try:
                self.data = json.loads(value)
            except (json.JSONDecodeError, TypeError):
                self.data = None
                raise ValidationError("Invalid JSON data.")
        else:
            self.data = None

    def pre_validate(self, form):
        if self.data is not None and not isinstance(self.data, (dict, list)):
            raise ValidationError("Field must be a valid JSON object or array.")
