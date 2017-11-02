#!/usr/bin/env python
import sys
import os
import logging
import argparse
try:
    import ujson as json
except:
    import json
import shutil
import distutils.dir_util
try:
    sys.path.append(os.path.dirname(os.path.join(os.path.dirname(__file__), 'resources', 'GelModelsTools')))
    from GelModelsTools import utils
    from GelModelsTools.gel_models_tools import GelModelsTools
    from protocols.util.dependency_manager import DependencyManager
except:
    logging.warning("Unmet dependencies. Not all build functionality will work")


logging.basicConfig(level=logging.DEBUG)

IDL_FOLDER = "schemas/IDLs"
JSON_FOLDER = "schemas/JSONs"
AVPR_FOLDER = "schemas/AVPRs"
JAVA_FOLDER = "target/generated-sources/java"
PYTHON_FOLDER = "protocols"
DOCS_FOLDER = "docs/html_schemas"


def __create_IDLs_build_folder(packages):
    """
    Creates the build folder for a given set of packages
    :param packages:
    :return:
    """
    __delete_IDLs_build_folder()
    build_folder = os.path.join(IDL_FOLDER, "build")
    for package in packages:
        source_folder = os.path.join(IDL_FOLDER, package["package"], package["version"])
        distutils.dir_util.copy_tree(source_folder, build_folder)
    return build_folder

def __delete_IDLs_build_folder():
    """
    Deletes the build folder
    """
    build_folder = os.path.join(IDL_FOLDER, "build")
    if os.path.exists(build_folder):
        distutils.dir_util.remove_tree(build_folder)


def __get_package_from_build(build, package_name):
    """
    Finds a package in a build by package name
    :param build:
    :param package:
    :return:
    """
    package = None
    for _package in build["packages"]:
        if _package["package"] == package_name:
            package = _package
            break
    return package


def __idl2json(input, output):
    args = [
        'resources/GelModelsTools/gel_models_tools.py',
        'idl2json',
        '--input', input,
        '--output', output
    ]
    original_args = sys.argv
    sys.argv = args
    GelModelsTools()


def __json2java(input, output):
    args = [
        'resources/GelModelsTools/gel_models_tools.py',
        'json2java',
        '--input', input,
        '--output', output
    ]
    original_args = sys.argv
    sys.argv = args
    GelModelsTools()


def __idl2json(input, output):
    args = [
        'resources/GelModelsTools/gel_models_tools.py',
        'idl2json',
        '--input', input,
        '--output', output
    ]
    original_args = sys.argv
    sys.argv = args
    GelModelsTools()


def __json2python(input, output, version):
    args = [
        'resources/GelModelsTools/gel_models_tools.py',
        'json2python',
        '--input', input,
        '--output-file', output,
        '--version', version
    ]
    original_args = sys.argv
    sys.argv = args
    GelModelsTools()


def __idl2avpr(input, output):
    args = [
        'resources/GelModelsTools/gel_models_tools.py',
        'idl2avpr',
        '--input', input,
        '--output', output
    ]
    original_args = sys.argv
    sys.argv = args
    GelModelsTools()


def __avpr2html(input, output):
    args = [
        'resources/GelModelsTools/gel_models_tools.py',
        'avpr2html',
        '--input-file', input,
        '--output', output
    ]
    original_args = sys.argv
    sys.argv = args
    GelModelsTools()

def __get_build_by_version(builds, version):
    build = None
    for _build in builds:
        if _build["version"] == version:
            build = _build
    return build


def run_build(build, skip_docs=False):
    """
    Builds a build ...
    :param build:
    :return:
    """
    version = build["version"]
    packages = build["packages"]
    # copy IDLs from specified packages in build into build folder
    build_folder = __create_IDLs_build_folder(packages)

    # generate JSON schemas
    json_build_folder = os.path.join(JSON_FOLDER, "build")
    if os.path.exists(json_build_folder):
        distutils.dir_util.remove_tree(json_build_folder)
    utils.makedir(json_build_folder)
    __idl2json(build_folder, json_build_folder)

    # generate Java source code
    if os.path.exists(JAVA_FOLDER):
        distutils.dir_util.remove_tree(JAVA_FOLDER)
    utils.makedir(JAVA_FOLDER)
    __json2java(json_build_folder, JAVA_FOLDER)

    # process each package separately now
    for package in packages:
        # fetch each package and its dependencies
        packages_to_process = [package]
        for dependency in package["dependencies"]:
            packages_to_process.append(__get_package_from_build(build, dependency))
        # copy IDLs from specified packages in build into build folder
        build_folder = __create_IDLs_build_folder(packages_to_process)

        # generate JSON schemas
        json_build_folder = os.path.join(JSON_FOLDER, "build")
        if os.path.exists(json_build_folder):
            distutils.dir_util.remove_tree(json_build_folder)
        utils.makedir(json_build_folder)
        __idl2json(build_folder, json_build_folder)

        # generate python source code
        package_name = DependencyManager.get_python_package_name(package)
        class_name = "{}.py".format(
            package_name
        )
        __json2python(json_build_folder, os.path.join(PYTHON_FOLDER, class_name), package["version"])

        if not skip_docs:
            # generate AVPR schemas
            avpr_build_folder = os.path.join(AVPR_FOLDER, "build")
            if os.path.exists(avpr_build_folder):
                distutils.dir_util.remove_tree(avpr_build_folder)
            utils.makedir(avpr_build_folder)
            __idl2avpr(build_folder, avpr_build_folder)

            # generate documentation
            docs_folder = os.path.join(DOCS_FOLDER, package["package"], package["version"])
            utils.makedir(docs_folder)
            for avpr in os.listdir(avpr_build_folder):
                __avpr2html(os.path.join(avpr_build_folder, avpr), docs_folder)

RESOURCES_FOLDER = "protocols/resources"
BUILDS_FILE = "builds.json"


def main():
    parser = argparse.ArgumentParser(
        description='GEL models build',
        usage='''build2.py [<args>]''')
    parser.add_argument('--version', help='A specific build version to run (if not provided runs all)')
    parser.add_argument('--skip-docs', action='store_true', help='Skips the documentation')
    parser.add_argument('--only-prepare-sandbox', action='store_true', help='Copies the required IDL schemas in the build folder under schemas/IDLs/build. A version must be specified')
    # parse_args defaults to [1:] for args, but you need to
    # exclude the rest of the args too, or validation will fail
    args = parser.parse_args(sys.argv[1:])

    # builds all builds or just the indicated in version parameter
    run_any = False
    builds = json.loads(open(BUILDS_FILE).read())["builds"]

    # copies builds.json into the resources folder reachable by the dependency manager
    if os.path.exists(RESOURCES_FOLDER):
        distutils.dir_util.remove_tree(RESOURCES_FOLDER)
    os.mkdir(RESOURCES_FOLDER)
    shutil.copyfile(BUILDS_FILE, "{}/{}".format(RESOURCES_FOLDER, BUILDS_FILE))

    if args.only_prepare_sandbox and args.version is None:
        raise ValueError("Please, provide a version to create the build sandbox")

    if args.only_prepare_sandbox:
        build = __get_build_by_version(builds, args.version)
        packages = build["packages"]
        # copy IDLs from specified packages in build into build folder
        __create_IDLs_build_folder(packages)
        logging.info("The build sandbox has been created under 'schemas/IDLs/build'")
    else:
        try:
            for build in builds:
                if args.version is None or build["version"] == args.version:
                    logging.info("Building build version {}".format(build["version"]))
                    run_build(build, args.skip_docs)
                    run_any = True
        finally:
            __delete_IDLs_build_folder()

        if not run_any and args.version is not None:
            raise ValueError("Provided build version does not exist [{}]".format(args.version))
        logging.info("Build/s finished succesfully!")


if __name__ == '__main__':
    main()
