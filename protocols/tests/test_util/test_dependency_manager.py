from unittest import TestCase
from protocols.util.dependency_manager import DependencyManager
import protocols.reports_6_1_0
import protocols.reports_6_0_0
import protocols.reports_5_0_0
import protocols.reports_4_2_0
import protocols.reports_4_0_0
import protocols.reports_6_0_1


class TestDependencyManager(TestCase):

    def test_dependency_manager(self):
        dependency_manager = DependencyManager()
        assert dependency_manager is not None
        latest_dependencies = dependency_manager.get_latest_version_dependencies()
        assert isinstance(latest_dependencies, dict)
        assert latest_dependencies["org.gel.models.report.avro"] == protocols.reports_6_1_0
        dependencies_400 = dependency_manager.get_version_dependencies("4.0.0")
        assert isinstance(dependencies_400, dict)
        assert dependencies_400["org.gel.models.report.avro"] == protocols.reports_4_0_0
        assert dependencies_400["org.gel.models.report.avro"] != protocols.reports_4_2_0

    def test_generate_protocol_packageName(self):
        build = {"version": "7.0"}
        protocol_name = DependencyManager().get_python_protocol_name(build)

        self.assertEqual(protocol_name, 'protocol_7_0')
