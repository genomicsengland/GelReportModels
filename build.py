#!/usr/bin/env python
from __future__ import print_function
import sys
import os
import logging
import argparse
import re
import json
import shutil
import distutils.dir_util
import protocols_utils.utils.conversion_tools as conversion_tools
from protocols_utils.utils.conversion_tools import ConversionTools
from protocols.util.dependency_manager import DependencyManager


logging.basicConfig(level=logging.DEBUG)

IDL_FOLDER = "schemas/IDLs"
JSON_FOLDER = "schemas/JSONs"
AVPR_FOLDER = "schemas/AVPRs"
JAVA_FOLDER = "target/generated-sources/java"
PYTHON_FOLDER = "protocols"
DOCS_FOLDER = "docs/html_schemas"
MODELS_DOCS_FILE = "docs/source/models.rst"


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
        logging.info("Copying '{}'...".format(source_folder))
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
    ConversionTools()


def __json2java(input, output):
    args = [
        'resources/GelModelsTools/gel_models_tools.py',
        'json2java',
        '--input', input,
        '--output', output
    ]
    original_args = sys.argv
    sys.argv = args
    ConversionTools()


def __idl2json(input, output):
    args = [
        'resources/GelModelsTools/gel_models_tools.py',
        'idl2json',
        '--input', input,
        '--output', output
    ]
    original_args = sys.argv
    sys.argv = args
    ConversionTools()


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
    ConversionTools()


def __idl2avpr(input, output):
    args = [
        'resources/GelModelsTools/gel_models_tools.py',
        'idl2avpr',
        '--input', input,
        '--output', output
    ]
    original_args = sys.argv
    sys.argv = args
    ConversionTools()


def __avpr2html(input, output):
    args = [
        'resources/GelModelsTools/gel_models_tools.py',
        'avpr2html',
        '--input-file', input,
        '--output', output
    ]
    original_args = sys.argv
    sys.argv = args
    ConversionTools()


def __build_version_package(builds_file, output, version):
    args = [
        'resources/GelModelsTools/gel_models_tools.py',
        'buildVersionPackage',
        '--builds-file', builds_file,
        '--output-dir', output,
        '--version', version
    ]
    original_args = sys.argv
    sys.argv = args
    ConversionTools()


def __get_build_by_version(builds, version):
    build = None
    for _build in builds:
        if _build["version"] == version:
            build = _build
    return build


def __update_documentation_index():
    htmls = {}
    fd = open(MODELS_DOCS_FILE, "w")
    print("GEL Models documentation", file=fd)
    print("========================", file=fd)
    print("", file=fd)
    for package in os.listdir(DOCS_FOLDER):
        print(package, file=fd)
        print("-" * len(package), file=fd)
        print("", file=fd)
        for version in os.listdir(os.path.join(DOCS_FOLDER, package)):
            print(version, file=fd)
            print("^" * len(version), file=fd)
            print("", file=fd)
            for html in os.listdir(os.path.join(DOCS_FOLDER, package, version)):

                if os.path.exists(os.path.join(IDL_FOLDER, package, version, html.replace(".html", ".avdl"))):
                    tag = "{package}{version}{name}".format(
                        package=package.replace(".", ""),
                        version=version.replace(".", "").replace("-", ""),
                        name=html.replace(".html", "")
                    )
                    htmls[tag] = (package, version, html)
                    print("* |{tag}|".format(tag=tag), file=fd)
            print("", file=fd)
        print("", file=fd)
    print("", file=fd)

    for tag, (package, version, html) in htmls.items():
        print(".. |{tag}| raw:: html".format(tag=tag), file=fd)
        print("", file=fd)
        print("    <a href=\"html_schemas/{package}/{version}/{html}\" target=\"_blank\">{name}</a>".format(
            package=package, version=version, html=html, name=html.replace(".html", "")
        ), file=fd)
    fd.close()

    # Calls Sphinx
    args = [
        'protocols_utils/utils/conversion_tools.py',
        'update_docs_index'
    ]
    original_args = sys.argv
    sys.argv = args
    ConversionTools()


def run_build(build, skip_docs=False, skip_java=False):
    """
    Builds a build ...
    :param build:
    :return:
    """
    logging.info("Building build version {}".format(build["version"]))
    version = build["version"]
    packages = build["packages"]
    # copy IDLs from specified packages in build into build folder
    build_folder = __create_IDLs_build_folder(packages)

    if not skip_java:
        # generate JSON schemas
        json_build_folder = os.path.join(JSON_FOLDER, "build")
        if os.path.exists(json_build_folder):
            distutils.dir_util.remove_tree(json_build_folder)
        conversion_tools.makedir(json_build_folder)
        __idl2json(build_folder, json_build_folder)

        # generate Java source code
        if os.path.exists(JAVA_FOLDER):
            distutils.dir_util.remove_tree(JAVA_FOLDER)
        conversion_tools.makedir(JAVA_FOLDER)
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
        conversion_tools.makedir(json_build_folder)
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
            conversion_tools.makedir(avpr_build_folder)
            __idl2avpr(build_folder, avpr_build_folder)

            # generate documentation
            docs_folder = os.path.join(DOCS_FOLDER, package["package"], package["version"])
            conversion_tools.makedir(docs_folder)
            for avpr in os.listdir(avpr_build_folder):
                __avpr2html(os.path.join(avpr_build_folder, avpr), docs_folder)

    protocol_output_dir_name = DependencyManager.get_python_protocol_name(build)
    __build_version_package(BUILDS_FILE, os.path.join(PYTHON_FOLDER, protocol_output_dir_name), version)


RESOURCES_FOLDER = "protocols/resources"
BUILDS_FILE = "builds.json"


def main():
    parser = argparse.ArgumentParser(
        description='GEL models build',
        usage='''build.py [<args>]''')
    parser.add_argument('--version', help='A specific build version to run (if not provided runs all)')
    parser.add_argument('--skip-docs', action='store_true', help='Skips the documentation')
    parser.add_argument('--update-docs-index', action='store_true', help='Updates the documentation index based on the existing documentation')
    parser.add_argument('--skip-java', action='store_true', help='Skips the generation of java source code')
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

    if not args.skip_docs:
        if os.path.exists(DOCS_FOLDER):
            distutils.dir_util.remove_tree(DOCS_FOLDER)
        conversion_tools.makedir(DOCS_FOLDER)

    if args.only_prepare_sandbox:
        build = __get_build_by_version(builds, args.version)
        packages = build["packages"]
        # copy IDLs from specified packages in build into build folder
        __create_IDLs_build_folder(packages)
        logging.info("The build sandbox has been created under 'schemas/IDLs/build'")
    else:
        try:
            if args.version:
                build = __get_build_by_version(builds, args.version)
                if build is None:
                    build = __get_build_by_version(builds, DependencyManager.remove_hotfix_version(args.version))
                    if build is None:
                        raise ValueError("Build version '{}' does not exist".format(args.version))
                run_build(build, args.skip_docs, args.skip_java)
                run_any = True
            else:
                for build in builds:
                    if args.version is None or build["version"] == args.version:
                        run_build(build, args.skip_docs, args.skip_java)
                        run_any = True
        finally:
            __delete_IDLs_build_folder()

        if args.update_docs_index:
            __update_documentation_index()

        if not run_any and args.version is not None:
            raise ValueError("Provided build version does not exist [{}]".format(args.version))
        logging.info("Build/s finished succesfully!")


if __name__ == '__main__':
    main()
