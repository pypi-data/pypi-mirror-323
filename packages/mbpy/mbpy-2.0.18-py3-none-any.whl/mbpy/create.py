import ast
import inspect
from functools import partial
from importlib import import_module
from itertools import filterfalse
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Generator, Literal, Type, TypeVar

import tomlkit
from rich.console import Console
from rich.prompt import Confirm
from tomlkit.exceptions import ParseError

from mbpy import ctx
from mbpy.collect import Path as PathLike
from mbpy.helpers._display import prompt_ask
from mbpy.helpers._sphinx import setup_sphinx_docs
from mbpy.import_utils import smart_import
from mbpy.pkg.graph import TreeNode as Node

DEFAULT_PYTHON = "3.11"
getcwd = Path.cwd
IGNORE_FILES = "venv|__pycache__|*.egg-info|*.dist-info|*.tox|*.nox|*.pytest_cache|*.mypy_cache|*.git|*.idea|*.vscode|*.pyc|*.pyo|*.pyd|*.cache|*.egg|*.eggs|*.log|*.tmp|*.swp|*.swo|*.swn|*.swo|*.swn"
WORKFLOW_UBUNTU = """name: "Ubuntu"
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: write
  pull-requests: write

jobs:
  ubuntu:
    name: ${{ matrix.os }}
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-20.04, ubuntu-latest]
        python-version: ["3.12", "3.10"]

    steps:
      - name: Checkout
        uses: actions/checkout@v3

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v3
        with:
          python-version: ${{ matrix.python-version }}


      - name: python

        steps:
          - uses: actions/checkout@v4

          - name: Install uv
            uses: astral-sh/setup-uv@v2

          - name: Set up Python ${{ matrix.python-version }}
            run: uv python install ${{ matrix.python-version }}

      - name: Cache packages
        uses: actions/cache@v3
        env:
          cache-name: cache-packages
        with:
          path: ~/.local/bin ~/.local/lib .mbodied/envs/mbodied
          key: ${{ runner.os }}-${{ env.cache-name }}-${{ hashFiles('install.bash') }}
          restore-keys: |
            ${{ runner.os }}-${{ env.cache-name }}-

      - name: Check disk usage
        run: df -h

      - name: Clean up before running tests
        run: |
          # Add commands to clean up unnecessary files
          sudo apt-get clean
          sudo rm -rf /usr/share/dotnet /etc/mysql /etc/php /etc/apt/sources.list.d
          # Add more cleanup commands as needed

      - name: Check disk usage after cleanup
        run: df -h

      - name: Install the project
        run: uv sync --all-extras --dev

      - name: Run tests
        # For example, using `pytest`
        run: uv run pytest tests"""


WORKFLOW_MAC = """name: "MacOS | Python 3.12|3.11|3.10"

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pull-requests: write

jobs:
  test:
    name: Python ${{ matrix.python-version }}
    runs-on: macos-latest
    strategy:
      matrix:
        python-version: ["3.12", "3.11", "3.10"]

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v3
        with:
          python-version: ${{ matrix.python-version }}

      - name: python

        steps:
          - uses: actions/checkout@v4

          - name: Install uv
            uses: astral-sh/setup-uv@v2

          - name: Set up Python ${{ matrix.python-version }}
            run: uv python install ${{ matrix.python-version }}


      - name: Cache packages
        uses: actions/cache@v3
        env:
          cache-name: cache-packages
        with:
          path: ~/Library/Caches/Homebrew
          key: ${{ runner.os }}-${{ env.cache-name }}-${{ hashFiles('install.bash') }}
          restore-keys: |
            ${{ runner.os }}-${{ env.cache-name }}-

      - name: Install the project
        run: uv sync --all-extras --dev

      - name: Run tests
        # For example, using `pytest`
        run: uv run pytest tests
"""

INIT_PY = """# Path: __init__.py
# This file is automatically created by mbpy.
from rich.pretty import install
from rich.traceback import install as install_traceback

install(max_length=10, max_string=80)
install_traceback(show_locals=True)
"""

API_CONTENT = """# API Reference

{description}
"""

managers = {
    "scm": {
        "requires": ["setuptools>=68", "setuptools_scm[toml]>=8"],
        "build-backend": "setuptools.build_meta",
    },
    "uv": {"requires": ["hatchling", "hatch-build-scripts"], "build-backend": "hatchling.build"},
    "hatch": {"requires": ["hatchling", "hatch-build-scripts"], "build-backend": "hatchling.build"},
}


async def mmkdir(path: str | Path) -> None:
    if not Path(str(path)).exists():
        Path(path).mkdir(parents=True, exist_ok=True)
        (Path(path) / ".gitkeep").touch()


async def maybetouch(
    path: str | Path, content: str | None = None, existing_content: Literal["merge", "replace", "forbid", "leave"] = "merge",
) -> Path | None:
    """Create a file if it doesn't exist, optionally with content.
    
    Args:
        path (str | Path): The path to the file.
        content (str | None): The content to write to the file.
        existing_content (Literal["merge", "replace", "forbid", "leave"]): How to handle existing content.
            - "merge": Append the new content to the existing content.
            - "replace": Overwrite the existing content with the new content.
            - "forbid": Raise an error if the file is not empty.
            - "leave": Do nothing if the file is not empty.
    """
    p = Path(path)
    p.touch(exist_ok=True)
    if content and existing_content == "leave":
        return None
    if content and existing_content == "forbid":
        msg = (
            f"File {path} already exists and is not empty. Use 'replace' or 'merge' to overwrite or merge the content."
        )
        raise FileExistsError(msg)
    if content and existing_content == "merge":
        content = "\n".join([*Path(path).read_text().splitlines(), *content.splitlines()])
        Path(path).write_text(content)
    Path(path).write_text(content) if content else None
    return p
T = TypeVar("T")
def walk_bfs(node: T, max_depth=0, depth=0):
    walk_children_to_depth = partial(walk, max_depth=max_depth, depth=depth+1)
    if max_depth > 0 and depth > max_depth:
        return
    yield node
    from mbpy.pkg.graph import TreeNode
    if isinstance(node, str | Path) and Path(str(node)).exists():
        yield from map(walk_children_to_depth,Path(node).iterdir())

    if isinstance(node, Node):
        yield from map(walk_children_to_depth,node.children)
    if isinstance(node, dict):
        makenode = partial(Node, parent=node)
        yield from  map(walk_children_to_depth,map(makenode, node.items()))
    if isinstance(node, ModuleType | Type):
        yield from map(walk_children_to_depth, node.__dict__.items())
    with ctx.suppress(Exception):
        if isinstance(node, str)  and (mods := ast.parse(node)):
            yield from  map(walk_children_to_depth, mods)
    with ctx.suppress(Exception):
        makenode = partial(Node, parent=node,name= node.__name__)
        if mod := import_module(node):
            yield from map(walk_children_to_depth, map(makenode, mod.__dict__.items()))
    with ctx.suppress(Exception):
        if etree := TreeNode(getattr(node,"name",str(node))):
            yield from map(walk_children_to_depth, etree.children)
    return False

def walk(node: T, ignore_pred: str | Callable[[T], bool] = IGNORE_FILES, max_depth=-1, depth=0):
    yield from filterfalse(ignore_pred, walk_bfs(node, depth=depth, max_depth=max_depth))

            

async def create_project(
    project_name: str,
    author: str,
    new: bool = False,
    description: str = "",
    dependencies: list[str] | Literal["local"] | None = None,
    python_version=DEFAULT_PYTHON,
    *,
    add_cli=False,
    autodoc="sphinx",
    project_root: Path | None = None,
) :
    if new:
        project_root = Path.cwd() / project_name
    # Set project root directory
    if project_root is None:
        project_root = Path.cwd()
    project_path = project_root
    # Create project structure
    src_dir = project_path / project_name
    src_dir.mkdir(parents=True, exist_ok=True)
    await maybetouch(src_dir / "__init__.py", INIT_PY)
    await maybetouch(
        src_dir / "__about__.py",
        f"__version__ = '0.0.1'\n__author__ = '{author}'\n__description__ = '{description}'",
        "replace",
    )
    await maybetouch(project_path / "README.md", f"# {project_name}\n\n{description}", "leave")
    # Create pyproject.toml
    pyproject_path = project_path / "pyproject.toml"
    existing_content = None
    if pyproject_path.exists():
        with pyproject_path.open() as f:
            existing_content = f.read()

    pyproject_content = await create_pyproject_toml(
        project_name,
        author,
        project_path=project_path,
        description=description,
        dependencies=dependencies if dependencies is not None else [],
        python_version=python_version,
        add_cli=add_cli,
        existing_content=existing_content,
    )
    if not pyproject_content:
        return
    pyproject_path.write_text(pyproject_content)

    # Setup documentation
    out = await setup_documentation(project_name=project_name, author=author, description=description, autodoc=autodoc, project_root=project_root)

    cli_content = ""
    if add_cli:
        cli_content = f"""
import rich_click as click

@click.command()
def main():
    click.echo(Hello from {project_name})

if __name__ == "__main__":
    main()
""" + ""
    return await maybetouch(src_dir / "cli.py", cli_content, "leave")



console = Console()
def find_readme(pu: Path = None, pd: Path = None, search_window=5) -> Path | None:
    for _ in range(search_window):
        if pu and (pu / "README.md").exists():
            return pu
        if pd and (pd / "README.md").exists():
            return pd
        if pu:
            pu = pu.parent
        if pd:
            for sub in pd.iterdir():
                if sub.is_dir():
                    found = find_readme(pu, sub)
                    if found:
                        return found
            pd = pd.parent
    
    return None
def find_pyproject(pu: Path = None, pd: Path = None,search_window=5) -> Path | None:
    for _ in range(search_window):
        if pu and (pu / "pyproject.toml").exists():
            return pu
        if pd and (pd / "pyproject.toml").exists():
            return pd
        if pu:
            pu = pu.parent
        if pd:
            for sub in pd.iterdir():
                if sub.is_dir():
                    found = find_pyproject(pu, sub)
                    if found:
                        return found
            pd = pd.parent
    return None


async def setup_documentation(
    project_name: str,
    author: str,
    description: str,
    autodoc: str = "sphinx",
    project_root: PathLike | None = None,
    search_window: int = 5,
    theme: str = "alabaster",
) -> None:
    """Set up documentation for a project."""
    pup = pdown = None
    if project_root is None:
        project_root = PathLike.cwd()
        pup = project_root
        pdown = project_root

    project_root = project_root or find_pyproject(pup, pdown)
    if not project_root:
        raise FileNotFoundError(f"Could not find project root {search_window} directories up or down.")
    console.print(f"Using project root: {project_root}...", style="bold light_goldenrod2")
    docs_dir = project_root / "docs"
    docs_dir.mkdir(exist_ok=True, parents=True)
    if docs_dir.exists() and len(list(docs_dir.iterdir())) > 0:
        resp = Confirm.ask(console=console, prompt=f"Documentation directory: {docs_dir} is not empty. Do you want to continue?")
        if not resp:
            console.print("Exiting...", style="bold blue")
    if autodoc == "sphinx":
        await setup_sphinx_docs(docs_dir=docs_dir, project_name=project_name, author=author, description=description, source_dir=project_root,theme=theme)
    elif autodoc == "mkdocs":
        setup_mkdocs(
            docs_dir,
            project_name,
            author,
            description,
            extract_docstrings(project_root),
        )
    else:
        raise ValueError("Invalid doc_type. Choose 'sphinx' or 'mkdocs'.")

def format_signature(node: ast.FunctionDef | ast.ClassDef | ast.Module) -> str:
    """Format function or class signature from AST node."""
    if isinstance(node, ast.ClassDef):
        # Handle class inheritance
        bases = []
        for base in node.bases:
            bases.append(ast.unparse(base))
        for kw in node.keywords:
            if kw.arg == 'metaclass':
                bases.append(f"metaclass={ast.unparse(kw.value)}")
        
        return str(f"({', '.join(bases)})" if bases else "")
        
    if isinstance(node, ast.FunctionDef):
        # Format arguments
        args = []
        for arg in node.args.args:
            arg_str = arg.arg
            if arg.annotation:
                arg_str += f": {ast.unparse(arg.annotation)}"
            args.append(arg_str)
        
        # Handle varargs
        if node.args.vararg:
            args.append(f"*{node.args.vararg.arg}")
        
        # Handle kwargs
        if node.args.kwonlyargs:
            if not node.args.vararg:
                args.append("*")
            for arg in node.args.kwonlyargs:
                arg_str = arg.arg
                if arg.annotation:
                    arg_str += f": {ast.unparse(arg.annotation)}"
                args.append(arg_str)
        
        # Handle kwargs
        if node.args.kwarg:
            args.append(f"**{node.args.kwarg.arg}")
        
        # Format return type
        return_str = ""
        if node.returns:
            return_str = f" -> {ast.unparse(node.returns)}"
            
        return str(f"({', '.join(args)}){return_str}")
    
    return ""
def extract_docstrings(project_path) -> dict[str, dict[str, str]]:
    project_path = Path(project_path)
    docstrings = {}

    for py_file in project_path.rglob(f"*.py | !{IGNORE_FILES} | !*//.*"):
        with Path(py_file).open() as f:
            tree: Any = None
            with ctx.suppress.logignore(SyntaxError,UnicodeError,FileNotFoundError) as e:
                tree = ast.parse(f.read(), filename=py_file)
            if e:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef | ast.ClassDef | ast.Module):
                    name = node.name if not isinstance(node, ModuleType | ast.Module) else node.__name__
                    signature = ""
                    if isinstance(node, ast.FunctionDef | ast.ClassDef):
                        signature = format_signature(node)
                    elif isinstance(node, ast.Module):
                        signature = f"module {name}"
                    cleaned_docstring = inspect.cleandoc(ast.get_docstring(node) or "")
                    docstrings[f"{py_file.stem}.{name}"] = {"signature": signature, "docstring": cleaned_docstring}
    return docstrings


def setup_mkdocs(docs_dir, project_name: str, author, description, docstrings) -> None:
    docs_dir.mkdir(exist_ok=True)
    # Create mkdocs.yml in the project root
    mkdocs_content = f"""
site_name: {project_name}
site_description: {description}
site_author: {author}

theme:
  name: material

nav:
  - Home: index.md
  - API: api.md

markdown_extensions:
  - pymdownx.highlight:
      anchor_linenums: true
  - pymdownx.inlinehilite
  - pymdownx.snippets
  - pymdownx.superfences

plugins:
  - search
  - mkdocstrings:
      default_handler: python
      handlers:
        python:
          rendering:
            show_source: true
""" + ""
    docs_dir = Path(str(docs_dir)) if docs_dir else Path("docs")
    root = Path(str(docs_dir)).parent
    (root / "mkdocs.yml").write_text(mkdocs_content)

    # Create index.md
    index_content = (
        Path("README.md").read_text() if (root / "README.md").exists() else f"# {project_name}\n\n{description}"
    )

    (docs_dir / "index.md").write_text(index_content)

    # Create api.md with extracted docstrings
    docstrings = docstrings or extract_docstrings(root)
    api_content = ""
    if docstrings:
        api_content = API_CONTENT.format(description=description)
        for full_name, docstring in docstrings.items():
            module_name, obj_name = full_name.rsplit(".", 1)
            obj_api = """## {obj_name}
```python
from {module_name} import {obj_name}
```

{docstring}

---
"""
            api_content += obj_api.format(module_name=module_name, obj_name=obj_name, docstring=docstring)
    if api_content:
        (docs_dir / "api.md").write_text(api_content)




async def create_pyproject_toml(
    project_name,
    author,
    *,
    project_path,
    description="",
    dependencies=None,
    python_version="3.10",
    add_cli=True,
    existing_content=None,
    manager="hatch",
    cython=False,
) -> str:
    """Create a pyproject.toml file."""

    if  (project_path / "pyproject.toml").exists() and not prompt_ask(f"project.toml already exists in dir: {project_path}. Do you want to continue? (y/n)"):
        
        console.print("Exiting...", style="bold blue")
        return None
    try:
        pyproject = tomlkit.parse(existing_content) if existing_content else tomlkit.document()
    except ParseError:
        pyproject = tomlkit.document()

    # Build system
    pyproject.setdefault("build-system", tomlkit.table()).update(managers[manager])
    # Project metadata
    project = pyproject.setdefault("project", tomlkit.table())
    project["name"] = project_name
    project["version"] = "0.0.1"
    project["description"] = description
    project["readme"] = "README.md"
    project["requires-python"] = f">={python_version}"
    project["authors"] = [{"name": author}]

    # Classifiers
    classifiers = tomlkit.array()
    classifiers.multiline(multiline=True)
    classifiers.extend(
        [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Developers",
            f"Programming Language :: Python :: {python_version}",
            "Programming Language :: Python :: 3 :: Only",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
    )
    project["classifiers"] = classifiers

    # Dependencies
    existing_deps = project.get("dependencies", tomlkit.array())
    new_deps = tomlkit.array()
    new_deps.multiline(multiline=True)

    # Add existing dependencies
    for dep in existing_deps:
        new_deps.append(dep)

    # Add new dependencies
    if dependencies:
        deps_to_add = dependencies if isinstance(dependencies, list) else [dependencies]
        for dep in deps_to_add:
            if dep not in new_deps:
                new_deps.append(dep)

    project["dependencies"] = new_deps

    if add_cli:
        scripts = project.setdefault("scripts", tomlkit.table())
        scripts[project_name] = f"{project_name}.cli:main"

    # Tool configurations
    tool = pyproject.setdefault("tool", tomlkit.table())
    if manager == "hatch":
        # Hatch configuration
        hatch = tool.setdefault("hatch", tomlkit.table())
        hatch["envs"] = {"default": {"dependencies": ["pytest", "pytest-cov"]}}
    elif manager == "setuptools":
        scm = tool.setdefault("setuptools_scm", tomlkit.table())
        scm["write_to"] = f"{project_name}/__version__.py"

    ruff = tool.setdefault("ruff", tomlkit.table())
    ruff["line-length"] = 120
    ruff["select"] = [
        "A",
        "COM812",
        "C4",
        "D",
        "E",
        "F",
        "UP",
        "B",
        "SIM",
        "N",
        "ANN",
        "ASYNC",
        "S",
        "T20",
        "RET",
        "SIM",
        "ARG",
        "PTH",
        "ERA",
        "PD",
        "I",
        "PLW",
    ]
    ruff["ignore"] = [
        "D105",
        "PGH004",
        "D100",
        "D101",
        "D104",
        "D106",
        "ANN101",
        "ANN102",
        "ANN003",
        "ANN204",
        "UP009",
        "B026",
        "ANN001",
        "ANN401",
        "ANN202",
        "D107",
        "D102",
        "D103",
        "E731",
        "UP006",
        "UP035",
        "ANN002",
    ]
    ruff["fixable"] = ["ALL"]
    ruff["unfixable"] = []

    ruff_format = ruff.setdefault("format", tomlkit.table())
    ruff_format["docstring-code-format"] = True
    ruff_format["quote-style"] = "double"
    ruff_format["indent-style"] = "space"
    ruff_format["skip-magic-trailing-comma"] = False
    ruff_format["line-ending"] = "auto"

    ruff_lint = ruff.setdefault("lint", tomlkit.table())
    ruff_lint_pydocstyle = ruff_lint.setdefault("pydocstyle", tomlkit.table())
    ruff_lint_pydocstyle["convention"] = "google"

    ruff_lint_per_file_ignores = ruff_lint.setdefault("per-file-ignores", tomlkit.table())
    ruff_lint_per_file_ignores["**/{tests,docs}/*"] = ["ALL"]
    ruff_lint_per_file_ignores["**__init__.py"] = ["F401"]

    tool["pytest"] = {
        "ini_options": {
            "addopts": "-m 'not network'",
            "markers": "network: marks tests that make network calls (deselect with '-m \"not network\"')",
        },
    }
    if manager in ("hatch", "uv"):
        tool.setdefault("hatchling", tomlkit.table()).setdefault("build", tomlkit.table()).setdefault(
            "hooks", tomlkit.table(),
        ).setdefault("build-scripts", tomlkit.table()).setdefault("scripts", tomlkit.table()).update(
            {
                "out_dir": "out",
                "commands": ["chmod +x build.sh && ./build.sh"],
                "artifacts": [f"~/.local/bin/{project_name}"],
            },
        )

    # Add additional Ruff configurations from the current pyproject.toml
    current_ruff = pyproject.get("tool", {}).get("ruff", {})
    for key, value in current_ruff.items():
        if key not in ruff:
            ruff[key] = value
        elif isinstance(value, list):
            ruff[key].extend([item for item in value if item not in ruff[key]])

    # Pytest configuration
    tool["pytest"] = {
        "ini_options": {
            "addopts": "--cov=src --cov-report=term-missing",
            "testpaths": ["tests"],
            "markers": [
                "network: marks tests that require network access (deselect with '-m \"not network\"')",
            ],
        },
    }

    return tomlkit.dumps(pyproject)
