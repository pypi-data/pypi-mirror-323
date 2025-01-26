"""This module contains the pinput function for displaying styled input prompts."""

import sys
from .styles import style


def pinput(prompt: str,
           customprefix: str = ">>",
           prefixstyle: str = "",
           autoquestion: bool = True,
           lfbefore: bool = True) -> str:
    """
    Display a styled input prompt with a custom prefix.

    :param prompt: The input prompt message.
    :type prompt: str
    :param customprefix: A custom prefix for the input prompt. Defaults to ">>".
    :type customprefix: str
    :param prefixstyle: The style to apply to the prefix using `colourup.style`. Defaults to no style.
    :type prefixstyle: str
    :param autoquestion: Whether to automatically change the prefix if a question mark is found at the end of the prompt. Defaults to True.
    :type autoquestion: bool
    :param lfbefore: Whether to add a line feed (\n) before the prompt. Defaults to True.
    :type lfbefore: bool
    :return: The user's input after displaying the prompt.
    :rtype: str
    """

    # To check if the prefix has been overriden, to not override it again.
    if autoquestion and prompt[-1] == "?" and customprefix == ">>":
        customprefix = "?>"

    sys.stdout.write(f"{"\n" if lfbefore else ""}{prompt}{style.RESET}\n{prefixstyle}{customprefix}{style.RESET} ")

    sys.stdout.flush()
    return sys.stdin.readline().strip()
