"""
This module provides background color codes for terminal styling.

Each constant represents an ANSI escape sequence for setting the background color of text.

Attributes:
    BLACK (str): Black background.
    RED (str): Red background.
    GREEN (str): Green background.
    YELLOW (str): Yellow background.
    BLUE (str): Blue background.
    MAGENTA (str): Magenta background.
    CYAN (str): Cyan background.
    WHITE (str): White background.
    BBLACK (str): Bright black (gray) background.
    BRED (str): Bright red background.
    BGREEN (str): Bright green background.
    BYELLOW (str): Bright yellow background.
    BBLUE (str): Bright blue background.
    BMAGENTA (str): Bright magenta background.
    BCYAN (str): Bright cyan background.
    BWHITE (str): Bright white background.
"""
BLACK: str = "\033[40m"
RED: str = "\033[41m"
GREEN: str = "\033[42m"
YELLOW: str = "\033[43m"
BLUE: str = "\033[44m"
MAGENTA: str = "\033[45m"
CYAN: str = "\033[46m"
WHITE: str = "\033[47m"
BBLACK: str = "\033[100m"
BRED: str = "\033[101m"
BGREEN: str = "\033[102m"
BYELLOW: str = "\033[103m"
BBLUE: str = "\033[104m"
BMAGENTA: str = "\033[105m"
BCYAN: str = "\033[106m"
BWHITE: str = "\033[107m"
