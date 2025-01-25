import asyncio
from datetime import datetime, timedelta
import ast
from typing import TYPE_CHECKING, Dict, List
import collections
import os
from typing_extensions import TypedDict
import rich_click as click
import re
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Optional, Set
from mbpy.import_utils import smart_import
from mbpy.cli import base_args
from mbpy.helpers._cache import acache
from mbpy.helpers._git_ctx import arun, is_git_repo, get_repo_root
_repo_root = None

if TYPE_CHECKING:
    class ModuleChanges(TypedDict):
        classes: list[str]
        functions: list[str] 
        module: str
else:
    ModuleChanges = dict

class Granularity(Enum):
    MODULE = "module"
    FILE = "file"
    CLASS = "class"
    FUNCTION = "function"

@dataclass
class ChangeMetric:
    name: str
    lines_changed: int
    type: Granularity
    module: str
    children: Optional[Set[str]] = None

    def __hash__(self):
        return hash((self.name, self.type, self.module))


def categorize_commit(message: str) -> tuple[str, str]:
    """Categorize a commit message and improve its formatting."""
    categories = {
        'feat': '🚀 Features',
        'fix': '🐛 Bug Fixes', 
        'docs': '📚 Documentation',
        'test': '🧪 Tests',
        'refactor': '♻️ Refactoring',
        'style': '💎 Style',
        'chore': '🔧 Maintenance',
        'perf': '⚡️ Performance'
    }
    
    # Extract type and description
    parts = message.split(':', 1)
    if len(parts) == 2:
        type_str = parts[0].lower()
        description = parts[1].strip()
    else:
        type_str = 'other'
        description = message.strip()
        
    # Improve message formatting
    if description:
        description = description[0].upper() + description[1:]
        if not description.endswith('.'):
            description += '.'
            
    return categories.get(type_str, '🔍 Other Changes'), description

async def get_diff_stats(commit_hash: str = None, include_unstaged: bool = False) -> Dict[str, int]:
    """Get number of changed lines per file."""
    if commit_hash:
        # Use a more specific git show command to get stats
        cmd = [
            'git', 'show',
            '--format=',  # Skip commit message
            '--stat',     # Get statistics
            '--numstat',  # Numeric statistics
            commit_hash
        ]
    else:
        if include_unstaged:
            # Include both staged and unstaged changes
            cmd = ['git', 'diff', '--numstat']
        else:
            # Only staged changes
            cmd = ['git', 'diff', '--cached', '--numstat']
    
    output = await arun(cmd)
    changes = {}
    
    for line in output.splitlines():
        line = line.strip()
        if not line or line.startswith('/'): # Skip empty lines and file paths
            continue
            
        try:
            parts = line.split('\t')
            if len(parts) == 3:  # Only process lines with additions, deletions, and filepath
                additions, deletions, filepath = parts
                if additions != '-' and deletions != '-':  # Skip binary files
                    changes[filepath] = int(additions) + int(deletions)
        except (ValueError, IndexError):
            continue
            
    return changes

async def analyze_scope_changes(filepath: str, commit_hash: str = None) -> str:
    """Analyze whether changes affect module, class or function level."""
    if commit_hash:
        cmd = ['git', 'show', f'{commit_hash}:{filepath}']
    else:
        cmd = ['git', 'show', f':{filepath}']
    
    try:
        content = await arun(cmd)
        tree = ast.parse(content)
        changed_classes = []
        changed_functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                changed_classes.append(node.name)
            elif isinstance(node, ast.FunctionDef):
                changed_functions.append(node.name)
        
        if changed_classes:
            return f"class:{','.join(changed_classes)}"
        elif changed_functions:
            return f"function:{','.join(changed_functions)}"
        return "module"
    except:
        return "module"

def categorize_by_size(filepath: str, lines: int, scope: str) -> str:
    """Categorize changes based on line count thresholds."""
    if lines > 1000:
        return f"Major overhaul to {os.path.basename(filepath)} module"
    elif lines >= 100:
        scope_name = scope.split(':')[-1] if ':' in scope else os.path.basename(filepath)
        return f"Improvements to {scope_name}"
    return "Minor fixes"

async def amend_commit_message(commit_hash: str, new_message: str) -> bool:
    """Amend a commit message using git filter-branch."""
    try:
        # Create a temporary script for filter-branch
        script = f'''
if [ "$GIT_COMMIT" = "{commit_hash}" ]; then
    echo "{new_message}"
else
    cat
fi
'''
        script_path = '/tmp/filter-msg'
        with open(script_path, 'w') as f:
            f.write(script)
        os.chmod(script_path, 0o755)

        # Run filter-branch to rewrite the commit message
        cmd = [
            'git', 'filter-branch', '-f', '--msg-filter', 
            f'/bin/bash {script_path}', f'{commit_hash}^..{commit_hash}'
        ]
        await arun(cmd)
        os.remove(script_path)
        return True
    except Exception as e:
        console = smart_import("mbpy.helpers._display.getconsole")()
        console.print(f"[red]Failed to amend commit message: {str(e)}[/red]")
        return False

def clean_commit_message(msg: str) -> str:
    """Clean up commit messages by removing unwanted patterns."""
    patterns = [
        r'┏[━┃┗]+┓[\s\S]*?┛',  # Box drawings with content
        r'┏[━┃┗]+┓',           # Box headers
        r'┗[━┃┗]+┛',           # Box footers
        r'━+',                 # Horizontal lines
        r'#\s*Changelog.*?(?=\n|$)',  # Changelog headers
        r'Generated on:.*?(?=\n|$)',   # Generated timestamps
        r'\s+$',              # Trailing whitespace
        r'^\s+',              # Leading whitespace
        r'\n+',               # Multiple newlines
        r'\[.*?\]',           # Square bracket content
        r'┃.*?┃',             # Vertical box lines with content
    ]
    
    cleaned = msg
    for pattern in patterns:
        cleaned = re.sub(pattern, '', cleaned, flags=re.MULTILINE | re.DOTALL)
    
    # Additional cleanup
    cleaned = cleaned.strip()
    cleaned = re.sub(r'\s+', ' ', cleaned)  # Collapse multiple spaces
    
    return cleaned if cleaned else "No message"

async def analyze_module_changes(filepath: str, commit_hash: str |None = None) -> ModuleChanges:
    """Analyze module changes using AST."""
    try:
        if commit_hash:
            cmd = ['git', 'show', f'{commit_hash}:{filepath}']
        else:
            cmd = ['git', 'show', f':{filepath}']
        
        content = await arun(cmd)
        tree = ast.parse(content)
        


        changes: ModuleChanges = {
            'classes': [],
            'functions': [], 
            'module': os.path.basename(filepath)
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                changes['classes'].append(node.name)
            elif isinstance(node, ast.FunctionDef):
                changes['functions'].append(node.name)       
        return changes
    except Exception:
        return {'module': os.path.basename(filepath), 'classes': [], 'functions': []}
async def generate_change_message(changes: ModuleChanges, lines: int, granularity: Granularity = Granularity.MODULE) -> tuple[str, List[ChangeMetric]]:
            """Generate a structured change message and return metrics."""
            module = changes['module']
            metrics = []
            
            # Determine change magnitude
            if lines > 1000:
                header = "Major Changes"
            elif lines >= 100:
                header = "Significant Changes"
            else:
                header = "Minor Changes"
            
            msg_parts = []
            
            if granularity == Granularity.FILE:
                msg_parts.append(f"{header}")
                msg_parts.append(f"- Module: {module}")
                metrics.append(ChangeMetric(module, lines, Granularity.FILE, module))
            
            elif granularity == Granularity.CLASS and changes['classes']:
                classes = changes['classes']
                msg_parts.append(f"{header}")
                msg_parts.append(f"- Module: {module}")
                msg_parts.extend([f"  - Class: {c}" for c in classes])
                metrics.extend([ChangeMetric(c, lines // len(classes), Granularity.CLASS, module) for c in classes])
            
            elif granularity == Granularity.FUNCTION and changes['functions']:
                functions = changes['functions']
                msg_parts.append(f"{header}")
                msg_parts.append(f"- Module: {module}")
                msg_parts.extend([f"  - Function: {f}" for f in functions])
                metrics.extend([ChangeMetric(f, lines // len(functions), Granularity.FUNCTION, module) for f in functions])
            
            else:  # Default MODULE
                msg_parts.append(f"{header}")
                msg_parts.append(f"- Module: {module}")
                if changes['classes']:
                    msg_parts.append("  - Classes:")
                    msg_parts.extend([f"    * {c}" for c in changes['classes']])
                if changes['functions']:
                    msg_parts.append("  - Functions:")
                    msg_parts.extend([f"    * {f}" for f in changes['functions']])
                
                metric = ChangeMetric(
                    module, 
                    lines, 
                    Granularity.MODULE, 
                    module,
                    children=set(changes['classes'] + changes['functions'])
                )
                metrics.append(metric)
            
            return "\n".join(msg_parts), metrics

async def get_log_date(days: int) -> str:
    """Get the correct date format for git log."""
    date = datetime.now() - timedelta(days=days)
    return date.strftime('%Y-%m-%d')

async def get_commit_history(
        days: int | None = None,
        branch: str | None = None, 
        overwrite: bool = False, 
        dry_run: bool = False,
        granularity: Granularity = Granularity.MODULE,
        max_changes: int|None = None,
        commit_filters: Dict[str, str] = None,  # Added configurable filters
        min_lines: int = 1,  # Added minimum lines threshold
        file_patterns: List[str] = None  # Added file pattern filter
    ) -> tuple[List[dict], List[ChangeMetric]]:
        """Get commit history and change metrics.
        
        Args:
            days: Number of days to look back (-1 for last change)
            branch: Branch to analyze
            overwrite: Whether to overwrite commit messages
            dry_run: Whether to perform a dry run
            granularity: Level of change analysis
            max_changes: Maximum number of changes to process
            commit_filters: Filters for commit selection
            min_lines: Minimum number of changed lines to include
            file_patterns: List of file patterns to analyze (e.g. ['*.py'])
        """
        debug = smart_import("mbpy.log.debug")
        console = smart_import("mbpy.helpers._display.getconsole")()

        console.print("\n[blue]Git Repository Info[/blue]")
        console.print(f"[dim]Working directory:[/dim] {os.getcwd()}")
        from mbpy.log import debug
        debug = bool(debug())
        try:
            repo_root = await get_repo_root()
            console.print(f"[dim]Git root:[/dim] {repo_root}")
        except Exception as e:
            console.print(f"[yellow]Could not get repo root: {e}[/yellow]")

        # Build git log command with configurable parameters
        cmd = ['git', 'log']
        
        if days is not None:
            cmd.extend([f'--since={days}.days.ago'])
        
        cmd.extend([
            '--all',
            '--full-history',
            '--no-merges',
            '--date=format:%Y-%m-%d',
            '--pretty=format:%H|%ad|%s|%ae'
        ])

        if branch:
            cmd.append(branch)
            
        if file_patterns:
            cmd.extend(['--'] + file_patterns)
        SPINNER = smart_import("mbpy.helpers._display.SPINNER")()
        SPINNER.stop()
        console.print("\n[blue]Commit History[/blue]")
        output = await arun(cmd,debug=debug)
        
        if not output:
            console.print("[yellow]No commits found in the specified time period[/yellow]")
            return [], []

        commits = []
        all_metrics: List[ChangeMetric] = []
        lines = output.splitlines()
        
        if max_changes:
            lines = lines[:max_changes]
        if debug:
            console.print(f"\n[blue]Found {len(lines)} commits to analyze[/blue]")
        
        for line in lines:
            try:
                hash_val, date, msg, author = line.split('|')
                
                # Apply commit filters if specified
                if commit_filters:
                    skip = False
                    for key, pattern in commit_filters.items():
                        if key == 'author' and not re.search(pattern, author):
                            skip = True
                            break
                        elif key == 'message' and not re.search(pattern, msg):
                            skip = True
                            break
                    if skip:
                        continue
                if debug:
                    SPINNER.stop()
                    console.print(f"\n[blue]Analyzing commit[/blue] {hash_val[:7]} from {date}")
                
                changes = await get_diff_stats(hash_val)
                if not changes:
                    console.print("[yellow]No file changes found[/yellow]")
                    continue

                # Filter changes by minimum lines
                changes = {k: v for k, v in changes.items() if v >= min_lines}
                
                messages = []
                commit_metrics = []
                
                for filepath, lines_changed in changes.items():
                    if filepath.endswith('.py'):  # This could be made configurable too
                        if debug:
                            console.print(f"[blue]Analyzing Python file:[/blue] {filepath} ({lines_changed} lines)")
                        module_changes = await analyze_module_changes(filepath, hash_val)
                        message, metrics = await generate_change_message(module_changes, lines_changed, granularity)
                        messages.append(message)
                        commit_metrics.extend(metrics)

                if commit_metrics:
                    all_metrics.extend(commit_metrics)

                final_message = ' && \n'.join(filter(None, messages)) if messages else "minor fixes"
                SPINNER.stop()
                console.print("\n[yellow]Commit Message Change:[/yellow]")
                if debug:
                    console.print(f"[green]+ New:[/green] {final_message}")
                
                if commit_metrics:
                    console.print("\n[blue]Change Metrics:[/blue]")
                    for metric in commit_metrics:
                        console.print(f"  - {metric.type.value}: {metric.name} ({metric.lines_changed} lines)")
                
                if overwrite and not dry_run:
                    if await amend_commit_message(hash_val, final_message):
                        console.print(f"[green]✓ Successfully rewrote commit {hash_val[:7]}[/green]")
                    else:
                        console.print(f"[red]✗ Failed to rewrite commit {hash_val[:7]}[/red]")
                
                commits.append({
                    'hash': hash_val,
                    'date': date,
                    'message': final_message,
                    'author': author,
                    'category': '🔄 Changes',
                    'metrics': commit_metrics
                })
            except ValueError as e:
                console.print(f"[red]Error processing commit {hash_val[:7]}: {str(e)}[/red]")
                continue
        
        if max_changes:
            filtered_metrics = sorted(all_metrics, key=lambda m: m.lines_changed, reverse=True)[:max_changes]
            filtered_hashes = {commit['hash'] for commit in commits 
                             if any(m in filtered_metrics for m in commit['metrics'])}
            commits = [c for c in commits if c['hash'] in filtered_hashes]
        
        console.print(f"\n[blue]Processed {len(commits)} commits total[/blue]")
        return commits, all_metrics

async def extract_code_changes(commit_hash: str) -> Dict[str, List[str]]:
    """Extract meaningful code changes from a commit."""
    cmd = ['git', 'show', '--format=', '--unified=3', commit_hash, '--', '*.py']
    diff = await arun(cmd)
    
    changes = collections.defaultdict(list)
    current_file = None
    current_block = []
    
    for line in diff.splitlines():
        if line.startswith('diff --git'):
            if current_file and current_block:
                code = '\n'.join(current_block)
                try:
                    ast.parse(code)  # Validate Python syntax
                    changes[current_file].append(code)
                except SyntaxError:
                    pass
            current_file = line.split(' b/')[-1]
            current_block = []
        elif line.startswith('+') and not line.startswith('+++'):
            current_block.append(line[1:])
    
    return dict(changes)

async def generate_changelog(
    days: int=-1,
    branch: str|None = None, 
    show_code: bool = False, 
    overwrite: bool = False,
    dry_run: bool = False, 
    granularity: Granularity = Granularity.MODULE,
    max_changes: int|None = None,
    commit_filters: Dict[str, str] | None = None,  # Add missing kwargs
    min_lines: int = 1,
    file_patterns: List[str] |  None = None
) -> str:
    console = smart_import("mbpy.helpers._display.getconsole")()
    cmd = ['git', 'rev-parse', 'HEAD'] if days == -1 else None
    if days == -1:
        commit_hash = await arun(cmd)
        if commit_hash:
            commits, metrics = await get_commit_history(
                1, commit_hash, overwrite, dry_run, granularity, max_changes,
                commit_filters=commit_filters,
                min_lines=min_lines,
                file_patterns=file_patterns
            )
        else:
            commits, metrics = [], []
    else:
        commits, metrics = await get_commit_history(
            days, branch, overwrite, dry_run, granularity, max_changes,
            commit_filters=commit_filters,
            min_lines=min_lines,
            file_patterns=file_patterns
        )
        
    repo_url = await arun(['git', 'config', '--get', 'remote.origin.url'])
    if repo_url and repo_url.endswith('.git'):
        repo_url = repo_url[:-4]
    
    # Generate changelog content
    lines = [
        "# Changelog",
        "",
        f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        ""
    ]
    
    # Group commits by category
    grouped_commits = collections.defaultdict(list)
    for commit in commits:
        if commit['message'].strip():  # Only include commits with messages
            grouped_commits[commit['category']].append(commit)
    
    # Helper function to format file links
    def format_file_link(filepath: str) -> str:
        """Create both GitHub and local file links."""
        filename = os.path.basename(filepath)
        if repo_url:
            return f"[{filename}]({repo_url}/blob/main/{filepath}) ([local](file://{filepath}))"
        return f"[{filename}](file://{filepath})"

    # Helper function to format changes
    def format_changes(message: str) -> str:
        """Format change messages more cleanly."""
        parts = message.split(" && ")
        formatted = []
        
        for part in parts:
            # Extract file and changes
            if "affecting classes:" in part or "with function changes in:" in part:
                # Split into file changes and details
                file_part, *details = part.split(" affecting classes:" if "affecting classes:" in part 
                                                else "with function changes in:")
                
                # Format file change
                file_name = file_part.split("for ")[-1].strip()
                change_type = "major overhaul to" if "major overhaul" in file_part else \
                            "modified" if "modified" in file_part else "minor fixes for"
                
                formatted.append(f"- **{change_type}** {format_file_link(file_name)}")
                
                # Format details if any
                if details:
                    detail_text = details[0].strip()
                    if "with function changes in:" in detail_text:
                        functions = detail_text.split("with function changes in:")[-1].strip()
                        formatted.append(f"  - 🔧 Functions: `{functions}`")
                    else:
                        classes = detail_text.strip()
                        formatted.append(f"  - 📦 Classes: `{classes}`")
            else:
                formatted.append(f"- {part.strip()}")
                
        return "\n".join(formatted)

    # Single consolidated loop for commit formatting
    for category, commits in grouped_commits.items():
        if not commits:
            continue
            
        lines.append(f"## {category}")
        lines.append("")
        
        for commit in commits:
            date = datetime.strptime(commit['date'], '%Y-%m-%d').strftime('%b %d')
            # Format the commit header and changes
            lines.append(f"### [{date}] Commit {commit['hash'][:7]}")
            formatted_message = format_changes(commit['message'])
            lines.extend(formatted_message.splitlines())
            
            if show_code:
                changes = await extract_code_changes(commit['hash'])
                for file_path, snippets in changes.items():
                    if snippets:  # Only show files with actual changes
                        lines.append(f"\n  Changes in `{file_path}`:")
                        for snippet in snippets:
                            lines.append("  ```python")
                            lines.extend("  " + line for line in snippet.splitlines())
                            lines.append("  ```")
                        lines.append("")  # Add spacing between files
            
            lines.append("")  # Add spacing between commits
        
        lines.append("")  # Add spacing between categories
    
    # Add metrics summary with improved formatting
    if metrics:
        lines.append("\n## Change Metrics Summary\n")
        
        # Group by type and sort by lines changed
        metrics_by_type = collections.defaultdict(list)
        for m in metrics:
            metrics_by_type[m.type].append(m)
            
        for type_, type_metrics in metrics_by_type.items():
            lines.append(f"### {type_.value.title()} Changes")
            sorted_metrics = sorted(type_metrics, key=lambda m: m.lines_changed, reverse=True)
            
            # Only show top changes with significant impact
            significant_changes = [m for m in sorted_metrics if m.lines_changed > 10][:5]
            
            for metric in significant_changes:
                lines.append(f"- {metric.name}")
                lines.append(f"  Lines changed: {metric.lines_changed}")
                if metric.children:
                    # Split long lists of affected items into multiple lines
                    affected = list(metric.children)
                    if len(affected) > 3:
                        lines.append("  Affects:")
                        for item in affected:
                            lines.append(f"    - {item}")
                    else:
                        lines.append(f"  Affects: {', '.join(affected)}")
                lines.append("")  # Add spacing between entries
            
            lines.append("")  # Add spacing between types
    
    try:
        return "\n".join(lines).strip()
    except Exception as e:
        console.print(f"[red]Error generating changelog: {str(e)}[/red]")
        return ""

async def undo_last_commit() -> bool:
    """Undo the last commit but keep the changes staged."""
    console = smart_import("mbpy.helpers._display.getconsole")()
    try:
        # Get the last commit hash first
        last_hash = await arun(['git', 'rev-parse', 'HEAD'])
        if not last_hash:
            console.print("[yellow]No commits to undo[/yellow]")
            return False
            
        # Reset to the previous commit, keeping changes staged
        await arun(['git', 'reset', '--soft', 'HEAD~1'])
        console.print(f"[green]Successfully undid last commit ({last_hash[:7]})[/green]")
        console.print("[dim]Changes are still staged in your working directory[/dim]")
        return True
    except Exception as e:
        console.print(f"[red]Failed to undo last commit: {str(e)}[/red]")
        return False

async def get_git_status() -> Dict[str, str]:
    """Get current git status including staged and unstaged changes."""
    status = {}
    try:
        # Get status in porcelain format for easy parsing
        cmd = ['git', 'status', '--porcelain']
        output = await arun(cmd)
        
        for line in output.splitlines():
            if not line:
                continue
            index_status, work_tree_status = line[:2]
            filepath = line[3:].trim().split(' -> ')[-1].strip('"')
            
            # Parse status codes
            if index_status == 'R':  # Renamed
                old_path = line[3:].split(' -> ')[0].strip()
                status[old_path] = 'remove'
                status[filepath] = 'rename'
            elif index_status == 'A':  # Added
                status[filepath] = 'add'
            elif index_status == 'M':  # Modified
                status[filepath] = 'modify'
            elif index_status == 'D':  # Deleted
                status[filepath] = 'remove'
            
    except Exception as e:
        console = smart_import("mbpy.helpers._display.getconsole")()
        console.print(f"[red]Failed to get git status: {str(e)}[/red]")
    return status

async def add_untracked(branch: str = None, dry_run: bool = False) -> Dict[str, str]:
    """Add untracked files and return a dict of {filepath: status}."""
    try:
        file_status = {}
        cmd = ['git', 'status', '--porcelain']
        output = await arun(cmd)
        
        for line in output.splitlines():
            if not line:
                continue
            status, filepath = line[0:2], line[3:].strip()
            
            # Clean up filepath (handle quotes and renames)
            if ' -> ' in filepath:
                _, filepath = filepath.split(' -> ')
            filepath = filepath.strip('"')
            
            # Only track files that actually exist
            if not os.path.exists(filepath) and status[0] != 'D':
                continue
                
            # Map git status to our simplified status
            if status[0] == 'M' or status[1] == 'M':
                file_status[filepath] = 'modify'
            elif status[0] == 'A':
                file_status[filepath] = 'add'
            elif status[0] == 'D':
                file_status[filepath] = 'remove'
            elif status[0] == '?' and not dry_run:
                file_status[filepath] = 'add'
        
        if not dry_run:
            await arun(['git', 'add', '.'])
            
        return file_status

    except Exception as e:
        console = smart_import("mbpy.helpers._display.getconsole")()
        console.print(f"Failed to process files: {str(e)}")
        return {}

async def get_status_summary(file_status: Dict[str, str]) -> Dict[str, List[str]]:
    """Convert file status dict into a summary by operation."""
    summary = {}
    for filepath, status in file_status.items():
        if status not in summary:
            summary[status] = []
        summary[status].append(filepath)
    return summary
    
async def brief_commit_message(*, dry_run: bool = False) -> str:
    """Generate a concise commit message focused on specific changes."""
    try:
        # await arun(['git', 'add', '.'])
        changes = await get_diff_stats(include_unstaged=False)
    
        if not changes:
            return "No changes to commit"

        significant_changes = []
        for filepath, lines in changes.items():
            if not filepath.endswith('.py'):
                continue
                
            module_changes = await analyze_module_changes(filepath)
            if module_changes['classes']:
                class_names = ', '.join(module_changes['classes'])
                significant_changes.append(f"Updated {class_names} in {os.path.basename(filepath)}")
            elif module_changes['functions']:
                func_names = ', '.join(module_changes['functions'])
                significant_changes.append(f"Modified {func_names} in {os.path.basename(filepath)}")
            elif lines > 50:
                significant_changes.append(f"Major changes to {os.path.basename(filepath)}")
            else:
                significant_changes.append(f"Minor updates to {os.path.basename(filepath)}")

        if not significant_changes:
            return "chore: Minor updates"

        # Keep all significant changes but format them well
        if len(significant_changes) > 5:
            total_files = len(significant_changes)
            base_changes = significant_changes[:4]
            base_changes.append(f"...and {total_files - 4} more files")
            significant_changes = base_changes


        prefix = "feat" if any("Major changes" in change or "Updated" in change for change in significant_changes) else "fix"
        return f"{prefix}: " + " && ".join(significant_changes)

    except Exception as e:
        console = smart_import("mbpy.helpers._display.getconsole")()
        console.print(f"[red]Error generating commit message: {str(e)}[/red]")
        return "fix: Code updates"

async def check_diverging_changes(branch: str = None) -> tuple[bool, str]:
    try:
        has_commits = await arun(['git', 'rev-parse', '--verify', 'HEAD'], debug=False)
        if not has_commits:
            return False, ""

        if not branch:
            branch = await arun(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
        
        remote_exists = await arun(['git', 'ls-remote', '--heads', 'origin', branch])
        if not remote_exists:
            return False, ""
            
        # Fetch latest changes from remote
        await arun(['git', 'fetch', 'origin', branch])
        
        # Check if branches have diverged
        local_commit = await arun(['git', 'rev-parse', 'HEAD'])
        remote_commit = await arun(['git', 'rev-parse', f'origin/{branch}'])
        
        if local_commit != remote_commit:
            diff = await arun(['git', 'diff', f'origin/{branch}...'])
            return True, diff
        
        return False, ""
        
    except Exception as e:
        if "does not have any commits yet" in str(e):
            return False, ""
        console = smart_import("mbpy.helpers._display.getconsole")()
        console.print(f"[red]Error checking diverging changes: {str(e)}[/red]")
        return False, ""

async def git_pull(branch: str = None, rebase: bool = False) -> bool:
    """Pull latest changes from remote with optional rebase."""
    try:
        # Check if we have any commits first
        has_commits = await arun(['git', 'rev-parse', '--verify', 'HEAD'], debug=False)
        if not has_commits:
            return True  # Nothing to pull in new repo
            
        current = await arun(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
        if branch:
            try:
                await arun(['git', 'branch', '--set-upstream-to', f'origin/{branch}', current])
            except Exception:
                pass  # Ignore if remote branch doesn't exist yet
        
        cmd = ['git', 'pull']
        if rebase:
            cmd.append('--rebase')
        if branch:
            cmd.extend(['origin', branch])
        
        output = await arun(cmd)
        if "Already up to date" in output:
            return True
        if "Refusing to merge unrelated histories" in output:
            output = await arun(['git', 'pull', '--allow-unrelated-histories']) 
        return "Already up to date" in output or not output
    except Exception as e:
        if "does not have any commits yet" in str(e):
            return True
        console = smart_import("mbpy.helpers._display.getconsole")()
        console.print(f"[red]Failed to pull changes: {str(e)}[/red]")
        return False

async def create_new_branch(base_branch: str, new_branch: str) -> bool:
    """Create a new branch from the specified base branch."""
    try:
        # Create and checkout new branch
        await arun(['git', 'checkout', '-b', new_branch, base_branch])
        return True
    except Exception as e:
        console = smart_import("mbpy.helpers._display.getconsole")()
        console.print(f"[red]Failed to create new branch: {str(e)}[/red]")
        return False

async def git_add_commit_push(branch: str = None, dry_run: bool = False) -> bool:
    """Add, commit and push changes with proper error handling."""
    console = smart_import("mbpy.helpers._display.getconsole")()
    Prompt = smart_import("rich.prompt.Prompt")
    spinner = smart_import("mbpy.helpers._display.SPINNER")()
    branch = branch or await arun(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    try:
        # Check for diverging changes first
        has_diverged, diff = await check_diverging_changes(branch)
        if has_diverged:
            spinner.stop()
            console.print(f"[yellow]Warning: Your branch has diverged from origin {branch}[/yellow]")
            console.print("\n[blue]Diverging changes:[/blue]")
            console.print(diff)
            
            if not dry_run:
                console.print("\nYou have several options:")
                console.print("1. Pull and rebase (recommended)")
                console.print("2. Create a new branch")
                console.print("3. Force push (not recommended)")
                console.print("4. Cancel")
                
                choice = Prompt.ask(
                    "How would you like to proceed?",
                    choices=['1', '2', '3', '4'],
                    default='1'
                )
                
                if choice == '1':
                    console.print("\nAttempting to pull and rebase...")
                    try:
                        out = await arun(['git', 'pull', '--rebase', 'origin', branch])
                    except Exception as e:
                        console.print(f"[red]Failed to rebase: {str(e)}[/red]")
                        console.print("[yellow]Please resolve conflicts manually and try again[/yellow]")
                        return False
                elif choice == '2':
                    new_branch = click.prompt("Enter new branch name")
                    try:
                        await arun(['git', 'checkout', '-b', new_branch])
                        branch = new_branch
                        console.print(f"[green]Created and switched to new branch: {new_branch}[/green]")
                    except Exception as e:
                        console.print(f"[red]Failed to create new branch: {str(e)}[/red]")
                        return False
                elif choice == '3':
                    if not click.confirm("[red]WARNING: Force push will overwrite remote changes. Continue?[/red]"):
                        return False
                else:
                    console.print("Operation cancelled")
                    return False

        # Add untracked files and verify status
        file_status = await add_untracked(branch, dry_run=True)  # Always check without adding
        
        if dry_run:
            # Show what would be changed
            if file_status:
                by_status = collections.defaultdict(list)
                for filepath, status in file_status.items():
                    by_status[status].append(filepath)
                
                console.print("[yellow]DRY RUN - No changes will be made[/yellow]\n")
                for status, files in by_status.items():
                    if files:
                        console.print(f"\nFiles to be {status}ed:")
                        for f in files:
                            console.print(f"  - {f}")
                
                msg = await brief_commit_message(dry_run=True)
                console.print(f"\n[bold cyan]Commit message would be: [/bold cyan]\n{msg}")
            else:
                console.print("\n[yellow]No changes detected[/yellow]")
            return True

      
        if not file_status:
            console.print("[yellow]No changes to commit[/yellow]")
            return False

        if dry_run:
            console.print("[yellow]Dry run enabled. No changes will be pushed.[/yellow]")
            if file_status:
                by_status = collections.defaultdict(list)
                for file, status in file_status.items():
                    by_status[status].append(file)
                
                for status, files in by_status.items():
                    console.print(f"[blue]Files that would be {status}ed:[/blue]")
                    for f in files:
                        console.print(f"  - {f}")
                        
            cl = await brief_commit_message(dry_run=True)
            console.print(f"[blue]Dry run commit message:[/blue] {cl}")
            return True

        # Attempt commit
        cl = await brief_commit_message()
        commit_cmd = ['git', 'commit', '-m', cl]
        try:
            out = await arun(commit_cmd)

            console.print(f"\n[blue]Commit Message:[/blue] \n{cl}")
        except Exception as e:
            if "nothing to commit" in str(e).lower():
                console.print("[yellow]No changes to commit[/yellow]")
                return False
            raise
      

        # Push changes
        push_cmd = ['git', 'push']
        if not  branch:
            branch = await arun(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
        push_cmd.extend(['origin', branch])
        
        try:
            out = await arun(push_cmd)
            if "rejected" in out:
                console.print("[yellow]Push rejected: Remote contains work you do not have locally. Attempting to pull changes in a new branch...[/yellow]")
                from mbpy.helpers._git_ctx import gitpush
                with gitpush() as out:
                    if "rejected" in out:
                    
                        cmd = f"git checkout -b {out.ctx.local_branch} && git pull origin {branch} && git push origin {branch}"
                        out = await arun(cmd)
                        if "unrelated histories" in out:
                            console.print(out)
                            cmd = f"git pull origin {branch} --allow-unrelated-histories && git push origin {branch}"
                            out = await arun(cmd)
                        if "error" in out or "fatal" in out:
                            console.print(out)
                            console.print("[red]Error during push operation. Please check the output above for details.[/red]")
                            return False
                        return True
                    if "error" in out:
                        console.print(out)
                        console.print("[red]Error during push operation. Please check the output above for details.[/red]")
                        return False
                    


                console.print("[green]Successfully pushed changes[/green]")
                return True
        except Exception as e:
            import traceback
            traceback.print_exc()
            if "non-fast-forward" in str(e):
                console.print("[red]Push failed: Remote contains work you do not have locally[/red]")
                console.print("[yellow]Hint: Try pulling changes first or create a new branch[/yellow]")
            else:
                console.print(f"[red]Push failed: {str(e)}[/red]")
            return False

    except Exception as e:
        console.print(f"[red]Error during git operations: {str(e)}[/red]")
        return False

@click.command("git",no_args_is_help=True)
@click.option('-cl','--change-log',is_flag=True,help='Generate changelog')
@click.option('--days', type=int, default=30, help='Number of days to look back')
@click.option('--branch', '-b', type=str, help='Branch to analyze or push to')
@click.option('--output', type=click.Path(), help='Output file path')
@click.option('--show-code', is_flag=True, help='Include code changes in changelog')
@click.option('--overwrite', is_flag=True, help='DANGER: Rewrites commit messages - use with caution')
@click.option('--dry-run', is_flag=True, help='Preview changes without applying them')
@click.option('--undo', is_flag=True, help='Undo the last commit')
@click.option('--push', '-p', is_flag=True, help='Push changes after generating changelog')
@click.option('--max-changes', type=int, help='Maximum number of commits to process')
@click.option('--granularity', 
              type=click.Choice([g.value for g in Granularity], case_sensitive=False),
              default=Granularity.MODULE.value,
              help='Level of detail for change messages')
@base_args()
async def main(change_log: bool,
    days: int, branch: str, output: str, show_code: bool, 
               overwrite: bool, dry_run: bool, max_changes: int,
               undo: bool, push: bool, granularity: str):
    """Git operations including changelog generation and pushing changes."""
    if TYPE_CHECKING:
            from mbpy.helpers._display import SPINNER
            from mbpy.helpers._display import getconsole
            from rich.markdown import Markdown
    else:
        console = smart_import("mbpy.helpers._display.getconsole")()
        Markdown = smart_import("rich.markdown.Markdown")
        SPINNER = smart_import("mbpy.helpers._display.SPINNER")
    try:
        # Validate working directory
        if not os.path.exists(os.getcwd()):
            console.print("[red]Error: Current working directory does not exist[/red]")
            return
            
        if not await is_git_repo():
            console.print("[red]Error: Not a git repository[/red]")
            return

        if undo:
            await undo_last_commit()
            return

        if dry_run:
            SPINNER().stop()
            console.print("[yellow]DRY RUN - No changes will be made[/yellow]\n")
            SPINNER().start()
            await asyncio.sleep(1)
            
            
        # Only push if explicitly requested
        if push:
           return await git_add_commit_push(branch, dry_run)
        changelog = await generate_changelog(
            days, branch, show_code, overwrite, dry_run,
            granularity=Granularity(granularity),
            max_changes=max_changes
        )
        
        if not changelog.strip():
            console.print("[yellow]No changes found in the specified time period[/yellow]")
            return
        if change_log:
            output = output or 'CHANGELOG.md'
        if output:
            with open(output, 'w') as f:
                f.write(changelog)
            console.print(f"[green]Changelog written to {output}[/green]")
        else:
            console.print(Markdown(changelog))
    except Exception as e:
        console.print(f"[red]Error generating changelog: {str(e)}[/red]")

if __name__ == '__main__':
    from mbpy.cli import cli
    cli.add_command(main)
    cli()