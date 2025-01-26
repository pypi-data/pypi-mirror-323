# Core imports needed for basic CLI functionality
import rich_click as click
from typing_extensions import TYPE_CHECKING

from mbpy import log
from mbpy.cli import base_args, cli, process_tasks
from mbpy.import_utils import smart_import

if TYPE_CHECKING:
    import logging
    import traceback
    from pathlib import Path
    from typing import (
        TYPE_CHECKING,
        AsyncIterator,
        Iterable,
        Literal,
    )

    import rich_click as click

    from mbpy.collect import PathType
    from mbpy.pkg.dependency import Dependency


@cli.command("install", no_args_is_help=True)
@click.argument("packages", nargs=-1, required=False, default=None)
@click.option(
    "-r",
    "--requirements",
    type=click.Path(exists=True),
    help="Install packages from the given requirements file",
)
@click.option("-U", "--upgrade", is_flag=True, help="Upgrade the package(s)")
@click.option(
    "-e",
    "--editable",
    is_flag=True,
    help="Install a package in editable mode",
)
@click.option(
    "-g",
    "--group",
    default="dependencies",
    help="Specify the dependency group to use",
)
@click.option("-d", "--debug", is_flag=True, help="Enable debug logging")
@click.option(
    "-b",
    "--broken",
    type=click.Choice(["skip", "ask", "repair"]),
    default="skip",
    help="Behavior for broken packages",
)
async def install_command(
    packages=None,
    requirements=None,
    upgrade=False,
    editable=False,
    env=None,
    group=None,
    *,
    debug=False,
    broken:'Literal["skip", "ask", "repair"]',
) -> None:
    """Install packages and update requirements.txt and pyproject.toml accordingly.

    Args:
        packages (tuple): Packages to install.
        requirements (str, optional): Requirements file to install packages from. Defaults to None.
        upgrade (bool, optional): Upgrade the package(s). Defaults to False.
        editable (bool, optional): Install a package in editable mode. Defaults to False.
        env (str, optional): The Hatch environment to use. Defaults to "default".
        group (str, optional): The dependency group to use. Defaults to "dependencies".
        debug (bool, optional): Enable debug logging. Defaults to False.
        broken (Literal["skip", "ask", "repair"], optional): Behavior for broken packages. Defaults to "skip".

    """
    await _install_command(
        packages, requirements, upgrade=upgrade, editable=editable, env=env, group=group, debug=debug, broken=broken,
    )



async def install_pip(
    executable: "PathType",
    packages: "Iterable[Dependency]",
    requirements: "str | PathType | None" = None,
    upgrade: bool = False,
    editable: bool = False,
    group: str | None = None,
    dev: bool = False,
) -> 'AsyncIterator':
    """Construct pip install command."""
    if TYPE_CHECKING:
        import asyncio
        from itertools import chain

        from rich.progress import (
            Progress,  # Updated import
            SpinnerColumn,
            TimeElapsedColumn,
        )

        from mbpy.cmd import arun, arun_command
        from mbpy.pkg.dependency import Dependency
        from mbpy.pkg.requirements import aget_requirements_file, aget_requirements_packages
    else:
        aget_requirements_file = smart_import("mbpy.pkg.requirements.aget_requirements_file")
        from rich.progress import Progress  # Updated import

        Dependency = smart_import("mbpy.pkg.dependency.Dependency")
        aget_requirements_packages = smart_import("mbpy.pkg.requirements.aget_requirements_packages")
        chain = smart_import("itertools.chain")
        log = smart_import("mbpy.log")
        log.debug(f"packages: {packages}")
        arun_command = smart_import("mbpy.cmd.arun_command")
        arun = smart_import("mbpy.cmd.arun")
        TimeElapsedColumn = smart_import("rich.progress.TimeElapsedColumn")
        SpinnerColumn = smart_import("rich.progress.SpinnerColumn")
        console = smart_import("mbpy.helpers._display.getconsole")()
        time = smart_import("time")
        asyncio = smart_import("asyncio")

    if requirements:
        requirements = await aget_requirements_file(requirements)
        requirements = await aget_requirements_packages(requirements=requirements)

    requirements = requirements or []
    packages = packages or []

    if not requirements and not packages:
        raise ValueError("No packages or requirements file provided.")

    packages = [Dependency(pkg) for pkg in chain(requirements, packages) if pkg is not None]
    editable = "-e" if editable else ""
    upgrade = "-U" if upgrade else ""
    group = f"--optional {group or dev}" if group or dev else ""
    SPINNER = smart_import("mbpy.helpers._display.SPINNER")()
    SPINNER.stop()
    with Progress() as progress:

        ts = [progress.add_task(f"[green]Downloading {p.install_cmd}", total=None) for p in packages]

        async def install(t, p):
            await p.install()
            return t

        while not progress.finished:
            async for t in process_tasks(
                [install(t, p) for t, p in zip(ts, packages, strict=False)],
            ):
                if has_failure(t):
                    progress.console.print(f"Error: {t}", style="bold red")
                progress.update(t, completed=1)
                yield t
            return


@cli.command("time", no_args_is_help=True)
@click.argument("command", nargs=-1)
@base_args()
async def time_command(command):
    """Execute a shell command asynchronously and print its execution time."""
    shlex = smart_import("shlex")
    time = smart_import("time")
    create_subprocess_exec = smart_import("asyncio.subprocess.create_subprocess_exec")
    PIPE = smart_import("asyncio.subprocess.PIPE")
    console = smart_import("mbpy.helpers._display.getconsole")()
    if not command:
        click.echo("Please provide a command to run.")
        return

    command_str = " ".join(command)
    args = shlex.split(command_str)

    start_time = time.perf_counter()

    process = await create_subprocess_exec(*args, stdout=PIPE, stderr=PIPE)

    stdout, stderr = await process.communicate()
    end_time = time.perf_counter()

    elapsed_time = end_time - start_time
    console.print(f"Command: {command_str}")
    console.print(f"Elapsed Time: {elapsed_time:.2f} seconds")

    if stdout:
        console.print(f"Output:\n{stdout.decode()}")
    if stderr:
        console.print(f"Output:\n{stdout.decode()}")


async def update_pyproject_toml(
    packages: "Iterable[Dependency]",
    env: str | None = None,
    group: str | None = None,
) -> None:
    """Update pyproject.toml with installed packages."""
    modify_pyproject = smart_import("mbpy.pkg.mpip.modify_pyproject")

    console = smart_import("mbpy.helpers._display.getconsole")()
    console.print("Updating pyproject.toml with installed packages...")
    console.print("\n")

    await modify_pyproject(
        package=packages,
        action="install",
        env=env,
        group=group,
    )


async def _install_command(
    packages: str | list[str],
    requirements_file: "PathType | None" = None,
    *,
    upgrade: bool = False,
    editable: bool = False,
    env: str | None = None,
    group: str | None = "dependencies",
    debug: bool = False,
    broken: 'Literal["ask", "repair", "skip"]' = "skip",
) -> None:
    """Install command handler."""
    get_executable = smart_import("mbpy.helpers._env.get_executable")
    traceback = smart_import("traceback")
    from mbpy.helpers._display import getconsole

    console = getconsole()
    import sys

    if sys.flags.debug or debug:
        log.debug().set()

    executable = get_executable(env)

    try:
        async for _ in install_pip(
            executable,
            packages=packages,
            requirements=requirements_file,
            upgrade=upgrade,
            editable=editable,
            group=group,
        ):
            pass

    except FileNotFoundError as e:
        console.print(f"File not Found Error: {e}", style="bold red")
    except Exception as e:
        traceback.print_exc()
        console.print(f"Unexpected error: {e}", style="bold red")
        if debug:
            raise


@cli.command("uninstall", no_args_is_help=True)
@click.argument("packages", nargs=-1)
@click.option("--env", default=None, help="Specify the Hatch environment to use")
@click.option(
    "-g",
    "--group",
    default="dependencies",
    help="Specify the dependency group to use",
)
@click.option("-d", "--debug", is_flag=True, help="Enable debug logging")
async def uninstall_command(packages, env, group, debug) -> None:
    """Uninstall packages and update requirements.txt and pyproject.toml accordingly.

    Args:
        packages (tuple): Packages to uninstall.
        env (str, optional): The Hatch environment to use. Defaults to "default".
        group (str, optional): The dependency group to use. Defaults to "dependencies".
        debug (bool, optional): Enable debug logging. Defaults to False.

    """
    await _uninstall_command(packages, env, group, debug=debug)


async def _uninstall_command(packages, env, group, *, debug=False) -> None:
    if not TYPE_CHECKING:
        modify_requirements = smart_import("mbpy.pkg.mpip.modify_requirements")
        afind_toml_file = smart_import("mbpy.pkg.toml.afind_toml_file")
        modify_pyproject = smart_import("mbpy.pkg.mpip.modify_pyproject")
        arun_command = smart_import("mbpy.cmd.arun_command")
        get_executable = smart_import("mbpy.helpers._env.get_executable")
        console = smart_import("mbpy.helpers._display.getconsole")()
        subprocess = smart_import("subprocess")
        Text = smart_import("rich.text.Text")
        Traceback = smart_import("rich.traceback.Traceback")
        compose = smart_import("mbpy.collect.compose")
        Dependency = smart_import("mbpy.pkg.dependency.Dependency")
        sys = smart_import("sys")
        partial = smart_import("functools.partial")
        log = smart_import("mbpy.log")
    else:
        from functools import partial

        from rich.text import Text

        from mbpy import log
        from mbpy.cmd import arun_command
        from mbpy.collect import compose
        from mbpy.helpers._env import get_executable
        from mbpy.pkg.dependency import Dependency
        from mbpy.pkg.mpip import modify_pyproject, modify_requirements
        from mbpy.pkg.toml import afind_toml_file

    if sys.flags.debug or debug:
        log.debug()
    for package in packages:
        package_name = Dependency(package).base

        try:
            await modify_requirements(package_name, action="uninstall")
            await modify_pyproject(
                package=package_name,
                action="uninstall",
                env=env,
                group=group,
                pyproject_path=await afind_toml_file(),
            )
            print_success = None
            console.print(f"Uninstalling {package_name}...")
            warning = False
            async for line in await arun_command(
                [get_executable(env) or "python3", "-m", "pip", "uninstall", "-y", package_name],
            ):
                console.print(Text.from_ansi(line), end="")
                if "WARNING" in line or "warning" in line.lower() or "error" in line.lower():
                    warning = True
                print_success = (
                    partial(compose(console.print, Text.from_ansi), f"\nSuccessfully uninstalled {package_name}")
                    if "WARNING" not in line
                    else None
                )
            print_success() if print_success and not warning else None
        except subprocess.CalledProcessError as e:
            console.print(f"Error: Failed to uninstall {package_name}.", style="bold red")
            console.print(f"Error: {e}")
            sys.exit(e.returncode)
        except Exception as e:
            console.print(f"Error: Failed to uninstall {package_name}.", style="bold red")
            import traceback

            from mbpy import log
            traceback.print_exc()
            log.error(f"Error: {e}")
            


@cli.command("show", no_args_is_help=False)
@click.argument("package", type=str, default=None, required=False)
@base_args
async def show_command(package=None, **kwargs):
    """Show the dependencies from the pyproject.toml file.

    Args:
        package (str, optional): The package to show information about. Defaults to None.
        env (str, optional): The Hatch environment to use. Defaults to "default".
        debug (bool, optional): Enable debug logging. Defaults to False.

    """
    if TYPE_CHECKING:
        from mbpy.helpers._show import _show_command
    else:
        _show_command = smart_import("mbpy.helpers._show._show_command")
    env = kwargs.get("env")
    await _show_command(package, env=env, debug=kwargs.get("debug", False))


INFO_KEYS = [
    "author",
    "author_email",
    "bugtrack_url",
    "classifiers",
    "description",
    "description_content_type",
    "docs_url",
    "download_url",
    "downloads",
    "dynamic",
    "home_page",
    "keywords",
    "license",
    "maintainer",
    "maintainer_email",
    "name",
    "package_url",
    "platform",
    "project_url",
    "project_urls",
    "provides_extra",
    "release_url",
    "requires_dist",
    "requires_python",
    "summary",
    "version",
    "yanked",
    "yanked_reason",
]
ADDITONAL_KEYS = ["last_serial", "releases", "urls", "vulnerabilities"]


@cli.command("search", no_args_is_help=True)
@click.argument("package", type=str, nargs=-1)
@click.option("--limit", default=10, help="Limit the number of results")
@click.option("--sort", default="downloads", help="Sort key to use")
@click.option(
    "-i",
    "--include",
    multiple=True,
    type=click.Choice(["all"] + INFO_KEYS + ADDITONAL_KEYS),
    default=None,
    help="Include additional information",
)
@click.option("--release", default=None, help="Release version to use")
@click.option("-d", "--debug", is_flag=True, help="Enable debug logging")
async def search_command(package, limit, sort, include, release, debug) -> None:
    """Find a package on PyPI and optionally sort the results.

    Args:
        package (str): The package to search for.s
        limit (int, optional): Limit the number of results. Defaults to 5.
        sort (str, optional): Sort key to use. Defaults to "downloads".
        include (str, optional): Include pre-release versions. Defaults to None.
        release (str, optional): Release type to use. Defaults to None.
        debug (bool, optional): Enable debug logging. Defaults to False.

    """
    if TYPE_CHECKING:
        import asyncio
        import logging
        import traceback

        from mrender.md import Markdown

        from mbpy.helpers._display import getconsole
        from mbpy.pkg.pypi import find_and_sort

        console = getconsole()
    else:
        traceback = smart_import("traceback")
        console = smart_import("mbpy.helpers._display.getconsole")()
        logging = smart_import("logging")
        asyncio = smart_import("asyncio")
        Markdown = smart_import("mrender.md.Markdown")
        find_and_sort = smart_import("mbpy.pkg.pypi.find_and_sort")

        SPINNER = smart_import("mbpy.helpers._display.SPINNER")()
    if not isinstance(package, str):
        package = " ".join(package)
    try:
   
        async for pkg in find_and_sort(package, limit=limit, sort=sort, include=include, release=release):
            md = Markdown(pkg)
            if debug:
                logging.debug(pkg)
            SPINNER.stop()
            md.stream()
    except KeyboardInterrupt:
        console.print("Search cancelled.", style="bold red")
    except Exception:
        traceback.print_exc()


@cli.command("", no_args_is_help=True)
@click.argument("packages", nargs=-1)
@click.option("--env", default=None, help="Specify the python, hatch, conda, or mbnix environment")
@click.option("-g", "--group", default=None, help="Specify the dependency group to use")
async def _search(packages, env, group, debug=False, console=None, arun=None):
    """Search for a package on PyPI or GitHub and optionally install it."""
    if TYPE_CHECKING:
        from mbpy.cmd import arun
        from mbpy.helpers._display import getconsole

        console = getconsole()
        from rich.text import Text

        from mbpy.cli import get_executor
        from mbpy.helpers._display import confirm, display_similar_repos_table, prompt_ask
        from mbpy.pkg.git import suggest_similar
    else:
        sys = smart_import("sys")
        arun = arun or smart_import("mbpy.cmd.arun")
        console = console or smart_import("mbpy.helpers._display.getconsole")()
        prompt_ask = smart_import("mbpy.helpers._display.prompt_ask")
        confirm = smart_import("mbpy.helpers._display.confirm")
        Text = smart_import("rich.text.Text")
        suggest_similar = smart_import("mbpy.pkg.git.suggest_similar")
        get_executor = smart_import("mbpy.cli.get_executor")

    if sys.flags.debug or debug:
        logging.basicConfig(level=logging.DEBUG, force=True)
    
    async def worker(p):
        results = await suggest_similar(p)
        if results:
            display_similar_repos_table(results, console=console)

            choices = [r["name"] for r in results]
            prompt_text = "Pick a package to install:"
            resp = prompt_ask(prompt_text, list(enumerate(choices)))
            if resp:
                from mbpy.pkg.git import clone_repo

                if resp:
                    await clone_repo(
                        results[[r["name"] for r in results].index(resp)].get("url", "github_url"),
                    )
    with get_executor("as_completed") as ex:
        ex.map(worker, packages)

@cli.command("info", no_args_is_help=True)
@click.argument("package")
@click.option("--verbose", "-v", is_flag=True, help="Show verbose output")
async def info_command(package, verbose) -> None:
    """Get information about a package from PyPI."""
    if not TYPE_CHECKING:
        Markdown = smart_import("mrender.md.Markdown")
        get_package_info = smart_import("mbpy.pkg.pypi.get_package_info")
    else:
        from mrender.md import Markdown

        from mbpy.pkg.pypi import get_package_info

    try:
        package_info = await get_package_info(package, verbose)
        md = Markdown(package_info)
        md.stream()
    except Exception:
        import traceback
        traceback.print_exc()


@cli.command("create", no_args_is_help=True)
@click.argument("project_name")
@click.argument("author")
@click.option("-n", "--new", is_flag=True)
@click.option("--description", default="", help="Project description")
@click.option("--deps", default=None, help="Dependencies separated by commas")
@click.option("--python", default="3.11", help="Python version to use")
@click.option("--no-cli", is_flag=True, help="Do not add a CLI")
@click.option("--autodoc", type=click.Choice(["sphinx", "mkdocs"]), default="sphinx", help="Documentation type to use")
async def create_command(
    project_name, author, new, description, deps: str, python="3.11", no_cli=False, autodoc="sphinx",
) -> None:
    """Create a new Python project. Optionally add dependencies and a CLI."""
    if not TYPE_CHECKING:
        create_project = smart_import("mbpy.create.create_project")
        safe_print = smart_import("mbpy.helpers._display.safe_print")
    else:
        from mbpy.create import create_project
        from mbpy.helpers._display import safe_print
    python_version = python

    try:
        if deps:
            deps = deps.split(",")
        out = await create_project(
            project_name=project_name,
            author=author,
            new=new,
            description=description,
            python_version=python_version,
            dependencies=deps,
            add_cli=not no_cli,
            autodoc=autodoc,
        )
        if out:
           safe_print(f"Project {project_name} created successfully.", style="bold light_goldenrod2")
    except Exception:
        import traceback

        traceback.print_exc()


@cli.command("bump")
@click.option("--major", is_flag=True, help="Bump the major version")
@click.option("--minor", is_flag=True, help="Bump the minor version")
@click.option("--patch", is_flag=True, help="Bump the patch version")
@click.option("-d", "--debug", is_flag=True, help="Enable debug logging")
async def bump_command(major=False, minor=False, patch=True, debug=False) -> None:
    """Bump the version of a package."""
    mbpy = smart_import("mbpy")

    if debug:
        logging = smart_import("logging")
        logging.basicConfig(level=logging.DEBUG, force=True)
    bump_pkg = smart_import("mbpy.pkg.bump.bump")
    try:
        await bump_pkg(major=major, minor=minor, patch=patch)
    except Exception:
        import traceback

        traceback.print_exc()




@cli.command("build", no_args_is_help=True)
@click.argument("path", default=".", required=False)
@base_args(env=False)
async def build_command(path) -> None:
    """Cythonize and build a package."""
    await _build_command(path)

async def _build_command(path: 'Path' = ".", env=None) -> None:
    """Cythonize and build a package."""
    if TYPE_CHECKING:
        from pathlib import Path

        from more_itertools import unique_everseen
        from rich.live import Live
        from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn

        from mbpy.helpers._display import SPINNER, getconsole, prompt_ask
        from mbpy.helpers._env import get_executable
        from mbpy.pkg.directive import add_auto_cpdef_to_package
        spinner = SPINNER()
        console = getconsole()
        
    else:
        Path = smart_import("pathlib.Path")
        Progress = smart_import("rich.progress.Progress")
        SpinnerColumn = smart_import("rich.progress.SpinnerColumn")
        TimeElapsedColumn = smart_import("rich.progress.TimeElapsedColumn")
        Live = smart_import("rich.live.Live")
        console = smart_import("mbpy.helpers._display.getconsole")()
        tomlkit = smart_import("tomlkit")
        unique_everseen = smart_import("more_itertools.unique_everseen")
        prompt_ask = smart_import("mbpy.helpers._display.prompt_ask")
        spinner = smart_import("mbpy.helpers._display.SPINNER")()
        tomlkit = smart_import("tomlkit")
    try:

        path = Path(str(path))
        spinner.stop()
        with Progress() as progress:
            # Setup task
            setup_task = progress.add_task("[cyan]Setting up build environment...", total=100)
            
            # Initialize build environment
            out = path / "tmp" / path.name
            out.mkdir(parents=True, exist_ok=True)
            
            # Copy source files with cpdef injection
            progress.update(setup_task, description="[cyan]Preprocessing source files...")
            add_auto_cpdef_to_package = smart_import("mbpy.pkg.directive.add_auto_cpdef_to_package")
            add_auto_cpdef_to_package(path, out,progress=progress)
            exit()
            # Configure build settings
            progress.update(setup_task,  description="[cyan]Configuring build settings...")
            pyproject = tomlkit.loads((path / "pyproject.toml").read_text())
            
            # Update build requirements
            progress.update(setup_task, description="[cyan]Updating build requirements...")
            bsr = pyproject.setdefault("build-system", {}).setdefault("requires", [])
            bsr = unique_everseen(bsr + ["setuptools", "wheel"])
            pyproject["build-system"]["requires"] = list(bsr)

            # Verify and update build backend
            progress.update(setup_task, advance=20, description="[cyan]Verifying build configuration...")
            if pyproject["build-system"]["build-backend"] != "setuptools.build_meta":
                y = prompt_ask(
                    "Build backend not set to setuptools. Configure it now?",
                    choices=["y", "n", "explain"],
                    default="y",
                )
                if y == "explain":
                    console.print(
                        "\n".join([
                            f"Current build backend: {pyproject['build-system']['build-backend']}",
                            "",
                            "Setuptools is the recommended build backend for Cython projects because:",
                            "1. It has mature Cython support built-in",
                            "2. It handles extension modules reliably across platforms", 
                            "3. It's well-tested with most Python packaging tools",
                            "",
                            "A temporary setup.py will be created to ensure proper Cython compilation.",
                        ]),
                    )
                if prompt_ask("Continue?", choices=["y", "n"], default="y") == "y":
                    pyproject["build-system"]["build-backend"] = "setuptools.build_meta"
                    (path / "pyproject.toml").write_text(tomlkit.dumps(pyproject))


            progress.update(setup_task, description="[cyan]Compiling package...")

            progress.stop()
        from mbpy.helpers._setup_py import setup_command
        build_result = await setup_command(path, build=True,progress=progress)

        if not build_result.status:
            console.print(f"[red]Build failed:[/red]\n{build_result.err}")
            return

        # Install if build succeeded
        progress.update(setup_task, description="[green]Installing package...")
        get_executable = smart_import("mbpy.helpers._env.get_executable")
        arun = smart_import("mbpy.cmd.arun")
        await arun(f"{get_executable(env)} -m pip install -e {str(path)}", show=True)
        

    except Exception as e:
        console.print(f"[red]Build failed:[/red] {str(e)}")
        import traceback
        traceback.print_exc()



@cli.command("sync")
@click.option("--branch", "-b", default="main", help="Branch to push to")
@click.option("-r","remote", default=None)
@base_args
async def sync_command(branch="main", remote=None, **kwargs) -> None:
    if TYPE_CHECKING:
        from mbpy.cmd import arun, arun_command
        from mbpy.helpers._display import safe_print
        from mbpy.pkg.git import push as push_project
        from mbpy.pkg.toml import afind_toml_file
    else:
        push_project = smart_import("mbpy.pkg.git.push")
        arun_command = smart_import("mbpy.cmd.arun_command")
        arun = smart_import("mbpy.cmd.arun")
        console = smart_import("mbpy.helpers._display.getconsole")()
        afind_toml_file = smart_import("mbpy.pkg.toml.afind_toml_file")
        tomlkit = smart_import("tomlkit")
        traceback = smart_import("traceback")
        from mbpy.helpers._display import safe_print
    
    from mbpy.helpers.gcliff import git_add_commit_push

    if not remote:
        check_install_prompt("uv")
        async for line in await arun_command("uv sync"):
            if "Warning" in line and "project" in line:
                safe_print(line)
            safe_print(line)
        return 
    org = (await arun("gh org list")).split("\n")[-1].strip()
    toml = await afind_toml_file()

    repo = tomlkit.parse(toml.read_text()).get("project", {}).get("name")
    remote = f"https://github.com/{org}/{repo}.git"
    try:
        await git_add_commit_push(branch, remote)
    except Exception:
        traceback.print_exc()


@cli.command("undo")
async def undo_command() -> None:
    """Undo the last commit."""
    undo_commit = smart_import("mbpy.pkg.git.undo_last_commit")
    try:
        await undo_commit()
    except Exception:
        import traceback

        traceback.print_exc()


@cli.command("publish", no_args_is_help=True)
@click.option("--bump", "-b", is_flag=True, help="Bump the version before publishing")
@click.option("--build", "-B", is_flag=True, help="Build the package before publishing")
@click.option(
    "--package-manager",
    "-p",
    type=click.Choice(
        [
            "gh",
            "hatch",
            "uv",
            "nix",
        ],
    ),
    default="github",
    help="Package manager to use",
)
@click.option(
    "--auth",
    "-a",
    help="PyPI or GitHub authentication token. Defaults to PYPI_TOKEN or GIT_TOKEN environment variable.",
)
@click.option("--gh-release", is_flag=True, help="Create a GitHub release")
@click.option("-A", "--args", help="Additional arguments to pass to the package manager")
async def publish_command(
    bump=False, build=False, package_manager="github", auth=None, gh_release=False, args=None,
) -> None:
    r"""Publish a package to PyPI or GitHub.

    Note: Git features require the GitHub CLI to be installed. See https://cli.github.com/ for more information.
    """
    if TYPE_CHECKING:
        from datetime import datetime

        from mbpy.cmd import arun, interact
        from mbpy.helpers._display import getconsole
        from mbpy.pkg.bump import bump as bump_pkg

        console = getconsole()
        today = datetime.today
        import os

        from rich.text import Text
    else:
        console = smart_import("mbpy.helpers._display.getconsole")()
        today = smart_import("datetime.today")

        interact = smart_import("mbpy.cmd.interact")
        arun = smart_import("mbpy.cmd.arun")
        bump_pkg = smart_import("mbpy.pkg.bump.bump")
        os = smart_import("os")
        Text = smart_import("rich.text.Text")

    if not await arun("which gh", show=False) and (package_manager == "github" or gh_release):
        platform_install_cmd = "`brew install gh`" if arun("which brew") else "`sudo snap install gh --classic`"
        console.print(
            f"GitHub CLI not found. Please install it to use this feature by running {platform_install_cmd}.",
            style="bold red",
        )
        return
    if not auth:
        auth = (
            os.getenv("GIT_TOKEN", os.getenv("GITHUB_TOKEN", None))
            if package_manager == "github"
            else os.getenv("PYPI_TOKEN")
        )
        if not auth:
            console.print("No authentication token found. Please provide one with the --auth flag.", style="bold red")
    version = None
    try:
        if bump:
            version = await bump_pkg()
        out = ""
        if build:
            await arun("rm -rf dist")
            out = await _build_command()
        if package_manager == "github":
            out = interact(["gh", "pr", "create", "--fill"], show=True)
            outs = ""
            for o in out:
                outs += o
                if "error" in o.lower():
                    console.print("Error occurred while creating pull request.", style="bold red")
                    return
            out = outs or "Pull request created successfully."
        elif package_manager == "uv":
            if not await arun("which twine"):
                console.print("Twine is not installed. Installing...", style="bold light_goldenrod2")
                await arun("pip install twine", show=True)
            out = await arun(["twine", "upload", "'dist/*'", "-u", "__token__", "-p", auth], show=False)
            console.print(Text.from_ansi(out))
        elif package_manager == "hatch":
            out = await arun(["hatch", "publish", "-u", "__token__", "-a", auth], show=True)
        else:
            console.print("Invalid package manager specified.", style="bold red")

        if "error" in out.lower():
            console.print("Error occurred while publishing package.", style="bold red")
        else:
            console.print(
                f"Package published successfully with {('version ' + version) if version else 'current version.'}",
                style="bold light_goldenrod2",
            )

        if gh_release:
            out = await arun(
                ["gh", "release", "create", version or f"{today().strftime('%d-%m-%Y')}"],
                show=True,
            )
        if "error" in out[-1].lower():
            console.print("Error occurred while creating release.", style="bold red")
        else:
            console.print(
                f"Release created successfully for version {(version or 'current')}.", style="bold light_goldenrod2",
            )

    except Exception:
        console.print("Error occurred while publishing package.", style="bold red")


@cli.command("help", no_args_is_help=True)
@click.argument("command", default=None, required=False)
async def help_command(command) -> None:
    """Display help for a command."""
    arun = smart_import("mbpy.cmd.arun")
    await arun(f"python -m pydoc {command}", show=True)
    command = smart_import(f"{command}")
    from pydoc import getdoc

    console = smart_import("mbpy.helpers._display.getconsole")()
    console.print(getdoc(command))
    from pyclbr import readmodule_ex

    console.print(readmodule_ex("mbpy"))


def has_failure(line: str) -> bool:
    line = str(line)
    return (
        line.lower().strip().startswith("error")
        or "failed" in line.lower()
        or "error" in line.lower()
        or "fatal" in line.lower()
        or "ERROR" in line
    )




async def check_install_prompt(
    program: str, unix: str | None = None, windows: str | None = None, linux: str | None = None, mac: str | None = None,
) -> bool:
    """Check if a program is installed and prompt to install it if not."""
    if TYPE_CHECKING:
        import os

        from mbpy.cmd import arun
        from mbpy.helpers._display import confirm, prompt_ask
    else:
        os = smart_import("os")
        prompt_ask = smart_import("mbpy.helpers._display.prompt_ask")
        confirm = smart_import("mbpy.helpers._display.confirm")
        arun = smart_import("mbpy.cmd.arun")
        
    if not await arun(f"which {program}"):
        y = confirm(f"{program} is not installed. Install now?")
        if y != "y":
            return False
        if os.name == "posix":
            out = await arun(unix)
        elif os.name == "nt":
            out = await arun(windows)
        elif os.name == "linux":
            out = await arun(linux)
        elif os.name == "mac":
            out = await arun(mac)
        if has_failure(out):
            return False
    return True


@cli.command("remove", no_args_is_help=True)
@click.argument("packages", nargs=-1)
@click.option("--dev", is_flag=True, help="Remove as a development dependency")
@click.option("--env", default=None, help="Specify the python, hatch, conda, or mbnix environment")
@click.option("-g", "--group", default=None, help="Specify the dependency group to use")
@click.option("-d", "--debug", is_flag=True, help="Enable debug logging")
async def remove_command(packages, dev, env, group, debug) -> None:
    """Remove a package from the project using uv or pip."""
    if dev and group:
        if group != "dev":
            msg = "Cannot specify both --dev and --group"
            raise click.UsageError(msg)
        group = None

    return await _uninstall_command(packages, env, group, debug=debug)


@cli.command("run", no_args_is_help=True, context_settings={"ignore_unknown_options": True})
@click.argument("command", nargs=-1)
@click.option("--auto", is_flag=True, help="Auto repair broken imports")
@click.option("-d", "--debug", is_flag=True, help="Enable debug logging")
async def run_cli_command(command: str, auto: bool = False, debug: bool = False) -> None:
    try:
        if auto:
            from mbpy.helpers.autopip import run_command_with_auto_pip

            await run_command_with_auto_pip(command, max_retries=3)
        else:
            from mbpy.cmd import arun

            await arun(command, show=True)
    except Exception:
        import traceback

        traceback.print_exc()





@cli.command("undo")
async def undo_command() -> None:
    """Undo the last commit."""
    undo_commit = smart_import("mbpy.pkg.git.undo_last_commit")
    try:
        await undo_commit()
    except Exception:
        import traceback

        traceback.print_exc()


@cli.command("publish", no_args_is_help=True)
@click.option("--bump", "-b", is_flag=True, help="Bump the version before publishing")
@click.option("--build", "-B", is_flag=True, help="Build the package before publishing")
@click.option(
    "--package-manager",
    "-p",
    type=click.Choice(
        [
            "gh",
            "hatch",
            "uv",
            "nix",
        ],
    ),
    default="github",
    help="Package manager to use",
)
@click.option(
    "--auth",
    "-a",
    help="PyPI or GitHub authentication token. Defaults to PYPI_TOKEN or GIT_TOKEN environment variable.",
)
@click.option("--gh-release", is_flag=True, help="Create a GitHub release")
async def publish_command(bump=False, build=False, package_manager="github", auth=None, gh_release=False) -> None:
    r"""Publish a package to PyPI or GitHub.

    Note: Git features require the GitHub CLI to be installed. See https://cli.github.com/ for more information.
    """
    if TYPE_CHECKING:
        from datetime import datetime

        from mbpy.cmd import arun, interact
        from mbpy.helpers._display import getconsole
        from mbpy.pkg.bump import bump as bump_pkg

        console = getconsole()
        today = datetime.today
        import os

        from rich.text import Text
    else:
        console = smart_import("mbpy.helpers._display.getconsole")()

        interact = smart_import("mbpy.cmd.interact")
        arun = smart_import("mbpy.cmd.arun")
        bump_pkg = smart_import("mbpy.pkg.bump.bump")
        os = smart_import("os")
        Text = smart_import("rich.text.Text")

    if not await arun("which gh", show=False) and (package_manager == "github" or gh_release):
        platform_install_cmd = "`brew install gh`" if arun("which brew") else "`sudo snap install gh --classic`"
        console.print(
            f"GitHub CLI not found. Please install it to use this feature by running {platform_install_cmd}.",
            style="bold red",
        )
        return
    if not auth:
        auth = (
            os.getenv("GIT_TOKEN", os.getenv("GITHUB_TOKEN", None))
            if package_manager == "github"
            else os.getenv("PYPI_TOKEN")
        )
        if not auth:
            console.print("No authentication token found. Please provide one with the --auth flag.", style="bold red")
    version = None
    try:
        if bump:
            version = await bump_pkg()
        out = ""
        if build:
            await arun("rm -rf dist")
            out = await arun(" ".join([package_manager, "build"]), show=True)
        if package_manager == "github":
            out = interact(["gh", "pr", "create", "--fill"], show=True)
            outs = ""
            for o in out:
                outs += o
                if "error" in o.lower():
                    console.print("Error occurred while creating pull request.", style="bold red")
                    return
            out = outs or "Pull request created successfully."
        elif package_manager == "uv":
            if not await arun("which twine"):
                console.print("Twine is not installed. Installing...", style="bold light_goldenrod2")
                await arun("pip install twine", show=True)
            out = await arun(["twine", "upload", "'dist/*'", "-u", "__token__", "-p", auth], show=False)
            console.print(Text.from_ansi(out))
        elif package_manager == "hatch":
            out = await arun(["hatch", "publish", "-u", "__token__", "-a", auth], show=True)
        else:
            console.print("Invalid package manager specified.", style="bold red")

        if "error" in out[-1].lower():
            console.print("Error occurred while publishing package.", style="bold red")
        else:
            console.print(
                f"Package published successfully with {('version ' + version) if version else 'current version.'}",
                style="bold light_goldenrod2",
            )

        if gh_release:
            out = await arun(
                ["gh", "release", "create", version or f"{today().strftime('%d-%m-%Y')}"],
                show=True,
            )
        if "error" in out[-1].lower():
            console.print("Error occurred while creating release.", style="bold red")
        else:
            console.print(f"Release created successfully for version {version}.", style="bold light_goldenrod2")

    except Exception:
        import traceback

        traceback.print_exc()


@cli.command("add", no_args_is_help=True)
@click.argument("packages", nargs=-1)
@click.option("--dev", is_flag=True, help="Add as a development dependency")
@click.option("-e", "--editable", is_flag=True, help="Add as an optional dependency")
@click.option("--env", default=None, help="Specify the Hatch, Conda, or mbnix environment to use")
@click.option("-g", "--group", default=None, help="Specify the dependency group to use")
@click.option("-U", "--upgrade", is_flag=True, help="Upgrade the package(s)")
@click.option("-r", "--requirements", type=click.Path(exists=True), help="Requirements file to install packages from")
@click.option(
    "-b", "--broken", type=click.Choice(["skip", "ask", "repair"]), default="skip", help="Behavior for broken packages",
)
@click.option("-d", "--debug", is_flag=True, help="Enable debug logging")
async def add_uvcommand(packages, dev, editable, env, group, upgrade, requirements, broken, debug):
    try:
        # Validate packages
        packages = [p for p in packages if p and isinstance(p, str)]

        await _install_command(
            packages=packages,
            requirements_file=requirements,
            upgrade=upgrade,
            editable=editable,
            env=env,
            group=group or "dev" if dev else "dependencies",
            debug=debug,
            broken=broken,
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        console = smart_import("mbpy.helpers._display.getconsole")()
        console.print(f"[red]Error installing packages: {str(e)}[/red]")


@cli.command("ask", no_args_is_help=True)
@click.argument("packages", nargs=-1)
async def conan_install_command(packages, env, group, debug) -> None:
    """Install packages using Conan."""
    if TYPE_CHECKING:
        from mbpy.cmd import arun
        from mbpy.helpers._display import getconsole

        console = getconsole()
        from mbpy.helpers._env import getenv
    else:
        arun = smart_import("mbpy.cmd.arun")
        console = smart_import("mbpy.helpers._display.getconsole")()
        getenv = smart_import("mbpy.helpers._env.getenv")
    if not await arun("which conan"):
        console.print('Conan is not installed. Please install with  `pip install "mbpy[conan]"`', style="bold red")
        return
    env = getenv(env)
    await _conan_cmd(packages, env=env, group=group, debug=debug, console=console, arun=arun)


async def _conan_cmd(packages, env, group, debug=False, console=None, arun=None):
    """Install packages using Conan."""
    if TYPE_CHECKING:
        from mbpy.cmd import arun
        from mbpy.helpers._display import getconsole

        console = getconsole()
        from rich.prompt import Prompt
        from rich.text import Text

        from mbpy.pkg.git import suggest_similar
    else:
        sys = smart_import("sys")
        arun = arun or smart_import("mbpy.cmd.arun")
        console = console or smart_import("mbpy.helpers._display.getconsole")()
        Prompt = smart_import("rich.prompt.Prompt")
        Text = smart_import("rich.text.Text")
        suggest_similar = smart_import("mbpy.pkg.git.suggest_similar")

    if sys.flags.debug or debug:
        logging.basicConfig(level=logging.DEBUG, force=True)

    for package in packages:
        try:
            resp = await arun(f"conan install {package}")
            if "error" in resp.lower():
                resp = prompt_ask(
                    f"Package '[bold blue]{package}[/bold blue]' not found for: [bold yellow]{env}[/bold yellow]. Search pypi/github for [bold blue]{package}[/bold blue]?",
                    choices=["y", "n"],
                    default="y",
                )
                if resp == "y":
                    from mbpy.helpers._display import display_similar_repos_table

                    results = await suggest_similar(package)
                    if results:
                        display_similar_repos_table(results, console=console)

                        choices = [r["name"] for r in results]
                        prompt_text = "Pick a package to install:\n" + "\n".join(f"- {name}" for name in choices)
                        resp = prompt_ask(Text(prompt_text), choices=choices, show_choices=False)
                        if resp:
                            from mbpy.pkg.git import clone_repo

                            if resp:
                                await clone_repo(
                                    results[[r["name"] for r in results].index(resp)].get("url", "github_url"),
                                )
                                await arun(f"conan install {package}")

        except Exception as e:
            console.print(f"Error: {e}", style="bold red")
            if debug:
                raise


@cli.command("remove", no_args_is_help=True)
@click.argument("packages", nargs=-1)
@click.option("--dev", is_flag=True, help="Remove as a development dependency")
@click.option("--env", default=None, help="Specify the python, hatch, conda, or mbnix environment")
@click.option("-g", "--group", default=None, help="Specify the dependency group to use")
@click.option("-d", "--debug", is_flag=True, help="Enable debug logging")
async def remove_command(packages, dev, env, group, debug) -> None:
    """Remove a package from the project using uv or pip."""
    if dev and group:
        if group != "dev":
            msg = "Cannot specify both --dev and --group"
            raise click.UsageError(msg)
        group = None
    return await _uninstall_command(packages, env, group, debug=debug)



async def _clean_command(path: "str | Path" = ".",env: str | None = None, debug: bool = False, all: bool = False, logs=False, patterns=None) -> None:
    """Remove build artifacts and optionally, generated c,cpp,so files."""
    console = smart_import("mbpy.helpers._display.getconsole")()
    arun = smart_import("mbpy.cmd.arun")
    files = smart_import("importlib.resources.files")
    isverbose = smart_import("mbpy.cli.isverbose")
    logs = "-p '*.log'" if logs else ""
    try:
        clean_script = files("mbpy") / "scripts" / "clean.sh"
        cmd = f"bash {clean_script} {env or ''} {'--all' if all else ''} {logs}"
        if patterns:
            cmd += " ".join([f"-p '{p}'" for p in patterns])
        cmd += f" {str(path)}"
        if isverbose():
            cmd += " --dry-run"

        await arun(cmd, show=True)

    except Exception as e:
        if log.debug():
            import traceback
            traceback.print_exc()
        else:
            console.print(f"Error: Failed to clean project: {str(e)}", style="bold red")

@cli.command("clean")
@click.argument("path", default=".", required=False)
@click.option("-a", "--all", is_flag=True, help="Clean all files")
@click.option("-l", "--logs", is_flag=True, help="Clean log files")
@click.option("-p", "--patterns", multiple=True, help="Patterns to clean")
@base_args
async def clean_command(path, all: bool = False, logs=False,patterns=None) -> None:
    """Remove build artifacts and optionally, logs and generated c,cpp,so files.
    
    Args:
        path (str): Path to clean
        all (bool): Clean all files
        logs (bool): Clean log files

    """
    return await _clean_command(path=path,all=all, logs=logs, patterns=patterns)


async def configure_cython(pyproject, project_name, path, out):
    """Configure Cython build settings in pyproject.toml"""
    arun = smart_import("mbpy.cmd.arun")
    platform = smart_import("platform")
    tomlkit = smart_import("tomlkit")
    chook = (
        pyproject.setdefault("tool", {})
        .setdefault("hatch", {})
        .setdefault("build", {})
        .setdefault("targets", {})
        .setdefault("wheel", {})
        .setdefault("hooks", {})
        .setdefault("cython", {})
    )
    chook["dependencies"] = ["hatch-cython"]

    # Match build system settings from pyproject.toml
    pyproject["build-system"] = {
        "requires": ["hatchling>=1.18.0", "Cython>=0.29.30", "toml>=0.10.2", "hatch-cython", "setuptools"],
        "build-backend": "hatchling.build",
    }

    chook["options"] = {
        "packages": [project_name],
        "src": ".",
        "includes": [project_name],
        "parallel": True,
        "directives": {
            "boundscheck": False,
            "nonecheck": False,
            "language_level": 3,
            "binding": True,
        },
        "source-files": [f"{str(path)}/**/*.pyx"],
    }

    system = platform.system().lower()
    machine = platform.machine().lower()

    compile_args = ["-v"]
    if system in ["linux", "darwin"]:
        compile_args.append("-Wcpp")
    if system == "darwin":
        if machine == "x86_64":
            compile_args.extend(["-arch", "x86_64"])
        elif machine in ["arm64", "aarch64"]:
            compile_args.extend(["-arch", "arm64"])

    chook["options"]["compile_args"] = compile_args
    chook["options"]["compile_kwargs"] = {
        "language_level": 3,
    }

    (path / "pyproject.toml").write_text(tomlkit.dumps(pyproject))
    await arun(f"cythonize -i -k -M {str(out)}/**/*.pyx", show=True)
    return await _install_command(project_name, editable=True)



@cli.command("doc", no_args_is_help=True)
@click.argument("name", type=str)
@click.argument("author", type=str)
@click.option("--theme", default="furo", help="Documentation theme to use")
@click.option("--kind", type=click.Choice(["sphinx", "mkdocs"]), default="sphinx", help="Documentation type to use")
async def docs_command(name: str, author: str, kind: str = "sphinx", theme: str = "furo"):
    """Generate documentation for a project."""
    # Import locally to avoid circular imports
    from mbpy.create import setup_documentation
    from mbpy.pkg.toml import afind_toml_file

    # Find project root using the toml file location
    project_root = (await afind_toml_file()).parent
    readme = project_root / "README.md"
    description = readme.read_text() if readme.exists() else ""

    await setup_documentation(
        project_name=name,
        author=author,
        description=description,
        autodoc=kind,
        theme=theme,
        project_root=project_root,
    )


# @cli.command("graph", no_args_is_help=True)
# @click.argument("path", default=".")
# @click.option("--sigs", is_flag=True, help="Include function and method signatures")
# @click.option("--docs", is_flag=True, help="Include docstrings in the output")
# @click.option("--code", is_flag=True, help="Include source code of modules in the output")
# @click.option("--who-imports", is_flag=True, help="Include modules that import each module")
# @click.option("--stats", is_flag=True, help="Include statistics and flow information")
# @click.option("--site-packages", is_flag=True, help="Include site-packages and vendor directories")
# async def graph_command(path, sigs, docs, code, who_imports, stats, site_packages) -> None:
#     """Generate a dependency graph of a Python project."""
#     generate_report = smart_import("mbpy.pkg.graph.generate")

#     try:
#         generate_report(path, sigs, docs, code, who_imports, stats, site_packages)
#     except Exception:
#         import traceback
#         traceback.print_exc()


@cli.command("who-imports")
@click.argument("module_name")
@click.argument("path", default=".")
@click.option("--site-packages", is_flag=True, help="Include site-packages and vendor directories")
async def who_imports_command(module_name, path, site_packages) -> None:
    """Find modules that import a given module."""
    who_imports = smart_import("mbpy.pkg.graph.who_imports")

    try:
        who_imports(module_name, path, site_packages=site_packages)
    except Exception:
        traceback.print_exc()


@cli.command("repair", no_args_is_help=True)
@click.argument("path", default=".")
@click.option("-d", "--dry-run", is_flag=True, help="Dry run")
async def repair_command(path, dry_run) -> None:
    """Repair broken imports."""
    traceback = smart_import("traceback")
    repair_main = smart_import("mbpy.pkg.repair.main", debug=True)
    try:
        await repair_main(path, dry_run)
    except Exception:
        traceback.print_exc()


# @cli.command("recover")
# @click.argument("branch", required=False)
# @click.option("-t", "--timeout", type=int, default=None, help="Command timeout")
# async def recover_command(branch=None, timeout=None) -> None:
#     """Recover from a failed rebase/merge and return to specified branch."""
#     if TYPE_CHECKING:
#         from mbpy.helpers._display import getconsole
#         from mbpy.pkg.git import recover_branch
#     else:
#         recover_branch = smart_import("mbpy.pkg.git.recover_branch")
#         getconsole = smart_import("mbpy.helpers._display.getconsole")

#     try:
#         await recover_branch(branch, timeout=timeout)
#     except Exception:
#         import traceback
#         traceback.print_exc()

from mbpy.helpers.gcliff import main as generate_changelog_command
from mbpy.pkg.graph import generate as graph_command

cli.add_command(generate_changelog_command, name="git")
cli.add_command(graph_command, name="graph")

def main():
    """Main entry point with proper async handling."""
    import uvloop

    uvloop.install()
    cli()


if __name__ == "__main__":


    main()
