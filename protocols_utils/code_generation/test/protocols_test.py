"""
DO NOT EDIT THIS FILE!!
This file is automatically generated by the process_schemas.py program
in the scripts directory. It is not intended to be edited directly. If
you need to update the GEL protocol classes, please run the script
on the appropriate schema version.
"""
from protocols.protocol import ProtocolElement
from protocols.protocol import SearchRequest
from protocols.protocol import SearchResponse

import avro.schema

version = '0.0.0'


class A(ProtocolElement):
    """
    No documentation
    """
    _schemaSource = """
{"type": "record", "name": "A", "namespace": "org.gel.test.avro", "fields": [{"name": "nullable_b",
"type": ["null", {"type": "record", "name": "B", "fields": [{"name": "integer_with_default", "type":
"int", "default": 5}, {"name": "integer_without_default", "type": "int"}, {"name":
"string_with_default", "type": "string", "default": "default_value"}, {"name":
"string_without_default", "type": "string"}, {"name": "string_nullable", "type": "string"}, {"name":
"float_with_default", "type": "float", "default": 0.5}, {"name": "float_without_default", "type":
"float"}]}]}, {"name": "just_b", "type": "B"}]}
"""
    schema = avro.schema.Parse(_schemaSource)
    requiredFields = {
        "just_b",
        "nullable_b",
    }

    @classmethod
    def isEmbeddedType(cls, fieldName):
        embeddedTypes = {
            'just_b': B,
            'nullable_b': B,
        }
        return fieldName in embeddedTypes

    @classmethod
    def getEmbeddedType(cls, fieldName):
        embeddedTypes = {
            'just_b': B,
            'nullable_b': B,
        }

        return embeddedTypes[fieldName]

    __slots__ = [
        'just_b', 'nullable_b'
    ]

    def __init__(self, **kwargs):
        self.just_b = kwargs.get(
            'just_b', B())
        self.nullable_b = kwargs.get(
            'nullable_b', None)


class B(ProtocolElement):
    """
    No documentation
    """
    _schemaSource = """
{"type": "record", "name": "B", "namespace": "org.gel.test.avro", "fields": [{"name":
"integer_with_default", "type": "int", "default": 5}, {"name": "integer_without_default", "type":
"int"}, {"name": "string_with_default", "type": "string", "default": "default_value"}, {"name":
"string_without_default", "type": "string"}, {"name": "string_nullable", "type": "string"}, {"name":
"float_with_default", "type": "float", "default": 0.5}, {"name": "float_without_default", "type":
"float"}]}
"""
    schema = avro.schema.Parse(_schemaSource)
    requiredFields = {
        "float_without_default",
        "integer_without_default",
        "string_nullable",
        "string_without_default",
    }

    @classmethod
    def isEmbeddedType(cls, fieldName):
        embeddedTypes = {}
        return fieldName in embeddedTypes

    @classmethod
    def getEmbeddedType(cls, fieldName):
        embeddedTypes = {}

        return embeddedTypes[fieldName]

    __slots__ = [
        'float_with_default', 'float_without_default',
        'integer_with_default', 'integer_without_default',
        'string_nullable', 'string_with_default',
        'string_without_default'
    ]

    def __init__(self, **kwargs):
        self.float_with_default = kwargs.get(
            'float_with_default', 0.5)
        self.float_without_default = kwargs.get(
            'float_without_default', None)
        self.integer_with_default = kwargs.get(
            'integer_with_default', 5)
        self.integer_without_default = kwargs.get(
            'integer_without_default', None)
        self.string_nullable = kwargs.get(
            'string_nullable', None)
        self.string_with_default = kwargs.get(
            'string_with_default', 'default_value')
        self.string_without_default = kwargs.get(
            'string_without_default', None)
