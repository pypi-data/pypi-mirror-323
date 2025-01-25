# Ensure the tmp/mbpy directory is correctly referenced
import os
from pathlib import Path
from typing_extensions import TYPE_CHECKING
from mbpy.helpers._display import safe_print,smart_import
import traceback

def add_auto_cpdef_to_package(package_path: Path | str, outdir="./tmp",progress=None,force=False,cythonize=True):
    """Add the `# cython: auto_cpdef=True` directive to all `.py` files and convert to .pyx."""
    if not TYPE_CHECKING:
        _cythonize = smart_import("Cython.Build.Cythonize.cythonize")
    else:
        from Cython.Build import cythonize as _cythonize
    package_path = Path(str(package_path))
    outdir = Path(str(outdir))
    outdir = outdir / package_path.name
    outdir.mkdir(parents=True, exist_ok=True)
    
    # Clear any existing .pyx files first
    if force:
        for f in outdir.glob("**/*.pyx"):
            f.unlink()
        
    # List to track created .pyx files
    converted_files = []
    
    # Skip problematic files and patterns
    SKIP_PATTERNS = (
        "venv", "site-packages", "cython", "test", 
        "example", "docs", ".git", "__pycache__"
    )
    SKIP_FILES = {
        "__init__.py", "__main__.py", "setup.py", 
        "conf.py", "cython.py", "_setup_pyx.py"
    }
    from io import StringIO
    stdout = StringIO()
    stderr = StringIO()
    for f in package_path.glob("**/*.py"):
        # Skip files in problematic directories
        if any(pat in str(f.resolve()) for pat in SKIP_PATTERNS):
            continue
            
        # Skip special files
        if f.name in SKIP_FILES:
            continue
            
        try:
            # Validate file is valid Python before converting
            with Path(f).open('r', encoding='utf-8') as source:
                content = source.read()
                try:
                    compile(content, str(f), 'exec')
                except SyntaxError:
                    safe_print(f"Skipping {f}: Invalid Python syntax")
                    continue
                    
            # Create corresponding .pyx file
            rel_path = f.relative_to(package_path)
            out_file = outdir / rel_path.with_suffix(".pyx")
            out_file.parent.mkdir(parents=True, exist_ok=True)
            
            out_file.write_text("# cython: auto_cpdef=True\n" + content, encoding='utf-8')
            from contextlib import redirect_stderr, redirect_stdout

            with redirect_stderr(stderr), redirect_stdout(stdout):
                try:
                    _cythonize([str(out_file)], force=True,quiet=False,show_all_warnings=True)
                except Exception as e:
                    safe_print(f"Error converting {f}: {e}")

                    if "error" in stderr.getvalue().lower():
                        safe_print(f"Removing cpdef directive from {f}")
                        out_file.write_text(content, encoding='utf-8')
        
                        out = _cythonize([str(out_file)], force=True,quiet=False,show_all_warnings=True)
                        safe_print(out)
                    else:
                        safe_print(stderr.getvalue().replace(str(out_file), str(f)))
                        safe_print(stdout.getvalue().replace(str(out_file), str(f)))
                        stdout.close()
                        stdout = StringIO()
                        stderr.close()
                        stderr = StringIO()
                        continue
      
          
            input("Press Enter to continue...")
            converted_files.append(out_file)
            
        except Exception as e:
            safe_print(f"Start")
            safe_print(stdout.getvalue().replace(str(out_file), str(f)))
            safe_print(stderr.getvalue().replace(str(out_file), str(f)))
            safe_print("Done")
            # traceback.print_exc()
            safe_print(f"Error converting {f}: {e}")
            exit(1)
            
    return converted_files



if __name__ == "__main__":
    add_auto_cpdef_to_package("mbpy", force=True,cythonize=True)