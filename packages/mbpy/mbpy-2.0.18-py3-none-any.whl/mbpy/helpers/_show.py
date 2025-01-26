from __future__ import annotations

from typing import TYPE_CHECKING

from mbpy.import_utils import smart_import


async def _show_command(package: str | None = None, *,debug=None, env=None) -> None:
    """Show the dependencies from the pyproject.toml file."""
    if TYPE_CHECKING:
        import json
        import sys
        import traceback
        from pathlib import Path

        import tomlkit
        from rich.pretty import pprint
        from rich.table import Table
        from rich.text import Text

        from mbpy.helpers._display import getconsole
        from mbpy.pkg.toml import afind_toml_file
        console = getconsole()
        from mbpy.cmd import arun_command
        from mbpy.helpers._env import get_executable
    else:
        Path = smart_import('pathlib.Path')
        tomlkit = smart_import('tomlkit')
        Table = smart_import('rich.table.Table')
        Text = smart_import('rich.text.Text')
        find_toml_file = smart_import('mbpy.pkg.toml.find_toml_file')
        arun_command = smart_import('mbpy.cmd.arun_command')
        get_executable = smart_import('mbpy.helpers._env.get_executable')
        console = smart_import('mbpy.helpers._display.getconsole')()
        traceback = smart_import('traceback')
        sys = smart_import('sys')
        afind_toml_file = smart_import('mbpy.pkg.toml.afind_toml_file')
        arun_command = smart_import('mbpy.cmd.arun_command')
        SPINNER = smart_import('mbpy.helpers._display.SPINNER')()
        json = smart_import('json')
    if package is not None and package.strip():
        try:
            arun = smart_import('mbpy.cmd.arun')
            await arun(f"{sys.executable} -m pip show {package}", show=True)
            return
        except Exception:
            traceback.print_exc()

    toml_path = await afind_toml_file()
    try:
        content = Path(toml_path).read_text()
        pyproject = tomlkit.parse(content)

        # Create a prettier table for installed packages
        installed_table = Table(title=Text("Installed Packages", style="bold green"))
        installed_table.add_column("Package", style="cyan")
        installed_table.add_column("Version", style="magenta")

        # Capture pip list output and parse it
        pip_output = []
        async for line in await arun_command(f"{get_executable(env)} -m pip list --format=json", show=False):
            pip_output.append(line)
        
        installed_packages = json.loads("".join(pip_output))
        for pkg in installed_packages:
            pkg["name"] = pkg["name"].lower().replace("_","-")
            installed_table.add_row(pkg["name"].replace("_","-"), pkg["version"])

        # Show installed packages
        console.print(installed_table)
        console.print()  # Add spacing between tables

        # Determine if we are using Hatch or defaulting to project dependencies
        if env is not None and "tool" in pyproject and "hatch" in pyproject.get("tool", {}):
            dependencies = (
                pyproject.get("tool", {}).get("hatch", {}).get("envs", {}).get(env, {}).get("dependencies", [])
            )
        else:
            dependencies = pyproject.get("project", {}).get("dependencies", [])
        
        dependencies = {dep.lower().replace("_","-") for dep in dependencies}

        if dependencies:
            required_table = Table(title=Text("Required Dependencies", style="bold cyan"))
            required_table.add_column("Package", style="bold cyan")
            required_table.add_column("Version", style="magenta")
            required_table.add_column("Status", style="bold green")
            required_table.add_column("Location", style="bold blue")
            
            # Check if required packages are installed
            installed_names = {pkg["name"].lower().replace("_","-") for pkg in installed_packages}
            for dep in dependencies:
                pkg_name = dep.split("[")[0].split(">=")[0].split("==")[0].split("<")[0].split(">")[0].split("@")[0].strip()
                version = dep.split("==")[-1].split(">=")[-1].split("<=")[-1].split("<")[-1].split(">")[-1].split(",")[-1].split("]")[0] if "@" not in dep else ""
                location = dep.split("@")[-1].strip() if "@" in dep else ""
                status = "✓ Installed" if pkg_name.lower() in installed_names else "✗ Missing"
                status_style = "bold green" if "Installed" in status else "bold red"
                required_table.add_row(pkg_name, version, Text(status, style=status_style),location)
            
            console.print(required_table)
        else:
            console.print("No dependencies found.", style="bold yellow")

    except FileNotFoundError:
        console.print("No pyproject.toml file found.", style="bold red")
    except Exception as e:
        console.print(f"Error: {e}", style="bold red")
        traceback.print_exc()
