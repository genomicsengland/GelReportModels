import sys

import factory.fuzzy
from factory.base import FactoryMetaClass, BaseFactory, BaseMeta


def mock_schema(protocol):
    """
    :type protocol: Protocol
    """
    INT_MIN_VALUE = -(1 << 31)
    INT_MAX_VALUE = (1 << 31) - 1
    LONG_MIN_VALUE = -(1 << 63)
    LONG_MAX_VALUE = (1 << 63) - 1
    expected_schema = protocol.schema

    mock_result = {}
    for field in expected_schema.fields:
        schema_type = field.type.type
        name = field.name
        if schema_type == 'null':
            mock_result[name] = 'null'
        elif schema_type == 'boolean':
            mock_result[name] = factory.fuzzy.FuzzyChoice([True, False])
        elif schema_type == 'string':
            mock_result[name] = factory.fuzzy.FuzzyText()
        elif schema_type == 'bytes':
            mock_result[name] = b'a'
        elif schema_type == 'int':
            mock_result[name] = factory.fuzzy.FuzzyInteger(INT_MIN_VALUE, INT_MAX_VALUE)
        elif schema_type == 'long':
            mock_result[name] = factory.fuzzy.FuzzyInteger(LONG_MIN_VALUE, LONG_MAX_VALUE)
        elif schema_type in ['float', 'double']:
            mock_result[name] = factory.fuzzy.FuzzyFloat(sys.float_info.min)
        elif schema_type == 'enum':
            mock_result[name] = factory.fuzzy.FuzzyChoice(expected_schema.symbols)
    return mock_result

class FactoryAvroMetaClass(FactoryMetaClass):
    def __new__(mcs, *args):
        attrs = args[2]
        if hasattr(attrs['Meta'], 'model'):
            fuzzy_attributes = mock_schema(attrs['Meta'].model)
            for parent in args[1]:
                fuzzy_attributes.update(parent._meta.pre_declarations.declarations)
            fuzzy_attributes.update(attrs)
            attrs = fuzzy_attributes

        return super(FactoryAvroMetaClass, mcs).__new__(mcs, args[0], args[1], attrs)

FactoryAvro = FactoryAvroMetaClass(str('Factory'), (BaseFactory,), {
    'Meta': BaseMeta,
    '__doc__': """Factory base with build and create support.

    This class has the ability to support multiple ORMs by using custom creation
    functions.
    """,
})
