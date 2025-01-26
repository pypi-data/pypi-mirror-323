from typing import TYPE_CHECKING
from typing_extensions import Callable, ParamSpec, TypeVar

from mbpy.import_utils import smart_import

if TYPE_CHECKING:
        import logging
        from functools import partial

        import rich_click as click

        from mbpy.cli import AsyncGroup, get_help_config
else:
    from functools import partial

    click = smart_import('rich_click')
    logging = smart_import('logging')

    AsyncGroup = smart_import('mbpy.cli.AsyncGroup')
    get_help_config = smart_import('mbpy.cli.get_help_config')
P = ParamSpec("P")
R = TypeVar("R")
def wraps(func: Callable[P, R]) -> Callable[...,Callable[P, R]]:
    """Decorator factory to preserve function metadata when wrapping a function.

    Args:
        func (Callable[P, R]): Function to be wrapped.

    Returns:
        Callable[...,Callable[P, R]]: Decorator function preserving metadata.

    Examples:
        ```python
        @wraps(func)
        def my_decorator(func):
            # Decorator implementation
            pass
        ```

    Notes:
        - Preserves function metadata when wrapping a function
        - Useful for decorators that wrap other functions
    """
    def decorator(wrapper: Callable[...,Callable[P, R]]) -> Callable[P, R]:
        wrapper.__name__ = func.__name__
        wrapper.__module__ = func.__module__
        wrapper.__doc__ = func.__doc__
        wrapper.__annotations__ = func.__annotations__
        return wrapper
    return decorator
def cli(*args,commands: tuple|list, **kwargs):
    """Command Line Interface (CLI) decorator for handling subcommands and CLI operations.

    This decorator transforms a function into a CLI command handler, providing command registration,
    execution flow control, and basic debugging support.

    Args:
        *args: Variable positional arguments passed to the decorator.
        commands (tuple|list): Collection of command functions to be registered and executed.
        **kwargs: Variable keyword arguments, supporting:
            - debug (bool): Enable debug mode logging when True.
            - ctx: Command context object for subcommand handling.

    Returns:
        Union[Context, Awaitable]: Returns either the command context for subcommands
        or runs the first command asynchronously if no subcommand is specified.

    Examples:
        ```python
        @cli(commands=[cmd1, cmd2])
        async def my_cli():
            # CLI implementation
            pass

        @cli(commands=[cmd1, cmd2], debug=True)
        async def debug_cli():
            # CLI with debug logging
            pass
        ```

    Notes:
        - Automatically configures debug logging when debug flag is set
        - Handles subcommand routing through context object
        - Falls back to first command execution if no subcommand specified
        - Integrates with smart console output handling

    Raises:
        ImportError: If console dependencies cannot be imported
        RuntimeError: If command execution fails
    """
    @click.rich_config(help_config=get_help_config())
    @click.help_option("-h", "--help")
    @click.group("mbpy", cls=AsyncGroup)
    @click.pass_context
    @click.option(
        "-e",
        "--env",
        default=None,
        help="Specify the python, hatch, conda, or mbnix environment",
    )
    @click.option(
        "-d",
        "--debug",
        is_flag=True,
        help="Enable debug logging",
    )
    def _cli(ctx: click.RichContext, env, debug):
        import sys

        from mbpy.cli import run_async

        console = smart_import('mbpy.helpers._display.getconsole')()
        if sys.flags.debug or debug:
            logging.basicConfig(level=logging.DEBUG, force=True)

        if ctx.invoked_subcommand:
            return ctx

        console.print("No subcommand specified. Showing dependencies:")
        return run_async(commands[0])

    for command in commands:
        _cli.add_command(command)
    return _cli(**kwargs)

@wraps(cli)
def entrypoint(*commands) -> click.RichGroup:

    return  partial(cli,commands=commands)
    

