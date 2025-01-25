import traceback
from typing import TYPE_CHECKING
from typing_extensions import AsyncGenerator
from mbpy.collect import first
from mbpy.import_utils import smart_import
import os
from pathlib import Path
import platform
from setuptools import Extension
from mbpy.helpers._traceback import install as install_rich_traceback, Traceback, link_fp
from mbpy.helpers._display import safe_print, getconsole, prompt_ask
from rich.table import Table
from typing import Dict, List, Tuple, Generator
from dataclasses import dataclass
from concurrent.futures import ProcessPoolExecutor
from rich.progress import Progress, BarColumn, TaskID, TextColumn
import sys
import subprocess
from asyncio import Semaphore
import concurrent
from rich.live import Live
import tomlkit
from itertools import chain as unique_everseen
from Cython.Build import cythonize
from Cython.Compiler import Options
from Cython.Compiler.Main import compile as cython_compile
from Cython.Compiler.Main import CompilationResult as CythonCompileResult
from rich.syntax import Syntax
import distutils.log
import logging
from mbpy.helpers._display import SPINNER
from Cython.Build import cythonize
from Cython.Compiler.Main import Context, CompilationOptions
from Cython.Build.Dependencies import create_extension_list
from mbpy.cmd import arun, arun_command
from mbpy.helpers._env import get_executable, getenv
import atexit   
@dataclass
class CythonBuildError:
    file: str
    error: str
    traceback: str
    step: str = ""  # Add step information
    line_no: int = 0
    
    def format_error(self):
        """Format error message with clean, minimal styling."""
        if not self.error:
            return ""
        
        parts = []
        if self.step:
            parts.append(f"[yellow]{self.step}[/yellow]")
        
        if 'Error:' in self.error:
            for line in self.error.split('\n'):
                if 'Error:' in line:
                    msg = line.split('Error:', 1)[1].strip()
                    parts.append(f"[red]{msg}[/red]")
                elif 'line' in line and ':' in line:
                    try:
                        self.line_no = int(line.split(':')[1].split()[0])
                        parts.append(f"[blue]at line {self.line_no}[/blue]")
                    except (IndexError, ValueError):
                        parts.append(line)
        else:
            parts.append(self.error)
            
        return " - ".join(parts)

@dataclass
class BuildSummary:
    succeeded: List[str]
    failed: List[CythonBuildError]  

@dataclass
class CompilationResult:
    """Results from Cython compilation."""
    succeeded: List[str] 
    failed: List[CythonBuildError]  # Fixed typo here - removed angle bracket
    total_files: int = 0
    setup_content: str = ""

    def __post_init__(self):
        self.succeeded = self.succeeded or []
        self.failed = self.failed or []
    
    def __bool__(self):
        return len(self.failed) == 0

    def display(self, console):
        if self.failed:
            console.print("\n[bold red]Build Errors:[/bold red]")
            for error in self.failed:
                console.print(f"[red]{Path(error.file).name}:[/red] {error.format_error()}")

def create_progress():
    """Create a rich progress display with dynamic colors and fixed number of bars."""
    return Progress(
        # Overall progress at the top
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=50),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("{task.fields[status]}"),
        console=getconsole(),
        expand=False,
        refresh_per_second=15
    )

def create_multi_progress():
    """Create a progress display that can show multiple bars."""
    return Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=50),
        "[progress.percentage]{task.percentage:>3.0f}%",
        console=getconsole(),
        expand=True,
        refresh_per_second=10,  # Increase refresh rate
        transient=False
    )

def compile_cython_files(tmp_dir, progress:Progress|None=None) -> Generator[TaskID,None,CompilationResult]:
    pyx_files: list[Path] = list(tmp_dir.rglob("*.pyx"))
    if not pyx_files:
        raise ValueError(f"No .pyx files found in {tmp_dir}")
    if progress is not None:
    # Add overall progress task
        overall_task: TaskID = progress.add_task(
            "[bold cyan]Compiling...[/bold cyan]",
            total=len(pyx_files),
            status=""
        )
        yield overall_task
        import pickle

    # use hash helper to check if file has changed

    # Track file status
    file_status = pickle.load(open(tmp_dir / ".stat", "rb")) if (tmp_dir / ".stat").exists() else {}
    
    current_file = None

    # Override Cython's logger
    class CythonLogger:
        def __init__(self):
            self.errors = []
            self.current_error = []
            
        def info(self, msg):
            nonlocal current_file
            if msg.startswith("Compiling "):
                # Extract filename and update progress
                filename = msg.split()[1].strip()
                current_file = next((f for f in pyx_files if str(f) in filename), None)
                if current_file:
                    file_status[str(current_file)] = "compiling"
                    progress.print(f"[cyan]{current_file.name}[/cyan]")
                    progress.update(overall_task, advance=1)

        def error(self, msg):
            if current_file:
                if "Error:" in msg:
                    error = CythonBuildError(
                        file=str(current_file),
                        error=msg.strip(),
                        traceback="",
                        step="compilation"
                    )
                    result.failed.append(error)
                    file_status[str(current_file)] = "failed"
                    # Format error message
                    progress.print(f"[red]Error in {current_file.name}:[/red] {msg.strip()}")
                else:
                    # Accumulate error context
                    self.current_error.append(msg.strip())

        def warning(self, msg):
            if current_file and msg.strip():
                progress.print(f"[yellow]Warning in {current_file.name}:[/yellow] {msg.strip()}")

    logger = CythonLogger()
    old_logger = distutils.log.Log._log
    distutils.log.Log._log = logger.info

    try:
        # Initialize Cython options
        Options.generate_cleanup_code = False
        Options.clear_to_none = False
        
        # Setup extensions with proper module names
        extensions = []
        for pyx_file in pyx_files:
            # if Path(pyx_file).exists():
                # Check if changed since last compilation.
              
            module_path = pyx_file.relative_to(tmp_dir)
            module_name = str(module_path.parent / module_path.stem).replace('/', '.')
            if module_name.startswith('.'):
                module_name = f"{tmp_dir.parent.name}.{module_name[1:]}"
                if progress:
                    progress.print(f"[cyan]Compiling {pyx_file.name}[/cyan]")
                    tid: TaskID = progress.add_task(f"Compiling {pyx_file.name}", status="compiling")
                    yield tid
            ext = Extension(
                module_name,
                sources=[str(pyx_file)],
                include_dirs=[str(pyx_file.parent)],
            )
            extensions.append(ext)

        # Do compilation
        extensions = cythonize(
            extensions,
            compiler_directives={
                'embedsignature': True,
                'language_level': '3',
                'boundscheck': True,
                'wraparound': True,
            },
            
            quiet=False,
        )

        # Record successes
        failed_files = []
        for pyx_file in pyx_files:
            if str(pyx_file) not in file_status or file_status[str(pyx_file)] != "failed":
                if progress:
                    progress.update(overall_task, advance=1)
                    progress.update(tid, status="success",completed=True,refresh=True)
                file_status[str(pyx_file)] = "compiled"
            else:
                if progress:
                    progress.update(overall_task, advance=1)
                    progress.update(tid, status="fail", completed=True)
                failed_files.append(pyx_file)

        if failed_files and progress:
            progress.update(overall_task, status=f"[red]{len(failed_files)} files failed[/red]" + \
                f"[cyan] ({len(pyx_files) - len(failed_files)} compiled successfully)[/cyan]")

    except Exception as e:
     
        traceback.print_exc()
        
     

    finally:
        distutils.log.Log._log = old_logger



# async def gen_setup(
#     name: str,
#     path: str,
#     verbose: bool = False,
#     build: bool = False
# ) -> CompilationResult:
#     """Generate setup.py and compile Cython files."""
#     pkg_path = Path(path)
#     tmp_dir = pkg_path / "tmp" / name
#     console = getconsole()
#     progress = create_progress()


#     # Generate setup.py content
#     ext_modules = []
#     setup_content = f"""from setuptools import setup, find_namespace_packages
# from setuptools.extension import Extension
# from Cython.Build import cythonize
# import sys
# import platform

# ext_modules = {ext_modules}

# setup(
#     name='{name}',
#     packages=find_namespace_packages(include=['{name}*']),
#     package_dir={{'': '{tmp_dir.parent.relative_to(pkg_path)}'}},
#     ext_modules=ext_modules,
#     python_requires='>=3.7',
#     zip_safe=False
# )

# # Cleanup after build
# import atexit
# import shutil
# from pathlib import Path

# def cleanup():
#     try:
#         if Path('setup.py').exists():
#             Path('setup.py').unlink()
#         build_dir = Path('build')
#         if build_dir.exists():
#             shutil.rmtree(build_dir)
#     except Exception as e:
#         print(f'Cleanup failed: {{e}}')

# atexit.register(cleanup)
# """
#     compilation_result.setup_content = setup_content
#     return compilation_result

class BuildResults:
    def __init__(self, status: bool, err: str, compilation_result: CompilationResult = None):
        self.status = status
        self.err = err
        self.compilation_result = compilation_result

async def setup_command(path, build=False, progress=None):

    atexit.register(remove_setup, "setup.py")
    try:
        path = Path(str(path))
        console = getconsole()
        progress = progress or create_multi_progress()
        SPINNER().stop()
        with progress:

            # Build config phase
            tmp_dir = path / "tmp" / path.name
            tmp_dir.mkdir(parents=True, exist_ok=True)
            # Compilation phase
            gen = compile_cython_files(tmp_dir, progress)
            start = first(gen)
            hasfail = False
            for task_id in  gen:
                if progress.tasks[task_id].fields.get("status") == "fail":
                    progress.update(task_id, visible=True)
                else:
                    # safe_print(out)
                    hasfail = True
            progress.stop()


            # if build:
            #     progress.update(start, description="[cyan]Building package...[/cyan]", completed=75)
            #     other = []
            #     async for out in  await arun_command(f"{get_executable(None)} -m pip install -e .",show=False):
               

            #         other.append(out)
            #     out = "\n".join(other)
            #     if "failed" not in out.lower() or "error" not in out.lower():
            #         progress.update(start, completed=100)
            #         progress.print("[bold green] Compilation Succeeded[/bold green]")
            #     else:
            #         progress.print("[bold red] Compilation Failed [/bold red]")
            return BuildResults(not hasfail, "", CompilationResult(succeeded=[f.description for f in progress.tasks if f.fields.get("status") == "success"],
                                                                          failed=[f.description for f in progress.tasks if f.fields.get("status") == "fail"])
            )
        

    except Exception as e:
        if progress:
            progress.stop()
        return BuildResults(False, str(e), None)

def remove_setup(path):
    path = Path(str(path))
    setup_path = path
    if setup_path.exists():
        setup_path.unlink()

