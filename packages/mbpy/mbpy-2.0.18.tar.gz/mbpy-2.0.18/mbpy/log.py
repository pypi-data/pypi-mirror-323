import logging
import logging.config
import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Generic, Literal, TypeVar, overload

from mbpy.helpers._display import SPINNER
from mbpy.helpers.traverse import find_mb


def caller(depth=1, default='__main__'):
    try:
        return sys._getframemodulename(depth + 1) or default
    except AttributeError:  # For platforms without _getframemodulename()
        pass
    try:
        return sys._getframe(depth + 1).f_globals.get('__name__', default)
    except (AttributeError, ValueError):  # For platforms without _getframe()
        pass
    return None

if TYPE_CHECKING:
    from types import ModuleType

def parentmodule() -> "ModuleType":
    return sys.modules[caller() or "__main__"]

def parentname() -> str:
    return caller()

def parentfile() -> Path:
    return Path(sys.modules[parentname()].__file__).resolve()



def isverbose() -> bool:
    import sys
    return any(arg in sys.argv for arg in ("-v", "--verbose","-d", "--debug"))

def isvverbose() -> bool:
    import sys
    return any(arg in sys.argv for arg in ("-vv", "--vverbose","-dd", "--ddebug"))


def getlevel() -> int:
    if isverbose():
        return logging.DEBUG
    if isvverbose():
        return logging.INFO
    
    return logging.getLogger("rich").getEffectiveLevel()

log = logging.log

def getlogpath() -> Path:
    p =  (find_mb(parentfile().parent) /  parentname()).with_suffix(".log")
    return p

SHOW_TRACEBACKS = os.getenv("TRACEBACKS_SHOW") or False
SHOW_LOCALS = os.getenv("TRACEBACKS_SHOW_LOCALS") or False
# Logging configuration dictionary
LOGGING_CONFIG: Dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "detailed": {
            "format": "%(message)s",
            "datefmt": "[%X]",
        },
    },
    "handlers": {
        "rich": {
            "class": "mbpy.helpers._logging.RichHandler",
            "rich_tracebacks": SHOW_TRACEBACKS,
            "tracebacks_show_locals": SHOW_LOCALS,
            "show_time": True,
            "show_level": True,
            "show_path": True,
        },
        "file": {
            "class": "logging.FileHandler",
            # "formatter": "detailed",
            "filename": getlogpath(),
            "mode": "a",
        },
    },
    "loggers": {
        "rich": {  
            "handlers": ["rich", "file"],
            "level": getlevel(),
            "propagate": False,
        },
    },
}
def setup_logging(show_stack: bool = None, show_locals: bool =None) -> None:
    if show_stack is not None:
        global SHOW_TRACEBACKS
        SHOW_TRACEBACKS = show_stack
    if show_locals is not None:
        global SHOW_LOCALS
        SHOW_LOCALS = show_locals
    logging.config.dictConfig(LOGGING_CONFIG)
    
if TYPE_CHECKING:
    from mbpy.collect import wraps
else:
    wraps = lambda *args, **kwargs: lambda f: f

setup_logging()
# Update the existing code
if isverbose():
    LOGGING_CONFIG["loggers"]["rich"]["level"] = "DEBUG"
if isvverbose():
    LOGGING_CONFIG["handlers"]["console"]["formatter"] = "detailed"

LevelT = TypeVar("LevelT", bound=Literal["DEBUG", "INFO", "WARNING", "ERROR", "FATAL"])
class Log(Generic[LevelT]):
    level: LevelT
    @classmethod
    def set(cls):
        logging.basicConfig(level=cls.level,force=True)
        return cls
    @wraps(logging.log)
    @classmethod
    def log(cls, *args, **kwargs):
        if getlevel() > getattr(logging, cls.level.upper()):
            return cls
        if args or kwargs:
            SPINNER().stop()
            logging.getLogger("rich").log(getlevel(), *args, **kwargs, stack_info=SHOW_TRACEBACKS,stacklevel=3)
            logging.getLogger("file").log(getlevel(), *args, **kwargs, stack_info=SHOW_TRACEBACKS,stacklevel=3)
        return cls
    @classmethod
    def __class_getitem__(cls, level: LevelT):
        cls.level = level
        return cls
    
    @classmethod
    def __bool__(cls):
        return getlevel() <= getattr(logging, cls.level.upper())
    
DEBUG=Literal["DEBUG"]
INFO=Literal["INFO"]
WARNING=Literal["WARNING"]
ERROR=Literal["ERROR"]
FATAL=Literal["FATAL"]

@wraps(logging.debug, bool | Log["DEBUG"])
def debug(*args, **kwargs)-> Log["DEBUG"] | bool:
    """Initialize or log a debug message.
    
    Use debug or debug() to check if debug level is enabled.

    Examples:
        >>> debug()  # Returns Log["debug"] for configuration
        >>> if debug():  # Check if debug level is enabled
        ...     print("Will only print if debug level is enabled")
        >>> debug.set()  # Set logging level to DEBUG
        >>> debug.log("Processing file")  # Log a message
        DEBUG: Processing file

    """
    if not args and not kwargs:
        return Log["DEBUG"]()
    if getlevel() > logging.DEBUG:
        return Log["DEBUG"]()
    if args or kwargs:

        return Log["DEBUG"]().log(*args, **kwargs)
    
    return Log["DEBUG"]()

debug.__bool__ = lambda: getlevel() <= logging.DEBUG

@wraps(logging.info,bool | Log["INFO"])
def info(*args, **kwargs) -> Log["INFO"] | bool:
    """Initialize or log an info message.

    Examples:
        >>> info()  # Returns Log["info"] for configuration
        >>> if info():  # Check if info level is enabled
        ...     print("Will only print if info level is enabled")
        >>> info.set()  # Set logging level to INFO
        >>> info.log("Processing file")  # Log a message
        INFO: Processing file

    """
    if args is None and kwargs is None:
        return Log["info"]()
    if getlevel() > logging.INFO:
        return Log["info"]()
    if args or kwargs:
        return Log["info"]().log(*args, **kwargs)
    return Log["info"]()


@wraps(logging.warning)
def warning(*args, **kwargs) -> None:
    """Initialize or log a warning message.

    Examples:
        >>> warning()  # Returns Log["warning"] for configuration
        >>> if warning():  # Check if warning level is enabled
        ...     print("Will only print if warning level is enabled")
        >>> warning.set()  # Set logging level to WARNING
        >>> warning.log("File not found")  # Log a message
        WARNING: File not found
        >>> warning("File not found", path="/tmp/missing.txt")
        WARNING: File not found (/tmp/missing.txt)

    """
    if args is None and kwargs is None:
        return Log["warning"]()
    if getlevel() > logging.WARNING:
        return Log["warning"]()
    if args or kwargs:
        return Log["warning"]().log(*args, **kwargs)
    return Log["warning"]()

@wraps(logging.error)
def error(*args, **kwargs)-> Log["ERROR"]:
    """Initialize or log an error message.

    Examples:
        >>> error()  # Returns Log["error"] for configuration
        >>> if error():  # Check if error level is enabled
        ...     print("Will only print if error level is enabled")
        >>> error.set()  # Set logging level to ERROR
        >>> error.log("Failed to connect")  # Log a message
        ERROR: Failed to connect

    """
    if args is None and kwargs is None:
        return Log["error"]()
    if getlevel() > logging.ERROR:
        return Log["error"]()
    if args or kwargs:
        return Log["error"]().log(*args, **kwargs)
    return Log["error"]()
    


@wraps(logging.fatal)
def fatal(*args, **kwargs)-> Log["FATAL"]:
    """Initialize or log a fatal message.

    Examples:
        >>> fatal()  # Returns Log["fatal"] for configuration
        >>> if fatal():  # Check if fatal level is enabled
        ...     print("Will only print if fatal level is enabled")
        >>> fatal.set()  # Set logging level to FATAL
        >>> fatal.log("Critical system failure")  # Log a message
        FATAL: Critical system failure

    """
    if args is None and kwargs is None:
        return Log["fatal"]()
    if getlevel() > logging.FATAL:
        return Log["fatal"]()
    if args or kwargs:
        return Log["fatal"]().log(*args, **kwargs)