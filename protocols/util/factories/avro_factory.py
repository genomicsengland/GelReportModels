import sys

import factory.fuzzy
from factory import CREATE_STRATEGY
from factory.base import FactoryMetaClass, BaseFactory, BaseMeta
from protocols.util.dependency_manager import DependencyManager

from past.builtins import basestring

BASIC_TYPES = ['null', 'boolean', 'string', 'bytes', 'int', 'long', 'float', 'double', 'enum']
COMPLEX_TYPES = ['record', 'array', 'map']
UNION_TYPE = 'union'
DEFAULT_ELEMENTS_ARRAY = 5
DEFAULT_ELEMENTS_MAP = 5
INT_MIN_VALUE = -(1 << 31)
INT_MAX_VALUE = (1 << 31) - 1
LONG_MIN_VALUE = -(1 << 63)
LONG_MAX_VALUE = (1 << 63) - 1


def mock_schema(protocol, version, fill_nullables):
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
        mock_result[field_name] = mock_field(field, field_type, dependencies, version, fill_nullables)
    return mock_result


def mock_field(field, field_type, dependencies, version, fill_nullables):
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
        if fill_nullables and len(field.type.schemas) > 1:
            value = mock_field(field.type.schemas[1], field.type.schemas[1].type, dependencies, version, fill_nullables)
        else:
            value = mock_basic_type(field.type.schemas[0], field.type.schemas[0].type)
    elif field_type in COMPLEX_TYPES:
        value = mock_complex_type(field, field_type, dependencies, version, fill_nullables)
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
        value = factory.fuzzy.FuzzyChoice([True, False])
    elif field_type == 'string':
        value = factory.fuzzy.FuzzyText()
    elif field_type == 'bytes':
        value = b'a'
    elif field_type == 'int':
        value = factory.fuzzy.FuzzyInteger(INT_MIN_VALUE, INT_MAX_VALUE)
    elif field_type == 'long':
        value = factory.fuzzy.FuzzyInteger(LONG_MIN_VALUE, LONG_MAX_VALUE)
    elif field_type in ['float', 'double']:
        value = factory.fuzzy.FuzzyFloat(sys.float_info.min)
    elif field_type == 'enum':
        if hasattr(field, 'symbols'):
            symbols = field.symbols
        else:
            symbols = field.type.symbols
        value = factory.fuzzy.FuzzyChoice(symbols)
    return value


def mock_complex_type(field, field_type, dependencies, version, fill_nullables):
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
        if isinstance(field.type, str) or isinstance(field.type, basestring):
            # in some cases field types are just a string
            class_name = field.name
            namespace = field.namespace
        else:
            class_name = field.type.name
            namespace = field.type.namespace
        clazz = getattr(dependencies[namespace], class_name)
        value = FuzzyRecord(
            clazz = clazz,
            version = version,
            fill_nullables=fill_nullables
        )
    elif field_type == 'array':
        if isinstance(field.type, str):
            values_factory = mock_field(field.items, field.items.type, dependencies, version, fill_nullables)
        else:
            values_factory = mock_field(field.type.items, field.type.items.type, dependencies, version, fill_nullables)
        value = FuzzyList(
            values_factory = values_factory,
            length = DEFAULT_ELEMENTS_ARRAY
        )
    elif field_type == 'map':
        if isinstance(field.type, str):
            values_factory = mock_field(field.values, field.values.type, dependencies, version, fill_nullables)
        else:
            values_factory = mock_field(field.type.values, field.type.values.type, dependencies, version, fill_nullables)
        value = FuzzyMap(
            keys_factory = factory.fuzzy.FuzzyText(),
            values_factory = values_factory,
            length = DEFAULT_ELEMENTS_MAP
        )
    return value


class FactoryAvroMetaClass(FactoryMetaClass):
    def __new__(mcs, name, bases, attrs):
        if hasattr(attrs['Meta'], 'model'):
            version = attrs.get('_version', None)
            fill_nullables = attrs.get('_fill_nullables', False)
            fuzzy_attributes = mock_schema(attrs['Meta'].model, version, fill_nullables)
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


class FuzzyList(factory.fuzzy.BaseFuzzyAttribute):

    def __init__(self, values_factory=None, length=5, **kwargs):
        super(FuzzyList, self).__init__(**kwargs)
        self.length = length
        if values_factory is None:
            self.values_factory = factory.fuzzy.FuzzyText()
        else:
            self.values_factory = values_factory

    def fuzz(self):
        if isinstance(self.values_factory, factory.fuzzy.BaseFuzzyAttribute):
            values = [self.values_factory.fuzz() for _ in range(self.length)]
        elif isinstance(self.values_factory, factory.declarations.LazyFunction):
            values = [self.values_factory.function() for _ in range(self.length)]
        else:
            values = [self.values_factory for _ in range(self.length)]
        return values


class FuzzyMap(factory.fuzzy.BaseFuzzyAttribute):

    def __init__(self, keys_factory=None, values_factory=None, length=5, **kwargs):
        super(FuzzyMap, self).__init__(**kwargs)
        self.length = length
        if keys_factory is None:
            self.keys_factory = factory.fuzzy.FuzzyText()
        else:
            self.keys_factory = keys_factory
        if values_factory is None:
            self.values_factory = values_factory = factory.fuzzy.FuzzyText()
        else:
            self.values_factory = values_factory

    def fuzz(self):
        if isinstance(self.values_factory, factory.fuzzy.BaseFuzzyAttribute):
            values = [self.values_factory.fuzz() for _ in range(self.length)]
        elif isinstance(self.values_factory, factory.declarations.LazyFunction):
            values = [self.values_factory.function() for _ in range(self.length)]
        else:
            values = [self.values_factory for _ in range(self.length)]
        if isinstance(self.keys_factory, factory.fuzzy.BaseFuzzyAttribute):
            keys = [self.keys_factory.fuzz() for _ in range(self.length)]
        elif isinstance(self.keys_factory, factory.declarations.LazyFunction):
            keys = [self.keys_factory.function() for _ in range(self.length)]
        else:
            keys = [self.keys_factory for _ in range(self.length)]
        return dict(zip(keys, values))


class FuzzyRecord(factory.fuzzy.BaseFuzzyAttribute):

    def __init__(self, clazz=None, version=None, fill_nullables=False, **kwargs):
        super(FuzzyRecord, self).__init__(**kwargs)
        self.clazz = clazz
        self.version = version
        self.fill_nullables = fill_nullables

    def fuzz(self):
        clazz_factory = GenericFactoryAvro.get_factory_avro(self.clazz, self.version, self.fill_nullables)
        value = clazz_factory.create()
        return value


class GenericFactoryAvro():

    def __init__(self):
        pass

    factory_avro_cache = {}

    @staticmethod
    def register_factory(clazz, factory, version=None, fill_nullables=False):
        """
        :param fill_nullables:
        :param clazz:
        :param factory:
        :param version:
        :return:
        """
        if version is None:
            dependency_manager = DependencyManager()
            version = dependency_manager.get_latest_version()
        # checks if the factory is already in the cache
        GenericFactoryAvro.factory_avro_cache[(clazz, version, fill_nullables)] = factory

    @staticmethod
    def get_factory_avro(clazz, version=None, fill_nullables=False, cache=True, **kwargs):
        """
        Returns a generic factory avro to create mock objects
        :param cache:
        :param fill_nullables:
        :param clazz:
        :type clazz: ProtocolElement
        :param version: the build version as of the dependency manager to which the clazz corresponds
        :type version: str
        :return:
        """
        dependency_manager = DependencyManager()
        if version is None:
            version = dependency_manager.get_latest_version()
        if version not in dependency_manager.builds:
            # try removing hotfix version if version is not found
            version = dependency_manager.remove_hotfix_version(version)
        if version not in dependency_manager.builds:
            raise ValueError("Not valid build version '{version}'. Use one of: {valid_versions}"
                             .format(version=version, valid_versions=", ".join(dependency_manager.builds)))
        # checks if the factory is already in the cache
        if cache and (clazz, version, fill_nullables) in GenericFactoryAvro.factory_avro_cache:
            return GenericFactoryAvro.factory_avro_cache[(clazz, version, fill_nullables)]

        class ClazzFactory(FactoryAvro):
            def __init__(self, *args, **kwargs):
                ClazzFactory.super(self).__init__(*args, **kwargs)

            class Meta:
                model = clazz
                strategy = CREATE_STRATEGY

            _version = version
            _fill_nullables = fill_nullables

        if cache:
            GenericFactoryAvro.factory_avro_cache[(clazz, version, fill_nullables)] = ClazzFactory
        return ClazzFactory
