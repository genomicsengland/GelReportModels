"""
Definitions of the GA4GH protocol types.
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys
import json
import inspect
import itertools

import avro.io
from avro.schema import UnionSchema, ArraySchema


class ProtocolElementEncoder(json.JSONEncoder):
    """
    Class responsible for encoding ProtocolElements as JSON.
    """
    def default(self, obj):
        if isinstance(obj, ProtocolElement):
            ret = {a: getattr(obj, a) for a in obj.__slots__}
        else:
            ret = super(ProtocolElementEncoder, self).default(obj)
        return ret


class ValidationResult(object):

    def __init__(self, result=None, messages=None):
        self.result = result or True
        self.messages = messages or []
        self.msg = "Class: [{class_name}] expects field: [{field_name}] "
        self.msg += "with schema type: [{schema_type}] but received value: [{value}]"
        self.schema_type_msg = "Schema: [{expected_schema}] has type: [{schema_type}] "
        self.schema_type_msg += "but received datum: [{datum}]"

    def update_class(self, class_name, field_name, schema_type, value):
        self.messages.append(self.msg.format(
            class_name=class_name,
            field_name=field_name,
            schema_type=schema_type,
            value=value
        ))

    def update_simple(self, expected_schema, schema_type, datum):
        self.result = False
        self.messages.append(self.schema_type_msg.format(
            expected_schema=expected_schema,
            schema_type=schema_type,
            datum=datum,
        ))

    def update_custom(self, custom_message):
        self.result = False
        self.messages.append(custom_message)


class ProtocolElement(object):
    """
    Superclass of GA4GH protocol elements. These elements are in one-to-one
    correspondence with the Avro definitions, and provide the basic elements
    of the on-the-wire protocol.
    """
    def __str__(self):
        return "{0}({1})".format(self.__class__.__name__, self.toJsonString())

    def __eq__(self, other):
        """
        Returns True if all fields in this protocol element are equal to the
        fields in the specified protocol element.
        """
        if type(other) != type(self):
            return False

        fieldNames = itertools.imap(lambda f: f.name, self.schema.fields)
        return all(getattr(self, k) == getattr(other, k) for k in fieldNames)

    def __ne__(self, other):
        return not self == other

    def toJsonString(self):
        """
        Returns a JSON encoded string representation of this ProtocolElement.
        """
        return json.dumps(self, cls=ProtocolElementEncoder)

    def toJsonDict(self):
        """
        Returns a JSON dictionary representation of this ProtocolElement.
        """
        out = {}
        for field in self.schema.fields:
            val = getattr(self, field.name)
            if self.isEmbeddedType(field.name):
                if isinstance(val, list):
                    out[field.name] = list(el.toJsonDict() for el in val)
                elif val is None:
                    out[field.name] = None
                else:
                    out[field.name] = val.toJsonDict()
            elif isinstance(val, list):
                out[field.name] = list(val)
            else:
                out[field.name] = val
        return out

    def validate_parts(self):
        out = {}

        for field in self.schema.fields:
            val = getattr(self, field.name)
            if self.isEmbeddedType(field.name):
                if isinstance(val, list):
                    out[field.name] = list(el.validate_parts() for el in val)
                elif val is None:
                    if isinstance(field.type, UnionSchema) and 'null' in [t.type for t in field.type.schemas]:
                        out[field.name] = True
                    else:
                        out[field.name] = False

                else:
                    out[field.name] = val.validate_parts()
            elif isinstance(val, list):
                if isinstance(field.type, UnionSchema):
                    out[field.name] = False
                    for sc in field.type.schemas:
                        if isinstance(sc, ArraySchema):
                            out[field.name] = list(avro.io.validate(sc.items, el) for el in val)
                else:
                    if isinstance(field.type, ArraySchema):
                        out[field.name] = list(avro.io.validate(field.type.items, el) for el in val)
                    else:
                        out[field.name] = False
            else:
                out[field.name] = avro.io.validate(field.type, val)

        return out

    def extended_validation(self):
        for field in self.schema.fields:
            val = getattr(self, field.name)
            if field.type.type == 'string':
                if val == '':
                    return False
        return self.validate(self.toJsonDict())

    @classmethod
    def validate(cls, jsonDict, verbose=False):
        """
        Validates the specified JSON dictionary to determine if it is an
        instance of this element's schema.
        """
        if verbose:
            validation_result = ValidationResult()
            return cls.validate_debug(jsonDict=jsonDict, validation_result=validation_result)
        return avro.io.validate(expected_schema=cls.schema, datum=jsonDict)

    @classmethod
    def validate_debug(cls, jsonDict, validation_result, expected_schema=None):
        """
        Returns ValidationResult with fields:
                - result (True or False)
                - messages (List of message strings ideally to help debug the problem)
        """
        INT_MIN_VALUE = -(1 << 31)
        INT_MAX_VALUE = (1 << 31) - 1
        LONG_MIN_VALUE = -(1 << 63)
        LONG_MAX_VALUE = (1 << 63) - 1
        expected_schema = expected_schema or cls.schema
        datum = jsonDict
        schema_type = expected_schema.type
        if schema_type == 'null':
            if not (datum is None):
                validation_result.update_simple(expected_schema=expected_schema, schema_type=schema_type, datum=datum)
        elif schema_type == 'boolean':
            if not isinstance(datum, bool):
                validation_result.update_simple(expected_schema=expected_schema, schema_type=schema_type, datum=datum)
        elif schema_type == 'string':
            if not isinstance(datum, basestring):
                validation_result.update_simple(expected_schema=expected_schema, schema_type=schema_type, datum=datum)
        elif schema_type == 'bytes':
            if not isinstance(datum, str):
                validation_result.update_simple(expected_schema=expected_schema, schema_type=schema_type, datum=datum)
        elif schema_type == 'int':
            if not ((isinstance(datum, int) or isinstance(datum, long)) and INT_MIN_VALUE <= datum <= INT_MAX_VALUE):
                validation_result.update_simple(expected_schema=expected_schema, schema_type=schema_type, datum=datum)
                custom_message = "{INT_MIN_VALUE} <= {datum} <= {INT_MAX_VALUE}".format(
                    INT_MIN_VALUE=INT_MIN_VALUE, datum=datum, INT_MAX_VALUE=INT_MAX_VALUE,
                )
                validation_result.update_custom(custom_message=custom_message)
        elif schema_type == 'long':
            if not ((isinstance(datum, int) or isinstance(datum, long)) and LONG_MIN_VALUE <= datum <= LONG_MAX_VALUE):
                validation_result.update_simple(expected_schema=expected_schema, schema_type=schema_type, datum=datum)
                custom_message = "{LONG_MIN_VALUE} <= {datum} <= {LONG_MAX_VALUE}".format(
                    LONG_MIN_VALUE=LONG_MIN_VALUE, datum=datum, LONG_MAX_VALUE=LONG_MAX_VALUE,
                )
                validation_result.update_custom(custom_message=custom_message)
        elif schema_type in ['float', 'double']:
            if not (isinstance(datum, int) or isinstance(datum, long) or isinstance(datum, float)):
                validation_result.update_simple(expected_schema=expected_schema, schema_type=schema_type, datum=datum)
        elif schema_type == 'fixed':
            if not (isinstance(datum, str) and len(datum) == expected_schema.size):
                validation_result.update_simple(expected_schema=expected_schema, schema_type=schema_type, datum=datum)
                message_template = "Length of datum: {datum_length} does not match expected schema size: {schema_size}"
                custom_message = message_template.format(
                    datum_length=len(datum), schema_size=expected_schema.size,
                )
                validation_result.update_custom(custom_message=custom_message)
        elif schema_type == 'enum':
            if datum not in expected_schema.symbols:
                validation_result.update_simple(expected_schema=expected_schema, schema_type=schema_type, datum=datum)
                custom_message = "datum: [{datum}] not contained within symbols: [{enum}]".format(
                    datum=datum, enum=expected_schema.symbols,
                )
                validation_result.update_custom(custom_message=custom_message)
        elif schema_type == 'array':
            if not isinstance(datum, list):
                validation_result.update_simple(expected_schema=expected_schema, schema_type=schema_type, datum=datum)
            if isinstance(datum, list):
                for data in datum:
                    if not avro.io.validate(expected_schema=expected_schema.items, datum=data):
                        validation_result.update_simple(
                            expected_schema=expected_schema.items, schema_type=expected_schema.items.type, datum=data
                        )
        elif schema_type == 'map':
            if not isinstance(datum, dict):
                validation_result.update_simple(expected_schema=expected_schema, schema_type=schema_type, datum=datum)
            elif isinstance(datum, dict):
                for key in datum.keys():
                    if not isinstance(key, basestring):
                        custom_message = "key: {key} must be of type str but it of type: {key_type}".format(
                            key=key, key_type=type(key),
                        )
                        validation_result.update_custom(custom_message=custom_message)
                for value in datum.values():
                    if not avro.io.validate(expected_schema=expected_schema.values, datum=value):
                        validation_result.update_simple(
                            expected_schema=expected_schema.values, schema_type=expected_schema.values.type, datum=value
                        )
        elif schema_type in ['union', 'error_union']:
            if not any([avro.io.validate(s, datum) for s in expected_schema.schemas]):
                for expected_schema in expected_schema.schemas:
                    if not avro.io.validate(expected_schema=expected_schema, datum=datum):
                        if hasattr(expected_schema, 'values'):
                            validation_result.update_simple(
                                expected_schema=expected_schema.values,
                                schema_type=expected_schema.values.type,
                                datum=datum
                            )
                        else:
                            validation_result.update_simple(
                                expected_schema=expected_schema,
                                schema_type=expected_schema,
                                datum=datum
                            )
        elif schema_type in ['record', 'error', 'request']:
            if isinstance(datum, dict):
                for f in expected_schema.fields:
                    if not avro.io.validate(expected_schema=f.type, datum=datum.get(f.name)):
                        cls.validate_debug(
                            jsonDict=datum.get(f.name),
                            validation_result=validation_result,
                            expected_schema=f.type)
                        validation_result.update_class(
                            class_name=expected_schema.name,
                            field_name=f.name,
                            schema_type=f.type,
                            value=datum.get(f.name)
                        )

        return validation_result

    @classmethod
    def fromJsonString(cls, jsonStr):
        """
        Returns a decoded ProtocolElement from the specified JSON string.
        """
        jsonDict = json.loads(jsonStr)
        return cls.fromJsonDict(jsonDict)

    @classmethod
    def fromJsonDict(cls, jsonDict):
        """
        Returns a decoded ProtocolElement from the specified JSON dictionary.
        """
        if jsonDict is None:
            raise ValueError("Required values not set in {0}".format(cls))

        instance = cls()
        for field in cls.schema.fields:
            instanceVal = field.default
            if field.name in jsonDict:
                val = jsonDict[field.name]
                if cls.isEmbeddedType(field.name):
                    instanceVal = cls._decodeEmbedded(field, val)
                else:
                    instanceVal = val
            setattr(instance, field.name, instanceVal)
        return instance

    @classmethod
    def _decodeEmbedded(cls, field, val):
        if val is None:
            return None

        embeddedType = cls.getEmbeddedType(field.name)
        if isinstance(field.type, UnionSchema):
            if isinstance(field.type.schemas[1], ArraySchema):
                return list(embeddedType.fromJsonDict(elem) for elem in val)
            else:
                return embeddedType.fromJsonDict(val)

        elif isinstance(field.type, avro.schema.ArraySchema):
            return list(embeddedType.fromJsonDict(elem) for elem in val)
        else:
            return embeddedType.fromJsonDict(val)


class SearchRequest(ProtocolElement):
    """
    The superclass of all SearchRequest classes in the protocol.
    """


class SearchResponse(ProtocolElement):
    """
    The superclass of all SearchResponse classes in the protocol.
    """
    @classmethod
    def getValueListName(cls):
        """
        Returns the name of the list used to store the values held
        in a page of results.
        """
        return cls._valueListName


def getProtocolClasses(superclass=ProtocolElement):
    """
    Returns all the protocol classes that are subclasses of the
    specified superclass. Only 'leaf' classes are returned,
    corresponding directly to the classes defined in the protocol.
    """
    # We keep a manual list of the superclasses that we define here
    # so we can filter them out when we're getting the protocol
    # classes.
    superclasses = {
        ProtocolElement, SearchRequest, SearchResponse
    }
    thisModule = sys.modules[__name__]
    subclasses = []
    for name, class_ in inspect.getmembers(thisModule):
        if ((inspect.isclass(class_) and
                issubclass(class_, superclass) and
                class_ not in superclasses)):
            subclasses.append(class_)
    return subclasses
