import ast
import importlib
import os
import shutil
import sys
import subprocess
from importlib.resources import files
import glob
import click
from rich_click import RichGroup, RichCommand

def get_near_exports_from_file(file_path):
    with open(file_path, "r") as file:
        tree = ast.parse(file.read(), filename=file_path)

    near_exports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for d in node.decorator_list:
                if isinstance(d, ast.Attribute) and isinstance(d.value, ast.Name) and d.attr == 'export' and d.value.id == 'near':
                    near_exports.add(node.name)
        if isinstance(node, ast.FunctionDef) and any(isinstance(d, ast.Name) and d.id == 'near.export' for d in node.decorator_list):
            near_exports.add(node.name)

    return near_exports

def get_imports_from_file(file_path):
    """Extract imported modules from a Python file."""
    with open(file_path, "r") as file:
        tree = ast.parse(file.read(), filename=file_path)

    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module
            if module:
                imports.add(module)

    return imports

def resolve_module_path(module_name):
    """Resolve the filesystem path of a module."""
    try:
        module = importlib.import_module(module_name)
        module_path = os.path.dirname(module.__file__)
        return module_path
    except ImportError:
        return None

def get_package_paths(file_path):
    """Get paths of all packages imported by a Python file."""
    imports = get_imports_from_file(file_path)
    package_paths = {}

    for module_name in imports:
        path = resolve_module_path(module_name)
        if path:
            package_paths[module_name] = path
        else:
            click.echo(f"Warning: module {module_name} path wasn't resolved; is it not installed in the current venv?")

    return package_paths

def is_builtin_module(module_name):
    """Check if a module is built into the Python interpreter."""
    return module_name in sys.builtin_module_names

def is_externally_installed(module_name):
    """Check if a module is installed externally (via pip or similar)."""
    try:
        module = importlib.import_module(module_name)
        return hasattr(module, "__file__")  # Externally installed modules have __file__
    except ImportError:
        return False  # Module cannot be imported

def has_compiled_extensions(package_name):
    """Check if a package contains any natively compiled extensions."""
    try:
        module = importlib.import_module(package_name)
        if not hasattr(module, "__path__"):
            return False  # Single module, not a package

        for root, _, files in os.walk(module.__path__[0]):
            for file in files:
                if file.endswith((".so", ".pyd", ".dll")):
                    return True
        return False

    except ImportError:
        print(f"Package '{package_name}' could not be imported.")
        return None

def execute(cmd):
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    # popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd, universal_newlines=True)
    # popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        print(stdout_line)
        # yield stdout_line 
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)
    
def is_mpy_module(name):
    mpy_modules = [
        "array", "builtins", "json", "os", "random", "struct", "sys"
    ]
    return name in mpy_modules

def is_mpy_lib_package(name):
    mpy_lib_packages = [
        "aiohttp", "cbor2", "iperf3", "pyjwt", "requests"
    ]
    return name in mpy_lib_packages

def generate_manifest(contract_path, package_paths, manifest_path):
    mpy_stdlib_packages = [
        "binascii", "contextlib", "fnmatch", "hashlib-sha224", "hmac", "keyword", "os-path", "pprint", 
        "stat", "tempfile", "types", "warnings", "__future__", "bisect", "copy", "functools", "hashlib-sha256", 
        "html", "locale", "pathlib", "quopri", "string", "textwrap", "unittest", "zlib", "abc", "cmd", "curses.ascii", 
        "gzip", "hashlib-sha384", "inspect", "logging", "pickle", "random", "struct", "threading", "unittest-discover",
        "argparse", "collections", "datetime", "hashlib", "hashlib-sha512", "io", "operator", "pkg_resources", "shutil", 
        "tarfile", "time", "uu", "base64", "collections-defaultdict", "errno", "hashlib-core", "heapq", "itertools", "os", 
        "pkgutil", "ssl", "tarfile-write", "traceback", "venv"
    ]
    with open(manifest_path, "w") as o:
        o.write("# THIS FILE IS GENERATED, DO NOT EDIT\n\n")
        for module in mpy_stdlib_packages:
            o.write(f"require(\"{module}\")\n")
        o.write(f"module(\"typing.py\", base_path=\"$(PORT_DIR)/extra/typing\")\n")
        o.write(f"module(\"typing_extensions.py\", base_path=\"$(PORT_DIR)/extra/typing\")\n")
        for module, path in package_paths.items():
            if is_mpy_lib_package(module):
                o.write(f"require(\"{module}\")\n")
            elif not is_mpy_module(module):
                if has_compiled_extensions(module):
                    print(f"Warning: module {module} has compiled extension, which are not currently supported\n")
                o.write(f"package(\"{module}\", base_path=\"{os.path.dirname(path)}\")\n")
        o.write(f"module(\"{os.path.basename(contract_path)}\", base_path=\"{os.path.dirname(contract_path)}\")\n")

def generate_export_wrappers(py_filename, exports, export_wrappers_path):
    with open(export_wrappers_path, "w") as o:
        o.write("/* THIS FILE IS GENERATED, DO NOT EDIT */\n\n")
        o.write("void run_frozen_fn(const char *file_name, const char *fn_name);\n\n")
        for export in exports:
            o.write(f"void {export}() \u007b\n  run_frozen_fn(\"{os.path.basename(py_filename)}\", \"{export}\");\n\u007d\n\n");

def get_venv_package_paths(file_path, venv_path):
    """Get paths of all packages imported by a Python file."""
    imports = get_imports_from_file(file_path)
    package_paths = {}

    for module_name in imports:
        # todo: maybe look the venv's current python version and use that instead of globbing
        paths = glob.glob(f"{venv_path}/lib/python*.*/site-packages/{module_name}")
        if len(paths) == 0:
            click.echo(f"Warning: module {module_name} path wasn't resolved; is it installed in the current venv at {venv_path}?")
        elif len(paths) > 1:
            click.echo(f"Warning: module {module_name} has multiple candidate paths: {paths}")
        for path in paths:
            package_paths[module_name] = path

    return package_paths

def do_build(project_dir, rebuild_all):
    project_dir = os.path.abspath(project_dir)
    project_name = os.path.basename(project_dir)
    contract_path = os.path.abspath(f"{project_dir}/contract.py")
    if not os.path.isfile(contract_path):
        click.echo(click.style(f"Error: contract file {contract_path} doesn't exist", fg='bright_red'))
        return
    
    # todo: check for uv and emcc presence and offer installation if missing

    click.echo(f"Running `uv sync` in {project_dir}...")
    execute(["uv", "sync", "--directory", project_dir])

    package_paths = get_venv_package_paths(contract_path, f"{project_dir}/.venv")
    build_path = os.path.abspath(f"{project_dir}/build")
    mpy_port_path = files('near_py_tool') / 'assets' / 'micropython' / 'ports' / 'webassembly-near'

    if rebuild_all:
      try:
        shutil.rmtree(build_path)
      except Exception:
        pass

    os.makedirs(build_path, exist_ok=True)

    for module, path in package_paths.items():
        print(f"Module: {module}, Path: {path}, has_compiled_extensions: {has_compiled_extensions(module)}, is_builtin_module: {is_builtin_module(module)}, is_externally_installed: {is_externally_installed(module)}")

    exports = list(get_near_exports_from_file(contract_path))
    print(f"exports: {exports}")
    print(f"sys.builtin_module_names: {sys.builtin_module_names}")

    generate_manifest(contract_path, package_paths, f"{build_path}/manifest.py")
    generate_export_wrappers(contract_path, exports, f"{build_path}/export_wrappers.c")
    try:
      os.unlink(f"{build_path}/frozen_content.c")  # force frozen content rebuilt every time
    except Exception:
      pass

    contract_wasm_path = f"{build_path}/{project_name}.wasm"

    # todo: make contract wasm name the same as the project name
    execute(["make", "-C", mpy_port_path, 
            #  "V=1", 
             f"BUILD={build_path}",
             f"FROZEN_MANIFEST={build_path}/manifest.py",
             f"EXPORTED_FUNCTIONS={','.join(['_' + e for e in exports])}",
             f"OUTPUT_WASM={contract_wasm_path}"])
             
    # execute(["make", "-C", "./build/micropython/ports/webassembly-near", "V=1", f"EXPORTED_FUNCTIONS={','.join(['_' + e for e in exports])}"])

    click.echo(f"Contract WASM file was build successfully and is located at {contract_wasm_path}")

@click.command(cls=RichCommand)
@click.argument('project-dir', default='.')
@click.option('--rebuild-all', is_flag=True, help="Rebuild everything from scratch")
def non_reproducible_wasm(project_dir, rebuild_all):
    """Fast and simple (recommended for use during local development)"""
    do_build(project_dir, rebuild_all)

@click.command(cls=RichCommand)
@click.argument('project-dir', default='.')
@click.option('--rebuild-all', is_flag=True, help="Rebuild everything from scratch")
def reproducible_wasm(project_dir, rebuild_all):
    """Requires `[reproducible_build]` section in pyproject.toml, and all changes committed to git (recommended for the production release)"""
    do_build(project_dir, rebuild_all)

@click.group(cls=RichGroup)
def build():
    """Build a NEAR contract with embedded ABI"""
    pass

build.add_command(non_reproducible_wasm)
build.add_command(reproducible_wasm)
