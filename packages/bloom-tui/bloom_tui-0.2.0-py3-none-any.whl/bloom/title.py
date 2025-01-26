"""This module contains the code for the title function."""

import sys
from .styles import style

def title(text: str,
          borderchar: str = "=",
          borderlen: int = 10,
          lfbefore=True,
          stylebefore: str="",
          styleafter: str="",
          spacesbetween: int=1) -> None:
    """
    Create a centered text with decorative borders.

    :param text: The text to display.
    :type text: str
    :param borderchar: The character used for the border.
    :type borderchar: str
    :param borderlen: The length of the border.
    :type borderlen: int
    :param lfbefore: Whether to add a line feed (\\n) before the title.
    :type lfbefore: bool
    :param stylebefore: The style to apply to the title before the border. Will reset automatically after the first border segment.
    :type stylebefore: str
    :param styleafter: The style to apply to the title after the border. Will reset automatically after the last border segment.
    :type styleafter: str
    :param spacesbetween: The amount of spaces to add between the title and the border. Use 0 for none.
    :type spacesbetween: int

    :return: None
    :rtype: NoneType
    """

    border = f"{borderchar * borderlen}"
    sys.stdout.write(f"{"\n" if lfbefore else ""}{stylebefore}{border}{style.RESET if stylebefore else ""}{" "*spacesbetween}{text}{" "*spacesbetween}{styleafter}{border}{style.RESET if styleafter else ""}\n")
