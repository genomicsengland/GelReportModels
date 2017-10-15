import ujson
import importlib
import os.path
import inspect


VERSION_430 = "4.3.0-SNAPSHOT"
VERSION_300 = "3.0.0"
VERSION_410 = "4.1.0"

class DependencyManager:
    """
    Singleton class that reads builds.json file at the root of the project
    and provides utils for dependency management.
    """

    class __DependencyManager:

        def __init__(self):
            filename = inspect.getframeinfo(inspect.currentframe()).filename
            path = os.path.dirname(os.path.abspath(filename))
            dependencies_json = "{}/../../builds.json".format(path)
            self.builds = ujson.load(open(dependencies_json))["builds"]

            # prepares resource: version -> namespace -> python package
            self.versions = {}
            for build in self.builds:
                self.versions[build["version"]] = {}
                for package in build["packages"]:
                    namespace = package["package"]
                    _module = DependencyManager.get_python_module(package)
                    self.versions[build["version"]][namespace] = _module

        def get_version_dependencies(self, version):
            if version not in self.versions:
                raise ValueError("Version {} not available in builds.json!".format(version))
            return self.versions[version]

        def get_latest_version_dependencies(self):
            latest_version = max(self.versions.keys())
            return self.versions[latest_version]

        def get_latest_version(self):
            latest_version = max(self.versions.keys())
            return latest_version

    instance = None

    def __init__(self):
        if not DependencyManager.instance:
            DependencyManager.instance = DependencyManager.__DependencyManager()

    def __getattr__(self, name):
        return getattr(self.instance, name)

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
    def get_python_module(package):
        package_name = DependencyManager.get_python_package_name(package)
        _module = importlib.import_module("protocols.{}".format(package_name))
        return _module
