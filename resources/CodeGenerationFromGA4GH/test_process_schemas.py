import os
import shutil
import os.path
from unittest import TestCase
from process_schemas import SchemaProcessor


class TestProcessSchema(TestCase):

    test_folder = './test'
    test_python_package = os.path.join(test_folder, 'test_protocols.py')
    BASE_DIR = os.path.dirname(__file__)
    AVRO_TOOLS_JAR = os.path.join(BASE_DIR, "..", "bin", "avro-tools-1.7.7.jar")

    def setUp(self):
        try:
            os.mkdir(self.test_folder)
        except OSError:
            pass
        shutil.copyfile('../../schemas/IDLs/org.gel.models.coverage.avro/0.1.0-SNAPSHOT/Coverage.avdl',
                        os.path.join(self.test_folder, 'test.avdl'))

    def tearDown(self):
        try:
            os.rmdir(self.test_folder)
        except OSError:
            pass

    def test1(self):
        args = {
            'version': '5.0.0',
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