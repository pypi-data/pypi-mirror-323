from datetime import datetime
from mbpy.import_utils import smart_import
from typing import List
import asyncio
import os
from typing import TYPE_CHECKING


async def is_git_repo(path: str | None = None) -> bool:
    """Check if the current directory is a git repository."""
    try:
        process = await asyncio.create_subprocess_exec(
            'git', 'rev-parse', '--is-inside-work-tree',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=path
        )
        _, _ = await process.communicate()
        return process.returncode == 0
    except:
        return False

async def get_repo_root() -> str:
    """Get and cache the Git repository root."""
    global _repo_root
    if not _repo_root:
        result = await arun(['git', 'rev-parse', '--show-toplevel'])
        _repo_root = result.strip()
    return _repo_root


async def arun(cmd_args: List[str], cwd: str | None = None, debug: bool = False, console=None) -> str:
    """Run a command asynchronously and return its output."""
    if not TYPE_CHECKING:
        SPINNER = smart_import("mbpy.helpers._display.SPINNER")()
        console = console or smart_import("mbpy.helpers._display.getconsole")()
    else:
        from mbpy.helpers._display import SPINNER
        from mbpy.helpers._display import getconsole
        console = getconsole()
        
    if not await is_git_repo(cwd):
        raise ValueError("Not a git repository")
    try:
        # Only show command if debugging
        if debug:
            SPINNER.stop()
            console.print(f"[dim]$ {' '.join(cmd_args)}[/dim]")
        
        # Handle path validation
        if cwd and not os.path.exists(cwd):
            raise FileNotFoundError(f"Directory not found: {cwd}")
            
        # Clean up command arguments to handle malformed strings
        cleaned_args = [arg.strip() for arg in cmd_args if isinstance(arg, str)]
        
        process = await asyncio.create_subprocess_exec(
            *cleaned_args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd
        )
        stdout, stderr = await process.communicate()
        
        # Only show output if debugging
        if debug and stdout:
            console.print(f"[dim] -> {stdout.decode().strip()}[/dim]")
            
        if process.returncode != 0:
            if debug:
                console.print(f"[yellow]stderr:[/yellow] {stderr.decode().strip()}")
            
            error_msg = stderr.decode().strip()
            if "not a git repository" in error_msg.lower():
                raise ValueError("Not a git repository. Please check your working directory.")
            elif "no such file or directory" in error_msg.lower():
                raise FileNotFoundError(f"File or directory not found in command: {' '.join(cmd_args)}")
            raise RuntimeError(f"Command failed: {error_msg}")
        
        output = stdout.decode().strip()
        if debug and len(output) > 0:
            SPINNER.stop()
            console.print(f"[dim]{len(output)} bytes[/dim]")
        return output
    except Exception as e:
        SPINNER.stop()
        console.print(f"[red]Error:[/red] {str(e)}")
        return ""

class GitContext(dict):
    local_branch = None
    remote_branch = None
    async def __init__(self, local_branch: str = None, remote_branch: str = None):
        try:
            self.local_branch = local_branch or await arun(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
            out = self.local_branch.split("-temp")[0]
            if not local_branch:
                self.local_branch = f"{out}-temp-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            self.remote_branch = remote_branch or out
            
            checked_out = await arun(['git', 'checkout', '-b', self.local_branch])
            if "fatal" in checked_out:
                raise Exception(f"Error creating new branch: {checked_out}")
            
            await super().__init__(local_branch=self.local_branch, remote_branch=self.remote_branch)
        except Exception as e:
            raise Exception(f"Failed to initialize GitContext: {str(e)}")

    def __getattr__(self, name):
        try:
            if name in self:
                return self[name]
            return super().__getattr__(name)
        except AttributeError:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        if not name.startswith("_"):
            self[name] = value
        super().__setattr__(name, value)

    def __delattr__(self, name):
        if name in self:
            del self[name]
        super().__delattr__(name)

class gitpush:
    def __init__(self, ctx: GitContext = None):
        self.ctx = ctx or GitContext()
        
    async def __aenter__(self):
        out = await arun(['git', 'push'])
        if "fatal" in out:
            raise Exception(f"Error during push operation: {out}")
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            console = smart_import("mbpy.helpers._display.getconsole")()
            console.print(f"[red]Error during push operation: {str(exc_val)}[/red]")
            
            try:
                # Store current branch name for later cleanup
                current_branch = await arun(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
                if "fatal" in current_branch:
                    console.print("[red]Failed to get current branch[/red]")
                    return False
                
                # Check for untracked files
                untracked = await arun(['git', 'ls-files', '--others', '--exclude-standard'])
                if untracked and "fatal" not in untracked:
                    console.print("[yellow]Untracked files detected. Creating temporary commit...[/yellow]")
                    
                    # Create temporary commit
                    add_result = await arun(['git', 'add', '.'])
                    if "fatal" in add_result:
                        console.print("[red]Failed to stage files[/red]")
                        return False
                        
                    commit_msg = f"temp: Save changes before rebase {datetime.now().strftime('%Y%m%d%H%M%S')}"
                    commit_result = await arun(['git', 'commit', '-m', commit_msg])
                    if "fatal" in commit_result:
                        console.print("[red]Failed to create temporary commit[/red]")
                        return False
                    
                    # Switch to parent branch
                    parent_branch = self.ctx.remote_branch
                    if not parent_branch:
                        console.print("[red]No parent branch specified[/red]")
                        return False
                        
                    console.print(f"[blue]Switching to parent branch: {parent_branch}[/blue]")
                    checkout_result = await arun(['git', 'checkout', parent_branch])
                    if "fatal" in checkout_result:
                        console.print(f"[red]Failed to checkout {parent_branch}[/red]")
                        # Try to return to original branch
                        await arun(['git', 'checkout', current_branch])
                        return False
                    
                    # Rebase changes from temp branch
                    console.print("[blue]Rebasing changes...[/blue]")
                    rebase_result = await arun(['git', 'rebase', current_branch])
                    if "fatal" in rebase_result or "CONFLICT" in rebase_result:
                        console.print("[yellow]Rebase conflicts detected. Aborting...[/yellow]")
                        abort_result = await arun(['git', 'rebase', '--abort'])
                        if "fatal" in abort_result:
                            console.print("[red]Failed to abort rebase[/red]")
                        
                        # Return to original branch
                        await arun(['git', 'checkout', current_branch])
                        return False
                    
                    # Clean up temp branch
                    cleanup_result = await arun(['git', 'branch', '-D', current_branch])
                    if "fatal" in cleanup_result:
                        console.print("[yellow]Warning: Failed to delete temporary branch[/yellow]")
                    else:
                        console.print("[green]Successfully rebased changes and cleaned up[/green]")
                    
                    return True
                    
            except Exception as e:
                console.print(f"[red]Error during cleanup: {str(e)}[/red]")
                try:
                    if 'current_branch' in locals():
                        out = await arun(['git', 'checkout', current_branch])
                        if "fatal" in out:
                            console.print("[red]Failed to return to original branch[/red]")
                except:
                    pass
                return False
                
        return False