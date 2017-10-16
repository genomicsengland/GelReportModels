import sys

import factory.fuzzy
from factory.base import FactoryMetaClass, BaseFactory, BaseMeta
from protocols.util.dependency_manager import DependencyManager


BASIC_TYPES = ['null', 'boolean', 'string', 'bytes', 'int', 'long', 'float', 'double', 'enum']
COMPLEX_TYPES = ['record', 'array', 'map']
UNION_TYPE = 'union'
DEFAULT_ELEMENTS_ARRAY = 5
DEFAULT_ELEMENTS_MAP = 5
INT_MIN_VALUE = -(1 << 31)
INT_MAX_VALUE = (1 << 31) - 1
LONG_MIN_VALUE = -(1 << 63)
LONG_MAX_VALUE = (1 << 63) - 1


def mock_schema(protocol, version):
    """
    :type protocol: Protocol
    :param version: the package version as registered in the dependency manager
    :type version: str
    :return: a dictionary following the schema of the protocol containing mocked values
    :rtype: dict
    """
    expected_schema = protocol.schema
    dependency_manager = DependencyManager()
    if version is not None:
        dependencies = dependency_manager.get_version_dependencies(version)
    else:
        dependencies = dependency_manager.get_latest_version_dependencies()

    mock_result = {}
    for field in expected_schema.fields:
        field_type = field.type.type
        field_name = field.name
        mock_result[field_name] = mock_field(field, field_type, dependencies, version)
    return mock_result


def mock_field(field, field_type, dependencies, version):
    """
    :param field:
    :param field_type:
    :param dependencies: the list of dependencies as provided by the dependency manager
    :type dependencies: dict
    :param version: the package version as registered in the dependency manager
    :type version: str
    :return: the mocked value for a field
    :rtype: object
    """
    value = None
    if field_type in BASIC_TYPES:
        value = mock_basic_type(field, field_type)
    # by convention we expect that nullable fields are defined as "union {null, RelevantType}"
    # we get the first type of union expecting that it is the null type
    elif field_type == UNION_TYPE:
        value = mock_basic_type(field.type.schemas[0], field.type.schemas[0].type)
    elif field_type in COMPLEX_TYPES:
        value = mock_complex_type(field, field_type, dependencies, version)
    return value


def mock_basic_type(field, field_type):
    """
    :param field:
    :param field_type:
    :return: the mocked value for the basic type
    :rtype: object
    """
    value = None
    if field_type == 'null':
        value =  None
    elif field_type == 'boolean':
        value = factory.fuzzy.FuzzyChoice([True, False]).fuzz()
    elif field_type == 'string':
        value = factory.fuzzy.FuzzyText().fuzz()
    elif field_type == 'bytes':
        value = b'a'
    elif field_type == 'int':
        value = factory.fuzzy.FuzzyInteger(INT_MIN_VALUE, INT_MAX_VALUE).fuzz()
    elif field_type == 'long':
        value = factory.fuzzy.FuzzyInteger(LONG_MIN_VALUE, LONG_MAX_VALUE).fuzz()
    elif field_type in ['float', 'double']:
        value = factory.fuzzy.FuzzyFloat(sys.float_info.min).fuzz()
    elif field_type == 'enum':
        if hasattr(field, 'symbols'):
            symbols = field.symbols
        else:
            symbols = field.type.symbols
        value = factory.fuzzy.FuzzyChoice(symbols).fuzz()
    return value


def mock_complex_type(field, field_type, dependencies, version):
    """
    :param field:
    :param field_type:
    :param dependencies:
    :param version:
    :return: the mocked value for a complex type
    :rtype: object
    """
    value = None
    if field_type == 'record':
        if isinstance(field.type, unicode):
            # in some cases field types are just a string
            class_name = field.name
            namespace = field.namespace
        else:
            class_name = field.type.name
            namespace = field.type.namespace
        clazz = getattr(dependencies[namespace], class_name)
        clazz_factory = GenericFactoryAvro.get_factory_avro(clazz, version)
        value = clazz_factory()
    elif field_type == 'array':
        value = []
        for _ in xrange(DEFAULT_ELEMENTS_ARRAY):
            if isinstance(field.type, str):
                value.append(mock_field(field.items, field.items.type, dependencies, version))
            else:
                value.append(mock_field(field.type.items, field.type.items.type, dependencies, version))
    elif field_type == 'map':
        value = {}
        for _ in xrange(DEFAULT_ELEMENTS_MAP):
            if isinstance(field.type, str):
                value[factory.fuzzy.FuzzyText().fuzz()] = \
                    mock_field(field.values, field.values.type, dependencies, version)
            else:
                value[factory.fuzzy.FuzzyText().fuzz()] = \
                    mock_field(field.type.values, field.type.values.type, dependencies, version)
    return value


class FactoryAvroMetaClass(FactoryMetaClass):
    def __new__(mcs, name, bases, attrs):
        if hasattr(attrs['Meta'], 'model'):
            version = attrs.get('_version', None)
            fuzzy_attributes = mock_schema(attrs['Meta'].model, version)
            for parent in bases:
                fuzzy_attributes.update(parent._meta.pre_declarations.declarations)
            fuzzy_attributes.update(attrs)
            attrs = fuzzy_attributes

        return super(FactoryAvroMetaClass, mcs).__new__(mcs, name, bases, attrs)


FactoryAvro = FactoryAvroMetaClass(
    str('Factory'),
    (BaseFactory,),
    {
        'Meta': BaseMeta,
        '__doc__': """Factory base with build and create support.

        This class has the ability to support multiple ORMs by using custom creation
        functions.
        """,
    }
)


class GenericFactoryAvro():

    def __init__(self):
        pass

    factory_avro_cache = {}

    @staticmethod
    def register_factory(clazz, factory, version=None):
        """

        :param clazz:
        :param factory:
        :param version:
        :return:
        """
        if version is None:
            dependency_manager = DependencyManager()
            version = dependency_manager.get_latest_version()
        # checks if the factory is already in the cache
        GenericFactoryAvro.factory_avro_cache[(clazz, version)] = factory

    @staticmethod
    def get_factory_avro(clazz, version=None):
        """
        Returns a generic factory avro to create mock objects
        :param clazz:
        :type clazz: ProtocolElement
        :param version: the package version as of the dependency manager to which the clazz corresponds
        :type version: str
        :return:
        """
        if version is None:
            dependency_manager = DependencyManager()
            version = dependency_manager.get_latest_version()
        # checks if the factory is already in the cache
        if (clazz, version) in GenericFactoryAvro.factory_avro_cache:
            return GenericFactoryAvro.factory_avro_cache[(clazz, version)]

        class ClazzFactory(FactoryAvro):
            def __init__(self, *args, **kwargs):
                ClazzFactory.super(self).__init__(*args, **kwargs)

            class Meta:
                model = clazz

            _version = version

        GenericFactoryAvro.factory_avro_cache[(clazz, version)] = ClazzFactory
        return ClazzFactory
