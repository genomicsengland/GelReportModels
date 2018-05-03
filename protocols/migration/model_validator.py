import json


class PayloadValidation(object):
    def __init__(self, klass, payload):
        self._payload = payload
        self._klass = klass

    @property
    def is_valid(self):
        return self._klass.validate(self._payload)  # , verbose=True)

    def validate(self):
        if not self.is_valid:
            object_type = self._klass
            detail = 'Payload from object type: {object_type} does not match with the schema: {schema}'
            raise ValueError(detail.format(
                object_type=object_type,
                schema=json.dumps(self._klass.fromJsonDict(self._payload).validate_parts()))
            )
