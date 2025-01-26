"""
This module provides text style codes for terminal styling.

Each constant represents an ANSI escape sequence for applying styles to text.

Attributes:
    BOLD (str): Makes the text bold.
    ITALIC (str): Makes the text italic (not widely supported).
    UNDERLINE (str): Underlines the text.
    INVERTED (str): Inverts the background and foreground colors.
    RESET (str): Resets all styles to default.
"""
BOLD: str = "\033[1m"
ITALIC: str = "\033[3m"
UNDERLINE: str = "\033[4m"
INVERTED: str = "\033[7m"
RESET: str = "\033[0m"
