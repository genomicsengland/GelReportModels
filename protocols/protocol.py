"""
Definitions of the GA4GH protocol types.
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from past.builtins import basestring
from builtins import int

import sys
import json
import inspect
import dictdiffer
import logging

import avro.io
import avro.schema
from avro.schema import UnionSchema, ArraySchema, RecordSchema


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

    def short_messages(self, characters=80):
        return [message[0:characters] for message in self.messages]


class ProtocolElement(object):
    """
    Superclass of GA4GH protocol elements. These elements are in one-to-one
    correspondence with the Avro definitions, and provide the basic elements
    of the on-the-wire protocol.
    """
    def __str__(self):
        return "{0}({1})".format(self.__class__.__name__, self.toJsonString())

    def __hash__(self):
        return self.toJsonString().__hash__()

    def __eq__(self, other):
        """
        Returns True if all fields in this protocol element are equal to the
        fields in the specified protocol element.
        """
        if type(other) != type(self):
            return False

        fieldNames = map(lambda f: f.name, self.schema.fields)
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
            if val is None:
                out[field.name] = None
            elif self.isEmbeddedType(field.name):
                if isinstance(val, list):
                    out[field.name] = list(el.toJsonDict() for el in val)
                elif isinstance(val, dict):
                    out[field.name] = {key: el.toJsonDict() for key, el in val.items()}
                else:
                    out[field.name] = val.toJsonDict()
            else:
                out[field.name] = val
        return out

    def equals(self, instance):
        """
        Method to compare entities
        :return:
        """
        if not isinstance(instance, ProtocolElement):
            logging.error("Comparing instance of type {} with instance of type {}".format(type(self), type(instance)))
            return False
        differences = list(dictdiffer.diff(self.toJsonDict(), instance.toJsonDict()))
        if differences is None or differences == []:
            return True
        return differences

    def validate_parts(self):
        out = {}

        for field in self.schema.fields:
            val = getattr(self, field.name)
            if self.isEmbeddedType(field.name):
                if isinstance(val, list):
                    out[field.name] = list(el.validate_parts() for el in val)
                elif isinstance(val, dict):
                    out[field.name] = {key: el.validate_parts() for (key, el) in val.items()}
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
                            out[field.name] = list(avro_validate(sc.items, el) for el in val)
                else:
                    if isinstance(field.type, ArraySchema):
                        out[field.name] = list(avro_validate(field.type.items, el) for el in val)
                    else:
                        out[field.name] = False
            else:
                out[field.name] = avro_validate(field.type, val)

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
        return avro_validate(expected_schema=cls.schema, datum=jsonDict)

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
            if not ((isinstance(datum, int)) and INT_MIN_VALUE <= datum <= INT_MAX_VALUE):
                validation_result.update_simple(expected_schema=expected_schema, schema_type=schema_type, datum=datum)
                custom_message = "{INT_MIN_VALUE} <= {datum} <= {INT_MAX_VALUE}".format(
                    INT_MIN_VALUE=INT_MIN_VALUE, datum=datum, INT_MAX_VALUE=INT_MAX_VALUE,
                )
                validation_result.update_custom(custom_message=custom_message)
        elif schema_type == 'long':
            if not ((isinstance(datum, int)) and LONG_MIN_VALUE <= datum <= LONG_MAX_VALUE):
                validation_result.update_simple(expected_schema=expected_schema, schema_type=schema_type, datum=datum)
                custom_message = "{LONG_MIN_VALUE} <= {datum} <= {LONG_MAX_VALUE}".format(
                    LONG_MIN_VALUE=LONG_MIN_VALUE, datum=datum, LONG_MAX_VALUE=LONG_MAX_VALUE,
                )
                validation_result.update_custom(custom_message=custom_message)
        elif schema_type in ['float', 'double']:
            if not (isinstance(datum, int) or isinstance(datum, float)):
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
            elif isinstance(datum, list):
                for data in datum:
                    if not avro_validate(expected_schema=expected_schema.items, datum=data):
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
                    if not avro_validate(expected_schema=expected_schema.values, datum=value):
                        validation_result.update_simple(
                            expected_schema=expected_schema.values, schema_type=expected_schema.values.type, datum=value
                        )
        elif schema_type in ['union', 'error_union']:
            if not any([avro_validate(s, datum) for s in expected_schema.schemas]):
                for expected_schema in expected_schema.schemas:
                    if not avro_validate(expected_schema=expected_schema, datum=datum):
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
                    if not avro_validate(expected_schema=f.type, datum=datum.get(f.name)):
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
            else:
                validation_result.update_simple(
                    expected_schema=expected_schema,
                    schema_type=expected_schema,
                    datum=datum
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
    def fromJsonDict(cls, jsonDict, key_mapper=(lambda x: x)):
        """
        Returns a decoded ProtocolElement from the specified JSON dictionary.
        """
        if jsonDict is None:
            raise ValueError("Required values not set in {0}".format(cls))

        if isinstance(jsonDict, dict):
            json_key_mapping = {key_mapper(key): key for key in jsonDict.keys()}
        else:
            json_key_mapping = dict()
        protocol_key_mapping = {key_mapper(key): key for key in cls.__slots__}

        instance = cls()
        for field in cls.schema.fields:
            if field.has_default:
                instanceVal = field.default
            else:
                instanceVal = None
            if key_mapper(field.name) in json_key_mapping:
                json_mapped_name = json_key_mapping[key_mapper(field.name)]
                protocol_mapped_name = protocol_key_mapping[key_mapper(field.name)]
                val = jsonDict[json_mapped_name]
                if cls.isEmbeddedType(protocol_mapped_name):
                    instanceVal = cls._decodeEmbedded(field, val, key_mapper=key_mapper)
                else:
                    instanceVal = val
            setattr(instance, field.name, instanceVal)
        return instance

    @classmethod
    def migrateFromJsonDict(cls, jsonDict):
        """
        like fromJsonDict but applies some fuzzy rules
        """
        return cls.fromJsonDict(jsonDict, lambda s: s.lower().replace("_", ""))

    def updateWithJsonDict(self, jsonDict):
        """
        Updates this object from a dict
        """
        if jsonDict is None:
            raise ValueError("Required values not set in {0}".format(self))

        for field in self.schema.fields:
            if field.name in jsonDict:
                val = jsonDict[field.name]
                if self.isEmbeddedType(field.name):
                    instanceVal = self._decodeEmbedded(field, val)
                else:
                    instanceVal = val
                if instanceVal is not None:
                    setattr(self, field.name, instanceVal)


    @classmethod
    def _decodeEmbedded(cls, field, val, key_mapper=(lambda x: x)):
        if val is None:
            return None

        embeddedType = cls.getEmbeddedType(field.name)
        if isinstance(field.type, UnionSchema):
            if isinstance(field.type.schemas[1], ArraySchema):
                return list(embeddedType.fromJsonDict(elem, key_mapper=key_mapper) for elem in val)
            elif isinstance(field.type.schemas[1], avro.schema.MapSchema):
                return {key: embeddedType.fromJsonDict(elem, key_mapper=key_mapper) for (key, elem) in val.items()}
            else:
                return embeddedType.fromJsonDict(val, key_mapper=key_mapper)

        elif isinstance(field.type, avro.schema.ArraySchema):
            return list(embeddedType.fromJsonDict(elem, key_mapper=key_mapper) for elem in val)
        elif isinstance(field.type, avro.schema.MapSchema):
            return {key: embeddedType.fromJsonDict(elem, key_mapper=key_mapper) for (key, elem) in val.items()}
        else:
            return embeddedType.fromJsonDict(val, key_mapper=key_mapper)


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


def avro_parse(schema):
    if sys.version_info.major > 2:
        # python 3 version
        return avro.schema.Parse(schema)
    else:
        # python 2 version
        return avro.schema.parse(schema)


def avro_validate(expected_schema, datum):
    if sys.version_info.major > 2:
        # python 3 version
        return avro.io.Validate(expected_schema=expected_schema, datum=datum)
    else:
        # python 2 version
        return avro.io.validate(expected_schema=expected_schema, datum=datum)
