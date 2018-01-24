import os
import sys
import shutil
import os.path
from unittest import TestCase
from process_schemas import SchemaProcessor


class TestProcessSchema(TestCase):

    test_folder = './test'
    test_avdl = os.path.join(test_folder, "test.avdl")
    test_python_package = os.path.join(test_folder, 'protocols_test.py')
    BASE_DIR = os.path.dirname(__file__)
    AVRO_TOOLS_JAR = os.path.join(BASE_DIR, "..", "bin", "avro-tools-1.7.7.jar")

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

        class DictWithAttrs(object):
            def __init__(self, d):
                self.__dict__ = d
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
