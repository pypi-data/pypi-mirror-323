"""
This module initializes the `styles` package, which includes foreground colors,
background colors, and text styles for terminal applications.

Modules:
    fg: Foreground color codes.
    bg: Background color codes.
    style: Text style codes.

Initialization:
    Automatically initializes `colorama` for cross-platform terminal styling.

Attributes:
    __all__: A list of all submodules included in the package (`fg`, `bg`, `style`).

Note:
    `colorama.init()` is called with `autoreset=False` to preserve manual control of styles.
"""
from . import fg
from . import bg
from . import style

import colorama

colorama.init(autoreset=False)

__all__ = [
    fg,
    bg,
    style,
]
