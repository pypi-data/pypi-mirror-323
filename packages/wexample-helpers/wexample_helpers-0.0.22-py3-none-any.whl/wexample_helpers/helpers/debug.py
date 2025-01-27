from typing import Optional, TYPE_CHECKING

from wexample_helpers.enums.debug_path_style import DebugPathStyle
from wexample_helpers.helpers.trace import trace_print

if TYPE_CHECKING:
    pass


def debug_trace(
    path_style: DebugPathStyle = DebugPathStyle.FULL,
    truncate_stack: int = 0,
    paths_map: Optional[dict] = None
) -> None:
    trace_print(
        truncate_stack=truncate_stack,
        path_style=path_style,
        paths_map=paths_map
    )


def debug_trace_and_die(
    path_style: DebugPathStyle = DebugPathStyle.FULL,
    truncate_stack: int = 0,
    paths_map: Optional[dict] = None
) -> None:
    debug_trace(
        path_style=path_style,
        truncate_stack=truncate_stack,
        paths_map=paths_map
    )
    exit(1)

