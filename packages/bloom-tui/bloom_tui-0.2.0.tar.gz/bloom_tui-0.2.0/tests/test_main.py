import unittest
from unittest.mock import patch
import colourup
import io


class TestColourup(unittest.TestCase):
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_title(self, mock_stdout):
        colourup.title("Test Title", "-", 8, True)

        expected_output = "\n-------- Test Title --------\n"
        self.assertEqual(mock_stdout.getvalue(), expected_output)

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_title_style_and_spacing(self, mock_stdout):
        colourup.title("Styled Title", borderchar="*", borderlen=5, spacesbetween=2,
                       stylebefore=f"{colourup.styles.style.BOLD}", styleafter=f"{colourup.styles.style.ITALIC}", lfbefore=False)

        expected_output = f"{colourup.styles.style.BOLD}*****{colourup.styles.style.RESET}  Styled Title  {colourup.styles.style.ITALIC}*****{colourup.styles.style.RESET}"
        self.assertEqual(mock_stdout.getvalue().strip(), expected_output)

    @patch("sys.stdin")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_pinput_custom_prompt(self, mock_stdout, mock_stdin):
        mock_stdin.readline.return_value = "test"

        result = colourup.pinput("What's your name?")
        self.assertEqual(result, "test")

        expected_output = f"\nWhat's your name?{colourup.styles.style.RESET}\n?>{colourup.styles.style.RESET} "
        self.assertEqual(mock_stdout.getvalue(), expected_output)

        mock_stdin.readline.assert_called_once()

    @patch("sys.stdin")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_pinput_default(self, mock_stdout, mock_stdin):
        mock_stdin.readline.return_value = "test"

        result = colourup.pinput("Question?", autoquestion=False)
        self.assertEqual(result, "test")

        expected_output = f"\nQuestion?{colourup.styles.style.RESET}\n>>{colourup.styles.style.RESET} "
        self.assertEqual(mock_stdout.getvalue(), expected_output)

        mock_stdin.readline.assert_called_once()

    @patch("sys.stdin")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_pinput_lfbefore(self, mock_stdout, mock_stdin):
        mock_stdin.readline.return_value = "test"

        result = colourup.pinput("Inline Question?", lfbefore=False)
        self.assertEqual(result, "test")

        expected_output = f"Inline Question?{colourup.styles.style.RESET}\n?>{colourup.styles.style.RESET} "
        self.assertEqual(mock_stdout.getvalue(), expected_output)

    @patch("sys.stdin")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_pinput_custom_prefix_style(self, mock_stdout, mock_stdin):
        mock_stdin.readline.return_value = "test"

        result = colourup.pinput("Styled prompt?", customprefix="*", prefixstyle=f"{colourup.styles.style.BOLD}")
        self.assertEqual(result, "test")

        expected_output = f"\nStyled prompt?{colourup.styles.style.RESET}\n{colourup.styles.style.BOLD}*{colourup.styles.style.RESET} "
        self.assertEqual(mock_stdout.getvalue(), expected_output)

        mock_stdin.readline.assert_called_once()


if __name__ == "__main__":
    unittest.main()
