import shutil
import sys
import os.path
from unittest import TestCase
from protocols_utils.code_generation.process_schemas import SchemaProcessor, ProtocolGenerator
import importlib


class TestProcessSchema(TestCase):

    test_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), './test')
    test_avdl = os.path.join(test_folder, "test.avdl")
    test_python_package = os.path.join(test_folder, 'protocols_test.py')
    test_import_package = os.path.join(test_folder, 'protocols_import_test')
    BASE_DIR = os.path.dirname(__file__)
    AVRO_TOOLS_JAR = os.path.join(BASE_DIR, "../..", "resources/bin", "avro-tools-1.7.7.jar")

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test1(self):
        args = {
            'version': '0.0.0',
            'outputFile': self.test_python_package,
            'verbose': False,
            'avro_tools_jar': self.AVRO_TOOLS_JAR,
            'inputSchemasDirectory': self.test_folder
        }

        instance = DictWithAttrs(args)
        schema_processor = SchemaProcessor(instance)
        schema_processor.run()

        sys.path.insert(0, self.test_folder)
        test_protocol = __import__('protocols_test')

        b = test_protocol.B()
        self.assertTrue(b.float_with_default is not None)
        self.assertTrue(b.float_without_default is None)
        self.assertTrue(b.integer_with_default is not None)
        self.assertTrue(b.integer_without_default is None)
        self.assertTrue(b.string_with_default is not None and len(b.string_with_default) > 0)
        self.assertTrue(b.string_without_default is None)
        self.assertTrue(b.string_nullable is None)

        a = test_protocol.A()
        self.assertTrue(a.just_b.float_with_default is not None)
        self.assertTrue(a.just_b.float_without_default is None)
        self.assertTrue(a.just_b.integer_with_default is not None)
        self.assertTrue(a.just_b.integer_without_default is None)
        self.assertTrue(a.just_b.string_with_default is not None)
        self.assertTrue(a.just_b.string_nullable is None)
        self.assertTrue(a.just_b.string_nullable is None)
        self.assertTrue(a.nullable_b is None)

    # def test_generate_protocol(self):
    #     shutil.rmtree(self.test_import_package, ignore_errors=True)
    #     os.mkdir(self.test_import_package)
    #     protocol_generator = ProtocolGenerator('builds.json', self.test_import_package, '6.1')
    #     protocol_generator.write()
    #
    #     sys.path.insert(0, self.test_folder)
    #     assert importlib.import_module('protocols_import_test')
    #     cva_module = importlib.import_module('protocols_import_test.cva')
    #     assert cva_module
    #     inject_class = getattr(cva_module, 'ReportedVariantInjectCancer')
    #     assert inject_class


class DictWithAttrs(object):
    def __init__(self, d):
        self.__dict__ = d
