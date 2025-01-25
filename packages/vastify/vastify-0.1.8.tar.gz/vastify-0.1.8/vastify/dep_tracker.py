import ast
import shutil
from pathlib import Path
# Python 3.8+ recommended:
import importlib.metadata as importlib_metadata
# or for older Python versions:
# import importlib_metadata


def _collect_dependencies_recursively(
    file_path: Path,
    project_root: Path,
    visited_local: set,
    external_libs: set
):
    """
    Parses the AST of `file_path`, looks for import statements, and splits them into:
    - Local modules: relative or discovered in the project.
    - External libraries: things that must be added to requirements.txt.

    Recurses into local modules as needed.
    """

    # Normalize path
    file_path = file_path.resolve()
    if file_path in visited_local:
        return  # Already processed

    visited_local.add(file_path)

    # Read/parse the AST of this file.
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source, filename=str(file_path))
    except Exception as e:
        print(f"[WARNING] Could not parse {file_path}: {e}")
        return

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            # e.g.  import tqdm, import numpy as np
            for alias in node.names:
                mod_name = alias.name
                _handle_import(
                    mod_name=mod_name,
                    level=0,
                    project_root=project_root,
                    current_file=file_path,
                    visited_local=visited_local,
                    external_libs=external_libs
                )
        elif isinstance(node, ast.ImportFrom):
            # e.g. from .test_code import test_func
            mod_name = node.module
            level = node.level  # how many dots?
            _handle_import(
                mod_name=mod_name,
                level=level,
                project_root=project_root,
                current_file=file_path,
                visited_local=visited_local,
                external_libs=external_libs
            )


def _handle_import(
    mod_name,
    level,
    project_root,
    current_file,
    visited_local,
    external_libs
):
    """
    Decide if `mod_name` is a local module or an external library, then handle accordingly.
    """
    if not mod_name:
        # "from . import something" (no module name specified). It's local if level>0, but 
        # we can't easily guess the submodules. We skip or treat as local dir if needed.
        return

    # 1) If there is a leading dot or `level` > 0 => definitely local relative import.
    if level > 0:
        local_path = _resolve_relative_import(mod_name, level, current_file, project_root)
        if local_path and local_path.is_file():
            _collect_dependencies_recursively(local_path, project_root, visited_local, external_libs)
        return

    # 2) Attempt to find as local if it exists in project structure
    local_path = _find_local_module(mod_name, project_root)
    if local_path is not None:
        # It's definitely local
        if local_path.is_file():
            _collect_dependencies_recursively(local_path, project_root, visited_local, external_libs)
        return

    # 3) Otherwise, treat as external library
    # For a statement like "import numpy as np", mod_name = "numpy"
    external_libs.add(mod_name.split('.')[0])


def _resolve_relative_import(mod_name, level, current_file, project_root):
    """
    Resolve a relative import like `from .sub import thing` or `from ..sub import thing`
    into an absolute file path within the project.
    """
    # Start from the directory of `current_file`.
    base_dir = current_file.parent

    # Move `level` times up (each dot is one parent).
    # Note that `level=1` means "from . import something" => same dir
    # "from .. import something" => one dir up, etc.
    for _ in range(level - 1):
        base_dir = base_dir.parent

    # If mod_name has subpackages (like "sub.util"), break them up 
    parts = mod_name.split(".") if mod_name else []
    resolved_path = base_dir
    for part in parts:
        resolved_path = resolved_path / part

    # Attempt .py extension
    py_file = resolved_path.with_suffix(".py")
    if py_file.is_file():
        return py_file

    # If there's an __init__.py in a directory
    if resolved_path.is_dir():
        init_file = resolved_path / "__init__.py"
        if init_file.is_file():
            return init_file

    # Could not resolve
    return None


def _find_local_module(mod_name, project_root):
    """
    Check if `mod_name` might be a local file or package in the project. 
    For example, if someone wrote "import test_code", we see if there's a `test_code.py`
    or `test_code/__init__.py` in `project_root`.
    Return a Path or None if not found.
    """
    parts = mod_name.split('.')
    potential = project_root
    for part in parts:
        potential = potential / part

    py_file = potential.with_suffix(".py")
    if py_file.is_file():
        return py_file.resolve()

    if potential.is_dir():
        init_file = potential / "__init__.py"
        if init_file.is_file():
            return init_file.resolve()

    return None




def _copy_local_files_to_output(visited_local, project_root, output_dir):
    """
    Copy each visited local .py file from project_root into output_dir, 
    but remove any usage of 'run_on_vastai' decorator or direct import references 
    so the pruned code can't recursively spawn VastAI instances.
    """
    output_base = Path(output_dir).resolve()
    output_base.mkdir(parents=True, exist_ok=True)

    for local_file in visited_local:
        # Construct the relative path from project_root
        try:
            rel_path = local_file.relative_to(project_root)
        except ValueError:
            # If local_file isn't inside project_root, skip it or handle differently
            continue

        dest_path = output_base / rel_path
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        if local_file.suffix == ".py":
            # --- Transform the Python code AST to remove run_on_vastai usage ---
            source_code = local_file.read_text(encoding="utf-8")
            transformed = _remove_run_on_vastai_decorator_and_imports(source_code)
            dest_path.write_text(transformed, encoding="utf-8")
        else:
            # For non-Python files, just copy verbatim
            shutil.copy2(local_file, dest_path)



def _remove_run_on_vastai_decorator_and_imports(source_code: str) -> str:
    """
    1) Remove any decorator that looks like '@run_on_vastai(...)' from function or class defs.
    2) Remove any import statement referencing 'run_on_vastai'.
    3) Return the modified source code as a string.
    """
    import ast

    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        # If it fails to parse, just return original
        return source_code

    class RemoveRunOnVastAi(ast.NodeTransformer):
        def visit_Import(self, node: ast.Import):
            """
            For statements like: import something, import run_on_vastai, ...
            We'll remove the alias if it's 'run_on_vastai'.
            If the statement imports only run_on_vastai, remove it entirely.
            """
            new_names = []
            for alias in node.names:
                if alias.name != "run_on_vastai":
                    new_names.append(alias)
            if not new_names:
                # means we removed all imported names => remove this import node entirely
                return None
            node.names = new_names
            return node

        def visit_ImportFrom(self, node: ast.ImportFrom):
            """
            For statements like: 
              from .decorator import run_on_vastai
              from something import run_on_vastai, something_else
            We'll remove 'run_on_vastai' from the import list. If that was the only import, remove it entirely.
            """
            new_names = []
            for alias in node.names:
                if alias.name != "run_on_vastai":
                    new_names.append(alias)
            # If all removed => remove entire node
            if not new_names:
                return None
            node.names = new_names
            return node

        def visit_FunctionDef(self, node: ast.FunctionDef):
            # Filter out any decorator that calls "run_on_vastai"
            new_decorators = []
            for decorator in node.decorator_list:
                if _is_run_on_vastai_decorator(decorator):
                    # skip it
                    continue
                new_decorators.append(decorator)
            node.decorator_list = new_decorators
            # Proceed with normal recursion
            self.generic_visit(node)
            return node

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
            # same logic for async defs
            new_decorators = []
            for decorator in node.decorator_list:
                if _is_run_on_vastai_decorator(decorator):
                    continue
                new_decorators.append(decorator)
            node.decorator_list = new_decorators
            self.generic_visit(node)
            return node

        def visit_ClassDef(self, node: ast.ClassDef):
            # same logic for classes, if you ever used run_on_vastai on a class
            new_decorators = []
            for decorator in node.decorator_list:
                if _is_run_on_vastai_decorator(decorator):
                    continue
                new_decorators.append(decorator)
            node.decorator_list = new_decorators
            self.generic_visit(node)
            return node

    transformer = RemoveRunOnVastAi()
    new_tree = transformer.visit(tree)

    # Now unparse back to string (Python 3.9+)
    try:
        import ast
        return ast.unparse(new_tree)
    except Exception:
        # If unparse fails, fallback to original code or partial
        return source_code


def _is_run_on_vastai_decorator(decorator_node: ast.expr) -> bool:
    """
    Check if a decorator node is exactly 'run_on_vastai(...)'
    or 'run_on_vastai' bare or 'some_alias.run_on_vastai(...)' etc.
    We basically look at the "func" part of the Call, or the Name itself.
    """
    # If it's just '@run_on_vastai' with no parentheses 
    # it might show up as Name(id='run_on_vastai', ...)
    if isinstance(decorator_node, ast.Name):
        return decorator_node.id == "run_on_vastai"

    # If it's a call '@run_on_vastai(...)'
    if isinstance(decorator_node, ast.Call):
        # The function part might be Name('run_on_vastai') or Attribute(...). 
        func = decorator_node.func
        # If it's a Name node
        if isinstance(func, ast.Name):
            return (func.id == "run_on_vastai")
        # If it's "something.run_on_vastai"
        elif isinstance(func, ast.Attribute):
            return (func.attr == "run_on_vastai")

    return False



def _write_requirements_txt(external_libs, output_dir, additional_reqs=None):
    """
    Create a requirements.txt listing all external modules/libraries discovered in the code,
    including the version installed in the current environment (if we can find it).
    """
    reqs_path = Path(output_dir, "requirements.txt")
    with open(reqs_path, "w", encoding="utf-8") as f:
        for lib in sorted(external_libs):
            if 'dateutil' in lib:
                continue
            # Attempt to find the installed version in the current environment
            version = _get_distribution_version(lib)
            if version is not None:
                f.write(f"{lib}=={version}\n")
        if additional_reqs:
            for lib in additional_reqs:
                f.write(f"{lib}\n")
            # Disabled for now to avoid all kinds of internal libs being written
            # else:
            #     # Fallback: just write the import name (might need manual correction if it fails)
            #     f.write(f"{lib}\n")


def _get_distribution_version(import_name):
    """
    Try to look up a version for `import_name` in the current Python environment.
    - First try a direct `importlib_metadata.version(...)`.
    - If that fails, we scan all installed distributions to see which provides this top-level module.
    """
    # Attempt direct version lookup by the same name:
    try:
        return importlib_metadata.version(import_name)
    except importlib_metadata.PackageNotFoundError:
        pass

    # Fallback: check which distribution might provide this 'top_level.txt'
    # This approach can match many straightforward cases (like `tqdm` -> `tqdm`)
    # But for more complicated cases (like `cv2` -> `opencv-python`), you might need custom logic.
    for dist in importlib_metadata.distributions():
        try:
            top_level = dist.read_text('top_level.txt')
            if top_level:
                # If import_name is listed among top-level modules of `dist`
                # compare using a set of lines (split).
                if import_name in top_level.split():
                    return dist.version
        except:
            pass

    return None
