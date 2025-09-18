"""
Tests for main module functionality.
"""

from unittest.mock import patch, call
import sys
import os

# Add the project root to the path so we can import main
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import main


class TestMainFunction:
    """Test the main function greeting functionality."""

    def test_main_prints_greeting(self, capsys):
        """Test that main function prints the expected greeting."""
        main.main()

        captured = capsys.readouterr()
        output_lines = captured.out.strip().split("\n")

        # Verify all expected greeting lines are present
        expected_lines = [
            "🔍 Welcome to Brave Agent!",
            "Your intelligent research assistant powered by Brave Search.",
            "Ready to help you discover and analyze information from the web.",
            "Type your research queries and let's get started!",
        ]

        assert len(output_lines) == len(expected_lines)
        for expected, actual in zip(expected_lines, output_lines):
            assert expected == actual

    def test_main_function_exists(self):
        """Test that the main function is defined and callable."""
        assert hasattr(main, "main")
        assert callable(main.main)

    @patch("builtins.print")
    def test_main_uses_print_statements(self, mock_print):
        """Test that main function uses print statements correctly."""
        main.main()

        # Verify print was called 4 times with expected messages
        expected_calls = [
            call("🔍 Welcome to Brave Agent!"),
            call("Your intelligent research assistant powered by Brave Search."),
            call("Ready to help you discover and analyze information from the web."),
            call("Type your research queries and let's get started!"),
        ]

        mock_print.assert_has_calls(expected_calls)
        assert mock_print.call_count == 4

    def test_main_as_script(self):
        """Test that main module can be executed as a script."""
        # Verify that the if __name__ == "__main__" block exists
        with open(
            os.path.join(os.path.dirname(__file__), "..", "..", "main.py"), "r"
        ) as f:
            content = f.read()
            assert 'if __name__ == "__main__":' in content
            assert "main()" in content
