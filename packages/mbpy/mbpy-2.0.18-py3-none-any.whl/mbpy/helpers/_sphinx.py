import asyncio
import logging
import re
import sys
from contextlib import chdir
from inspect import cleandoc
from inspect import getdoc as inspect_getdoc
from pathlib import Path
from pydoc import getdoc as pydoc_getdoc
from pydoc import splitdoc, synopsis
from typing import Any, Dict, Tuple

from typing_extensions import Final

from mbpy.cmd import arun_command
from mbpy.collect import PathLike
# from mbpy.helpers._static import SPHINX_API, SPHINX_CONF, SPHINX_INDEX, SPHINX_MAKEFILE
from mbpy.import_utils import  smart_import
from mbpy.helpers._naming import resolve_name
visit: set = set()


CONTROL_ESCAPE: Final = {
    7: "\\a",
    8: "\\b",
    11: "\\v",
    12: "\\f",
    13: "\\r",
}


def escape_control_codes(
    text: str,
    _translate_table: Dict[int, str] = CONTROL_ESCAPE,
) -> str:
    r"""Replace control codes with their "escaped" equivalent in the given text.

    (e.g. "\b" becomes "\\b")

    Args:
        text (str): A string possibly containing control codes.

    Returns:
        str: String with control codes replaced with their escaped version.
    """
    return text.translate(_translate_table)


visit: set = set()


def first_paragraph(doc: str) -> Tuple[str, str, str]:
    """Split the docstring into the first paragraph and the rest."""
    return doc.partition("\n\n")


def prompt_ask(prompt: str, default: str = None) -> str:
    """Prompt the user for input."""
    SPINNER = smart_import("mbpy.helpers._display.SPINNER")()
    SPINNER.stop()
    Prompt = smart_import("rich.prompt.Prompt")
    return Prompt.ask(prompt, default=default, choices=["y", "n"]) == "y"


async def get_formatted_doc(obj: Any, verbose: bool = False) -> None | str:
    """Extract the docstring of an object, process it, and return it.

    The processing consists of cleaning up the docstring's indentation,
    taking only its first paragraph if `verbose` is False,
    and escaping its control codes.

    Args:
        obj (Any): The object to get the docstring from.
        verbose (bool): Whether to include the full docstring.

    Returns:
        Optional[str]: The processed docstring, or None if no docstring was found.

    """
    docs = pydoc_getdoc(obj)
    if docs is None:
        docs = inspect_getdoc(obj) or ""
    if not docs:
        return None

    docs = cleandoc(docs).strip()
    if not verbose:
        docs, _, _ = first_paragraph(docs)
    return escape_control_codes(docs)


async def brief_summary(obj: object) -> Tuple[str, str]:
    """Extract the first sentence (brief) and returns the.

    Args:
        obj (object): The object from which to extract the docstring.

    Returns:
        Tuple[str, str]: A tuple containing the summary and the remaining documentation.
                         Both elements are empty strings if no docstring is found.

    """
    doc = pydoc_getdoc(obj)
    if not doc:
        doc = inspect_getdoc(obj) or ""

    if not doc:
        # Attempt to locate the object and get a synopsis
        full_name = f"{getattr(obj, '__module__', '')}.{getattr(obj, '__qualname__', '')}"
        try:
            located = resolve_name(full_name, forceload=True)
            if located:
                if hasattr(located, "__file__"):
                    doc = synopsis(located.__file__)
                elif hasattr(obj, "__file__"):
                    doc = synopsis(obj.__file__)
        except Exception as e:
            logging.debug(f"Failed to locate synopsis for {full_name}: {e}")
            doc = ""

    if not doc:
        # Fallback to get_formatted_doc with verbose=True
        formatted_doc = await get_formatted_doc(obj, verbose=True)
        if formatted_doc:
            doc = formatted_doc

    # If doc is still empty, set to empty string to avoid None
    if not doc:
        doc = ""

    # Split the docstring into summary and remaining parts
    summary, remaining = splitdoc(doc)
    if not summary or not remaining:
        # Attempt to split manually using first_paragraph
        summary, sep, remaining = first_paragraph(doc)
        summary = summary.strip()
        remaining = remaining.strip()

    # Ensure both summary and remaining are strings
    summary = summary if summary else ""
    remaining = remaining if remaining else ""

    return summary, remaining


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def setup_sphinx_docs(
    *, docs_dir: PathLike, project_name: str, author: str, description: str, source_dir: PathLike, theme: str = "furo"
) -> None:
    """Set up Sphinx documentation."""
    logger.info(f"Setting up Sphinx documentation in {docs_dir}")
    
    docs_path = Path(docs_dir).resolve()
    source_path = Path(source_dir).resolve()
    
    try:
        # Create required directories
        templates_dir = docs_path / "_templates"
        templates_dir.mkdir(exist_ok=True, parents=True)
        api_dir = docs_path / "api"
        api_dir.mkdir(exist_ok=True, parents=True)
        static_dir = docs_path / "_static"
        static_dir.mkdir(exist_ok=True, parents=True)
        
        # Create source directory if using separate source/build
        source_dir = docs_path / "source"
        source_dir.mkdir(exist_ok=True, parents=True)

        # Write base index.rst
        index_content = f"""
{project_name}
{'=' * len(project_name)}

{description}

.. toctree::
   :maxdepth: 2
   :caption: Contents:
   :glob:

   api/*
"""
        (source_dir / "index.rst").write_text(index_content)

        # Write API index
        api_index_content = f"""
API Reference
============

.. autosummary::
   :toctree: ../_autosummary
   :template: module.rst
   :recursive:

   {project_name}
"""
        (api_dir / "index.rst").write_text(api_index_content)

        # Write conf.py with proper path handling
        conf_content = SPHINX_CONF(
            project_name=project_name,
            author=author,
            description=description,
            theme=theme,
        )
        conf_path = source_dir / "conf.py"
        conf_path.write_text(conf_content)

        # Write Makefile
        makefile_path = docs_path / "Makefile" 
        makefile_path.write_text(SPHINX_MAKEFILE)

        # Write module template
        module_template = templates_dir / "module.rst"
        module_template.write_text("""
{{ fullname | escape | underline}}

.. automodule:: {{ fullname }}
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
""")

        # Build the docs
        logger.info("Building documentation...")
        with chdir(docs_path):
            cmd = [
                sys.executable, "-m", "sphinx",
                "-b", "html",                  # Build as HTML
                "-v",                          # Be verbose
                "source",                      # Source dir
                "_build/html"                  # Output dir
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            out = stdout.decode() + "\n" + stderr.decode()
            if process.returncode != 0:
                if "No module named" in out and confirm("Sphinx and its extensions are not installed. Install now?"):
                    a = await arun_command(f"{get_executable(env)} -m pip install 'mbpy[sphinx]'")
                    await setup_sphinx_docs(
                        docs_dir=docs_dir,
                        project_name=project_name,
                        author=author,
                        description=description,
                        source_dir=source_dir,
                        theme=theme
                    )
                logger.error(f"Sphinx build failed:\n{stderr.decode()}")
                raise Exception(f"Sphinx build failed:\n{stderr.decode()}")
            
            logger.info(f"Documentation built successfully in {docs_path}/_build/html")
            return True

    except Exception as e:
        logger.error(f"Error during documentation setup: {str(e)}")
        raise


async def generate_sphinx_docs(project_dir: PathLike, docs_dir: PathLike, third_party=False) -> None:
    """Generate Sphinx-compatible `.rst` files."""
    logger.info(f"Generating Sphinx docs from {project_dir} to {docs_dir}")
    
    project_dir = Path(project_dir)
    docs_dir = Path(docs_dir)
    
    if not project_dir.exists():
        raise FileNotFoundError(f"Project directory {project_dir} does not exist")
    
    if not docs_dir.exists():
        docs_dir.mkdir(parents=True, exist_ok=True)
    # Create main index.rst
    index_rst = docs_dir / "index.rst"
    with index_rst.open("w") as f:
        f.write("Welcome to Documentation\n")
        f.write("=====================\n\n")
        f.write(".. toctree::\n")
        f.write("   :maxdepth: 2\n")
        f.write("   :caption: Contents:\n")
        f.write("   :glob:\n\n")
        f.write("   api/index\n")
        f.write("   modules/*/index\n")
    
    # Create API index
    api_dir = docs_dir / "api"
    api_dir.mkdir(exist_ok=True)
    api_index = api_dir / "index.rst"
    
    with api_index.open("w") as f:
        f.write("API Reference\n")
        f.write("=============\n\n")
        f.write(".. autosummary::\n")
        f.write("   :toctree: _autosummary\n")
        f.write("   :template: module.rst\n")
        f.write("   :recursive:\n\n")
        
        # Add all Python modules
        for py_file in project_dir.rglob("*.py"):
            if not third_party and ("venv" in str(py_file) or "site-packages" in str(py_file)):
                continue
            if py_file.stem.startswith("_"):
                continue
            module_path = str(py_file.relative_to(project_dir).with_suffix("")).replace("/", ".")
            f.write(f"   {module_path}\n")

    # Create template files
    templates_dir = docs_dir / "_templates"
    templates_dir.mkdir(exist_ok=True)
    
    # Module template
    module_template = templates_dir / "module.rst"
    module_template.write_text("""
{{ fullname | escape | underline}}

.. automodule:: {{ fullname }}
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
""")

    # Class template
    class_template = templates_dir / "class.rst" 
    class_template.write_text("""
{{ fullname | escape | underline}}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
""")

async def generate_recipe_docs(test_dir: PathLike, output_dir: PathLike, show: bool = False, third_party=False) -> None:
    """Generate recipe documentation from test files.

    Args:
        test_dir: Test files directory
        output_dir: Output documentation directory
        show: Whether to print processing information
    """
    if show:
        print(f"\nGenerating recipes from {test_dir} to {output_dir}")

    recipes_dir = output_dir / "recipes"
    recipes_dir.mkdir(parents=True, exist_ok=True)

    recipes_index = recipes_dir / "index.rst"
    with recipes_index.open("w") as index_file:
        index_file.write("Recipes\n=======\n\n")
        index_file.write(".. toctree::\n   :maxdepth: 2\n\n")

        for test_file in test_dir.rglob("test_*.py"):
            if not third_party and "venv" in str(test_file) or "site-packages" in str(test_file):
                continue
            if show:
                print(f"\nProcessing test file: {test_file}")
                print(f"File size: {test_file.stat().st_size} bytes")

            module_name = test_file.stem.replace("test_", "")
            index_file.write(f"   {module_name}\n")

            recipe_rst = recipes_dir / f"{module_name}.rst"
            with recipe_rst.open("w") as recipe_file:
                title = f"{module_name.capitalize()} Recipes"
                recipe_file.write(f"{title}\n{'=' * len(title)}\n")
                recipe_file.write(".. code-block:: python\n\n")

                with test_file.open() as tf:
                    content = tf.read()
                    if show:
                        print(f"Raw content length: {len(content)} characters")
                    cleaned = await clean_code(content)
                    if show:
                        print(f"\nCleaned content for {module_name}:")
                        print(cleaned)
                        print("-" * 80)
                    for line in cleaned.splitlines():
                        recipe_file.write(f"    {line}\n")


async def one_liner(package_name: str, openai: bool = False):
    """Generate a one-liner description for the package."""
    return await get_formatted_doc(locate(package_name), verbose=False)


async def summary(package_name: str):
    """Generate a summary for the package."""
    return await one_liner(package_name)


async def outline(package_name: str):
    """Generate an outline for the package."""
    return await one_liner(package_name)


async def clean_code(code: str) -> str:
    """Clean the test code by removing pytest imports, fixtures, mocks, and assert statements."""
    if not code.strip():
        return "No content found"

    # Remove pytest and mock imports
    code = re.sub(
        r"(^import pytest.*\n|^from pytest.*\n|^from unittest.mock.*\n|^import mock.*\n)", "", code, flags=re.MULTILINE
    )

    # Remove pytest decorators and mocks
    code = re.sub(r"(@pytest\.fixture.*\n|@mock\.patch.*\n|@patch.*\n)", "", code, flags=re.MULTILINE)

    # Remove commented sections
    code = re.sub(r"^\s*#.*\n", "", code, flags=re.MULTILINE)

    # Remove unused imports
    code = re.sub(r"(^from .*?\n|^import .*?\n)", "", code, flags=re.MULTILINE)

    # Improved function name cleaning
    code = re.sub(r"def test_(\w+)\(.*?\):", lambda m: m.group(1).replace("_", " "), code, flags=re.MULTILINE)
    code = re.sub(r"@.*\nmock\s+(\w+)", r"\1", code, flags=re.MULTILINE)  # Clean mock fixtures
    code = re.sub(r"^\s*mock\s+(\w+)\s*=", r"\1 =", code, flags=re.MULTILINE)  # Clean mock variables

    # Extract clean functions
    functions = {}
    current_fn = None
    current_body = []

    for line in code.splitlines():
        if line.strip() in ['if __name__ == "__main__":', "pytest.main([", "]):"]:
            continue
        if line.strip() and not line.strip().startswith(("assert", "pytest", "mock")):
            if line.strip() in functions.keys():
                current_fn = line.strip()
                current_body = []
            elif line[0].isupper() and line[-1] == "=":
                current_fn = line.strip("=").strip()
                current_body = []
            elif re.match(r"^[a-zA-Z][\w\s]+$", line.strip()):  # Match cleaned function names
                current_fn = line.strip()
                current_body = []
            else:
                if current_fn:
                    current_body.append(line)
                    functions[current_fn] = "\n".join(current_body).strip()

    # Format recipes
    recipe = []
    if not functions:
        return "No recipes found in this test file"

    for fn_name, fn_body in functions.items():
        if fn_body.strip():
            recipe.append(fn_name)
            recipe.append("=" * len(fn_name))
            recipe.append(fn_body.strip())
            recipe.append("")

    return "\n".join(recipe) if recipe else "No valid recipes extracted"


if __name__ == "__main__":
    from mbpy.helpers.traverse import search_children_for_file
    from mbpy.helpers._display import getconsole
    from rich.progress import Progress

    console = getconsole()
    
    # Validate project structure
    test_dir = search_children_for_file(".", cwd=Path.cwd())
    if not test_dir:
        console.print("[red]Error: Could not find project directory[/red]")
        sys.exit(1)
        
    output_dir = PathLike("docs2")

    async def main():
        with Progress() as progress:
            task1 = progress.add_task("[green]Generating Sphinx docs...", total=1)
            task2 = progress.add_task("[blue]Setting up documentation...", total=1)
            
            try:
                results = await asyncio.gather(
                    generate_sphinx_docs(test_dir, output_dir, third_party=True),
                    setup_sphinx_docs(
                        docs_dir=output_dir,
                        project_name="mbpy",
                        author="mbodiai",
                        description="build and package",
                        source_dir="mbpy"
                    ),
                    return_exceptions=True
                )
                
                for result in results:
                    if isinstance(result, Exception):
                        raise result
                
                progress.update(task1, advance=1)
                progress.update(task2, advance=1)
                
                # Verify output
                build_dir = Path(output_dir) / "build" / "html"
                if build_dir.exists() and any(build_dir.iterdir()):
                    console.print(f"[green]✓ Documentation generated successfully at {build_dir}[/green]")
                else:
                    console.print("[red]Warning: Documentation directory is empty[/red]")
                    
            except Exception as e:
                console.print(f"[red bold]Error: {str(e)}[/red bold]")
                logger.error(f"Documentation generation failed: {str(e)}", exc_info=True)
                raise

    try:
        asyncio.run(main())
    except Exception as e:
        console.print(f"[red bold]Error: {str(e)}[/red bold]")
        logger.error(f"Documentation generation failed: {str(e)}", exc_info=True)
        sys.exit(1)
