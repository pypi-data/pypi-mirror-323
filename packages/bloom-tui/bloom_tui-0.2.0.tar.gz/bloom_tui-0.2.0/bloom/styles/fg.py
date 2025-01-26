"""
This module provides foreground color codes for terminal styling.

Each constant represents an ANSI escape sequence for setting the foreground (text) color.

Attributes:
    BLACK (str): Black text.
    RED (str): Red text.
    GREEN (str): Green text.
    YELLOW (str): Yellow text.
    BLUE (str): Blue text.
    MAGENTA (str): Magenta text.
    CYAN (str): Cyan text.
    WHITE (str): White text.
    BBLACK (str): Bright black (gray) text.
    BRED (str): Bright red text.
    BGREEN (str): Bright green text.
    BYELLOW (str): Bright yellow text.
    BBLUE (str): Bright blue text.
    BMAGENTA (str): Bright magenta text.
    BCYAN (str): Bright cyan text.
    BWHITE (str): Bright white text.
"""
BLACK: str = "\033[30m"
RED: str = "\033[31m"
GREEN: str = "\033[32m"
YELLOW: str = "\033[33m"
BLUE: str = "\033[34m"
MAGENTA: str = "\033[35m"
CYAN: str = "\033[36m"
WHITE: str = "\033[37m"

BBLACK: str = "\033[90m"
BRED: str = "\033[91m"
BGREEN: str = "\033[92m"
BYELLOW: str = "\033[93m"
BBLUE: str = "\033[94m"
BMAGENTA: str = "\033[95m"
BCYAN: str = "\033[96m"
BWHITE: str = "\033[97m"
