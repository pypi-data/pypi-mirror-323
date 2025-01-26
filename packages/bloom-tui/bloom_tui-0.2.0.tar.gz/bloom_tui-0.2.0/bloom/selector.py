"""Create a selector with several options for your TUI application."""
import getch
import sys

from .utils import cursor
from .styles import fg, style


class Selector(object):
    """
    Creates a terminal-based selector with multiple options, allowing navigation with keyboard inputs.

    :param question: The question or prompt to display above the options.
    :type question: str
    :param options: A list of options to display in the selector. Minimum of two options required.
    :type options: list[str]
    """

    def __init__(self, question: str, options: list[str]) -> None:
        self.question = question
        if len(options) < 2:
            raise ValueError("Selector must have at least two options.")
        self.options = options
        self.selected_option = 0

    @staticmethod
    def __handle_keystroke() -> str:
        """
        Handles keyboard presses and returns the pressed key.

        :return: The key pressed by the user. Returns "up", "down", or "enter" for special keys (arrow keys, Enter).
        :rtype: str
        """
        first_char = getch.getch()
        if first_char == '\x1b':
            second_char = getch.getch()
            third_char = getch.getch()
            if second_char == '[':
                if third_char == 'A':
                    return 'up'
                elif third_char == 'B':
                    return 'down'
        elif first_char == '\r' or first_char == '\n':
            return 'enter'
        else:
            return first_char

    def __update(self) -> None:
        """
        Updates the current selected option based on keyboard input. Handles navigation logic for `up`, `down`, and `enter`.
        """
        sys.stdout.write(f"\n{cursor.HIDE}")
        self.__print_selector()
        while True:
            key_pressed = self.__handle_keystroke()

            if key_pressed == "up":
                self.selected_option -= 1
                if self.selected_option < 0:
                    self.selected_option = len(self.options) - 1
                self.__print_selector(self.selected_option)

            if key_pressed == "down":
                self.selected_option += 1
                if self.selected_option >= len(self.options):
                    self.selected_option = 0
                self.__print_selector(self.selected_option)

            if key_pressed == "enter":
                break

    def __print_selector(self, selected=0) -> None:
        """
        Displays the selector with the current selected option highlighted.

        :param selected: The index of the currently selected option.
        :type selected: int
        """
        output = f"{self.question}\n"
        for option in self.options:
            if option == self.options[selected]:
                output += f"  {fg.BGREEN}>{style.RESET} {option}\n"
            else:
                output += f"  {fg.BBLACK}- {option}{style.RESET}\n"
        sys.stdout.write(output)
        sys.stdout.write(f"{cursor.MOVE_UP * (len(self.options) + 1)}\r")

    def __reset_output(self) -> None:
        """
        Resets stdout to the original state by removing the selector interface.
        """
        for _ in range(len(self.options) + 1):
            sys.stdout.write(f"{cursor.MOVE_DOWN}")
        for _ in range(len(self.options) + 1):
            sys.stdout.write(f"{cursor.ERASE_LINE}")
            sys.stdout.write(f"{cursor.MOVE_UP}")
        sys.stdout.write(f"{cursor.SHOW}")
        sys.stdout.flush()

    def invoke(self, lfbefore: bool = True) -> int:
        """
        Invokes the selector, waits for user input, and returns the selected option index.

        :param lfbefore: Whether to add a blank line before displaying the selector.
        :type lfbefore: bool
        :return: The index of the selected option.
        :rtype: int
        """
        if lfbefore:
            sys.stdout.write(f"\n")
        self.__update()
        self.__reset_output()
        return self.selected_option


if __name__ == "__main__":
    selector = Selector("How are you?", ["Good", "Great", "Okay", "Bad"])
    hello = selector.invoke()
    print(hello)
