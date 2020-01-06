import json
import importlib
import os.path
import inspect
from protocols.util.singleton import Singleton

VERSION_73 = "7.3"
VERSION_70 = "7.0"
VERSION_72 = "7.2"
VERSION_61 = "6.1"
VERSION_500 = "5.0.0"
VERSION_400 = "4.0.0"
VERSION_300 = "3.0.0"
VERSION_210 = "2.1.0"


class DependencyManager:
    """
    Singleton class that reads builds.json file at the root of the project
    and provides utils for dependency management.
    """
    __metaclass__ = Singleton

    def __init__(self):
        filename = inspect.getframeinfo(inspect.currentframe()).filename
        path = os.path.dirname(os.path.abspath(filename))
        dependencies_json = "{}/../resources/builds.json".format(path)
        if not os.path.exists(dependencies_json):
            raise ValueError("Not found config file '{}'. Try running 'mvn initialize'".format(dependencies_json))
        builds = json.load(open(dependencies_json))["builds"]

        # prepares resource: version -> namespace -> python package
        self.builds = {}
        for build in builds:
            self.builds[build["version"]] = {}
            for package in build["packages"]:
                namespace = package["package"]
                _module = DependencyManager.get_python_module(package)
                self.builds[build["version"]][namespace] = _module

    def get_version_dependencies(self, version):
        if version not in self.builds:
            raise ValueError("Version {} not available in builds.json!".format(version))
        return self.builds[version]

    def get_latest_version_dependencies(self):
        latest_version = max(self.builds.keys())
        return self.builds[latest_version]

    def get_latest_version(self):
        latest_version = max(self.builds.keys())
        return latest_version

    def get_package_version(self, package, build_version):
        return self.builds[build_version][package]

    @staticmethod
    def get_python_package_name(package):
        """
        Returns the python package name built from a Gel package definition.
        :param package: the package dict
        :return: the python package name
        """
        package_base = package["python_package"]
        package_version = package["version"]
        package_name = "{}_{}".format(
            package_base,
            package_version.replace(".", "_").replace("-SNAPSHOT", "")
        )
        return package_name

    @staticmethod
    def get_python_protocol_name(build):
        version = build['version']
        return "protocol_{}".format(version.replace(".", "_").replace("-SNAPSHOT", ""))

    @staticmethod
    def get_python_module(package):
        package_name = DependencyManager.get_python_package_name(package)
        try:
            _module = importlib.import_module("protocols.{}".format(package_name))
        except: 
            # this happens during __init__ when you might not 
            # have built the other versions yet.
            _module = None  
        return _module

    @staticmethod
    def remove_hotfix_version(version):
        versions = version.split(".")
        if len(versions) < 2:
            raise ValueError("Version needs to have at least a major and minor versions")
        return ".".join(versions[0:2])
