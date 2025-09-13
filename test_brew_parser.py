#!/usr/bin/env python3
"""
test_brew_parser.py - Test suite for brew_parser

This module contains unit tests for all functionality in brew_parser.py
using pytest framework for clear, maintainable tests.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json
import requests
from brew_parser import (
    BrewParser,
    handle_update_command,
    handle_diff_command,
    handle_new_command,
)


class TestBrewParser:
    """Test suite for the BrewParser class."""

    @pytest.fixture
    def parser(self):
        """Create a BrewParser instance for testing."""
        return BrewParser()

    @pytest.fixture
    def sample_formula_data(self):
        """
        Provide sample formula data that mimics Homebrew API response.
        This helps us test without hitting the actual API.
        """
        return {
            "name": "example-tool",
            "desc": "A sample tool for testing",
            "homepage": "https://example.com",
            "versions": {"stable": "1.0.0"},
            "revision": 0,
            "version_scheme": 0,
            "bottle": {},
            "keg_only": False,
            "options": [],
            "build_dependencies": [],
            "dependencies": [],
            "recommended_dependencies": [],
            "optional_dependencies": [],
            "uses_from_macos": [],
            "requirements": [],
            "conflicts_with": [],
            "caveats": None,
            "installed": [],
            "linked_keg": None,
            "pinned": False,
            "outdated": False,
        }

    def test_init(self, parser):
        """Test BrewParser initialization."""
        assert parser.api_base == "https://formulae.brew.sh/api/formula"
        assert "User-Agent" in parser.headers
        assert parser.console is not None

    def test_fetch_all_formulas_success(self, parser):
        """Test successful fetching of all formulas from API."""
        # Mock the API response
        with patch("requests.get") as mock_get:
            # Set up mock response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = [
                {"name": "tool1", "desc": "Tool 1"},
                {"name": "tool2", "desc": "Tool 2"},
            ]
            mock_get.return_value = mock_response

            # Test the method
            formulas = parser.fetch_all_formulas()

            # Verify results
            assert len(formulas) == 2
            assert formulas[0]["name"] == "tool1"
            assert formulas[1]["name"] == "tool2"

            # Verify API was called correctly
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert "formula.json" in call_args[0][0]
            assert call_args[1]["headers"] == parser.headers

    def test_fetch_all_formulas_api_error(self, parser):
        """Test handling of API errors when fetching formulas."""
        with patch("requests.get") as mock_get:
            # Simulate API error
            mock_get.side_effect = requests.RequestException("API Error")

            # Test that we handle the error gracefully
            with pytest.raises(requests.RequestException):
                parser.fetch_all_formulas()

    def test_fetch_all_formulas_http_error(self, parser):
        """Test handling of HTTP errors (4xx, 5xx) when fetching formulas."""
        with patch("requests.get") as mock_get:
            # Set up mock response with error status
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.raise_for_status.side_effect = requests.HTTPError(
                "Server Error"
            )
            mock_get.return_value = mock_response

            # Test that HTTP errors are propagated
            with pytest.raises(requests.HTTPError):
                parser.fetch_all_formulas()

    def test_get_formula_details_success(self, parser, sample_formula_data):
        """Test successful fetching of individual formula details."""
        with patch("requests.get") as mock_get:
            # Set up mock response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = sample_formula_data
            mock_get.return_value = mock_response

            # Test the method
            details = parser.get_formula_details("example-tool")

            # Verify results
            assert details is not None
            assert details["name"] == "example-tool"
            assert details["desc"] == "A sample tool for testing"
            assert details["homepage"] == "https://example.com"

    def test_get_formula_details_not_found(self, parser):
        """Test handling when formula is not found (404)."""
        with patch("requests.get") as mock_get:
            # Set up mock 404 response
            mock_response = Mock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response

            # Test the method
            details = parser.get_formula_details("nonexistent-tool")

            # Should return None for not found
            assert details is None

    def test_get_formula_details_api_error(self, parser):
        """Test handling of API errors when fetching formula details."""
        with patch("requests.get") as mock_get:
            # Simulate connection error
            mock_get.side_effect = requests.ConnectionError("Network error")

            # Test the method
            details = parser.get_formula_details("example-tool")

            # Should return None on error
            assert details is None

    # Removed: filter_new_formulas tests (feature dropped)

    def test_format_as_markdown_with_formulas(self, parser, sample_formula_data):
        """Test markdown formatting of formula data."""
        formulas = [
            sample_formula_data,
            {
                "name": "another-tool",
                "desc": "Another testing tool",
                "homepage": "https://another.example.com",
                "versions": {"stable": "2.0.0"},
            },
        ]

        # Generate markdown
        markdown = parser.format_as_markdown(formulas)

        # Verify markdown contains expected elements
        assert "# New Homebrew Formulas" in markdown
        assert "Found 2 formulas" in markdown

        # Check first formula
        assert "## example-tool" in markdown
        assert "**Version:** 1.0.0" in markdown
        assert "**Description:** A sample tool for testing" in markdown
        assert "**Homepage:** https://example.com" in markdown

        # Check second formula
        assert "## another-tool" in markdown
        assert "**Version:** 2.0.0" in markdown
        assert "**Description:** Another testing tool" in markdown
        assert "**Homepage:** https://another.example.com" in markdown

    def test_format_as_markdown_empty_list(self, parser):
        """Test markdown formatting with no formulas."""
        markdown = parser.format_as_markdown([])

        # Should have a message about no new formulas
        assert "# New Homebrew Formulas" in markdown
        assert "No new formulas found" in markdown

    def test_format_as_markdown_missing_fields(self, parser):
        """Test markdown formatting when formula data has missing fields."""
        formulas = [
            {
                "name": "minimal-tool",
                # Missing desc, homepage, and versions
            }
        ]

        # Generate markdown
        markdown = parser.format_as_markdown(formulas)

        # Should handle missing fields gracefully
        assert "## minimal-tool" in markdown
        assert "**Description:** No description available" in markdown
        assert "**Homepage:** No homepage listed" in markdown
        assert "**Version:** Unknown version" in markdown

    def test_calculate_file_hash(self, parser, tmp_path):
        """Test SHA256 hash calculation for files."""
        # Create a test file with known content
        test_file = tmp_path / "test.txt"
        test_content = b"Hello, World!"
        test_file.write_bytes(test_content)

        # Calculate hash
        hash_result = parser.calculate_file_hash(test_file)

        # Verify it's a valid SHA256 hash (64 hex characters)
        assert len(hash_result) == 64
        assert all(c in "0123456789abcdef" for c in hash_result)

        # Verify the hash is consistent
        hash_again = parser.calculate_file_hash(test_file)
        assert hash_result == hash_again

    @patch("brew_parser.BrewParser.fetch_all_formulas")
    def test_update_stored_formulas_first_run(self, mock_fetch, parser, tmp_path):
        """Test updating formulas when no previous data exists."""
        # Use temp directory for testing
        parser.data_dir = tmp_path
        parser.stored_formulas_path = tmp_path / "formulas.json"
        parser.metadata_path = tmp_path / "metadata.json"

        # Mock API response
        mock_formulas = [
            {"name": "tool1", "desc": "Tool 1"},
            {"name": "tool2", "desc": "Tool 2"},
        ]
        mock_fetch.return_value = mock_formulas

        # Run update
        success, message = parser.update_stored_formulas()

        # Verify success
        assert success is True
        assert "Successfully updated" in message
        assert "Total formulas: 2" in message

        # Verify files were created
        assert parser.stored_formulas_path.exists()
        assert parser.metadata_path.exists()

        # Verify content (wrapped format {"formulas": [...]})
        with open(parser.stored_formulas_path) as f:
            stored_data = json.load(f)
        assert stored_data["formulas"] == mock_formulas

        # Verify metadata
        with open(parser.metadata_path) as f:
            metadata = json.load(f)
        assert metadata["formula_count"] == 2
        assert "last_updated" in metadata
        assert "hash" in metadata

    @patch("brew_parser.BrewParser.fetch_all_formulas")
    def test_update_stored_formulas_no_changes(self, mock_fetch, parser, tmp_path):
        """Test updating when data hasn't changed."""
        # Setup temp paths
        parser.data_dir = tmp_path
        parser.stored_formulas_path = tmp_path / "formulas.json"
        parser.metadata_path = tmp_path / "metadata.json"

        # Create existing data (wrapped format {"formulas": [...]})
        existing_data = [{"name": "tool1", "desc": "Tool 1"}]
        with open(parser.stored_formulas_path, "w") as f:
            json.dump({"formulas": existing_data}, f, indent=2)

        # Mock same data from API
        mock_fetch.return_value = existing_data

        # Run update
        success, message = parser.update_stored_formulas()

        # Should detect no changes
        assert success is True
        assert "already up to date" in message

    @patch("brew_parser.BrewParser.fetch_all_formulas")
    def test_update_stored_formulas_error(self, mock_fetch, parser):
        """Test handling of errors during update."""
        # Mock API error
        mock_fetch.side_effect = requests.RequestException("Network error")

        # Run update
        success, message = parser.update_stored_formulas()

        # Should handle error gracefully
        assert success is False
        assert "Network error" in message

    def test_load_stored_formulas_success(self, parser, tmp_path):
        """Test loading previously stored formula data."""
        # Setup temp paths
        parser.stored_formulas_path = tmp_path / "formulas.json"

        # Create test data
        test_data = {"formulas": [{"name": "tool1"}, {"name": "tool2"}]}
        with open(parser.stored_formulas_path, "w") as f:
            json.dump(test_data, f)

        # Load data
        loaded = parser.load_stored_formulas()

        # Verify
        assert loaded == test_data["formulas"]

    def test_load_stored_formulas_no_file(self, parser, tmp_path):
        """Test loading when no stored data exists."""
        # Use non-existent path
        parser.stored_formulas_path = tmp_path / "nonexistent.json"

        # Should return None
        loaded = parser.load_stored_formulas()
        assert loaded is None

    def test_load_stored_formulas_corrupt_file(self, parser, tmp_path):
        """Test loading when file is corrupted."""
        # Create corrupt JSON file
        parser.stored_formulas_path = tmp_path / "corrupt.json"
        parser.stored_formulas_path.write_text("{ invalid json }")

        # Should return None and not crash
        loaded = parser.load_stored_formulas()
        assert loaded is None

    def test_compare_formulas_all_changes(self, parser):
        """Test comparing formulas with additions, removals, and updates."""
        old_formulas = [
            {"name": "tool1", "versions": {"stable": "1.0.0"}},
            {"name": "tool2", "versions": {"stable": "2.0.0"}},
            {"name": "tool3", "versions": {"stable": "3.0.0"}},
        ]

        new_formulas = [
            {"name": "tool1", "versions": {"stable": "1.1.0"}},  # Updated
            {"name": "tool3", "versions": {"stable": "3.0.0"}},  # Same
            {"name": "tool4", "versions": {"stable": "4.0.0"}},  # Added
        ]

        # Compare
        diff = parser.compare_formulas(old_formulas, new_formulas)

        # Verify additions
        assert len(diff["added"]) == 1
        assert diff["added"][0]["name"] == "tool4"

        # Verify removals
        assert len(diff["removed"]) == 1
        assert diff["removed"][0]["name"] == "tool2"

        # Verify updates
        assert len(diff["updated"]) == 1
        assert diff["updated"][0]["name"] == "tool1"
        assert diff["updated"][0]["old_version"] == "1.0.0"
        assert diff["updated"][0]["new_version"] == "1.1.0"

    def test_compare_formulas_no_changes(self, parser):
        """Test comparing identical formula lists."""
        formulas = [
            {"name": "tool1", "versions": {"stable": "1.0.0"}},
            {"name": "tool2", "versions": {"stable": "2.0.0"}},
        ]

        # Compare identical lists
        diff = parser.compare_formulas(formulas, formulas)

        # Should find no differences
        assert len(diff["added"]) == 0
        assert len(diff["removed"]) == 0
        assert len(diff["updated"]) == 0

    def test_compare_formulas_empty_lists(self, parser):
        """Test comparing with empty lists."""
        # Test various empty scenarios
        diff1 = parser.compare_formulas([], [])
        assert all(len(diff1[key]) == 0 for key in ["added", "removed", "updated"])

        # All new
        new_formulas = [{"name": "tool1"}]
        diff2 = parser.compare_formulas([], new_formulas)
        assert len(diff2["added"]) == 1
        assert len(diff2["removed"]) == 0

        # All removed
        diff3 = parser.compare_formulas(new_formulas, [])
        assert len(diff3["added"]) == 0
        assert len(diff3["removed"]) == 1

    @patch("brew_parser.Console.print")
    def test_format_diff_as_table(self, mock_print, parser):
        """Test formatting diff results as tables."""
        # Create sample diff
        diff = {
            "added": [
                {"name": "new-tool", "versions": {"stable": "1.0"}, "desc": "New tool"}
            ],
            "removed": [
                {"name": "old-tool", "versions": {"stable": "0.9"}, "desc": "Old tool"}
            ],
            "updated": [
                {
                    "name": "updated-tool",
                    "old_version": "1.0",
                    "new_version": "2.0",
                    "desc": "Updated tool",
                }
            ],
        }

        # Format and display
        parser.format_diff_as_table(diff)

        # Verify print was called (tables and summary)
        assert mock_print.call_count >= 4  # At least 3 tables + summary

    @patch("brew_parser.Console.print")
    def test_format_diff_as_table_empty(self, mock_print, parser):
        """Test formatting empty diff (no changes)."""
        diff = {"added": [], "removed": [], "updated": []}

        # Format and display
        parser.format_diff_as_table(diff)

        # Should still print summary
        mock_print.assert_called()
        # Check last call was summary with all zeros
        last_call = mock_print.call_args_list[-1][0][0]
        assert "0 added, 0 removed, 0 updated" in last_call


class TestSubcommands:
    """Test suite for the new subcommand handlers."""

    @patch("brew_parser.BrewParser")
    @patch("brew_parser.Console")
    def test_handle_update_command_success(self, mock_console_class, mock_parser_class):
        """Test successful update command execution."""
        # Setup mocks
        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser
        mock_parser.update_stored_formulas.return_value = (True, "Updated successfully")

        mock_console = Mock()
        mock_console_class.return_value = mock_console
        # Mock status as a context manager
        mock_status = MagicMock()
        mock_status.__enter__ = Mock(return_value=None)
        mock_status.__exit__ = Mock(return_value=None)
        mock_console.status.return_value = mock_status

        # Create args
        args = Mock()
        args.debug = False

        # Run command
        try:
            handle_update_command(args)
        except SystemExit:
            pass

        # Verify update was called
        mock_parser.update_stored_formulas.assert_called_once()

        # Verify success message was printed
        mock_console.print.assert_called()
        call_args = mock_console.print.call_args[0][0]
        assert "✓" in call_args
        assert "Updated successfully" in call_args

    @patch("brew_parser.BrewParser")
    @patch("brew_parser.Console")
    def test_handle_diff_command_success(self, mock_console_class, mock_parser_class):
        """Test successful diff command execution."""
        # Setup mocks
        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser

        # Mock stored and current formulas
        stored = [{"name": "tool1", "versions": {"stable": "1.0"}}]
        current = [
            {"name": "tool1", "versions": {"stable": "1.0"}},
            {"name": "tool2", "versions": {"stable": "2.0"}},
        ]
        mock_parser.load_stored_formulas.return_value = stored
        mock_parser.fetch_all_formulas.return_value = current
        mock_parser.compare_formulas.return_value = {
            "added": [{"name": "tool2"}],
            "removed": [],
            "updated": [],
        }

        mock_console = Mock()
        mock_console_class.return_value = mock_console
        # Mock status as a context manager
        mock_status = MagicMock()
        mock_status.__enter__ = Mock(return_value=None)
        mock_status.__exit__ = Mock(return_value=None)
        mock_console.status.return_value = mock_status

        # Create args
        args = Mock()
        args.debug = False

        # Run command
        try:
            handle_diff_command(args)
        except SystemExit:
            pass

        # Verify methods were called
        mock_parser.load_stored_formulas.assert_called_once()
        mock_parser.fetch_all_formulas.assert_called_once()
        mock_parser.compare_formulas.assert_called_once_with(stored, current)
        mock_parser.format_diff_as_table.assert_called_once()

    @patch("brew_parser.BrewParser")
    @patch("brew_parser.Console")
    def test_handle_diff_command_no_baseline(
        self, mock_console_class, mock_parser_class
    ):
        """Test diff command when no baseline exists."""
        # Setup mocks
        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser
        mock_parser.load_stored_formulas.return_value = None

        mock_console = Mock()
        mock_console_class.return_value = mock_console

        # Create args
        args = Mock()
        args.debug = False

        # Run command - should exit with error
        with pytest.raises(SystemExit) as exc_info:
            handle_diff_command(args)

        assert exc_info.value.code == 1

        # Verify error message
        mock_console.print.assert_called()
        call_args = mock_console.print.call_args[0][0]
        assert "No stored formula data found" in call_args

    @patch("brew_parser.BrewParser")
    @patch("brew_parser.Console")
    def test_handle_new_command_with_results(
        self, mock_console_class, mock_parser_class
    ):
        """Test new command showing newly added formulas."""
        # Setup mocks
        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser

        # Mock data
        stored = [{"name": "tool1"}]
        current = [
            {"name": "tool1"},
            {"name": "tool2", "desc": "New tool 2"},
            {"name": "tool3", "desc": "New tool 3"},
        ]
        mock_parser.load_stored_formulas.return_value = stored
        mock_parser.fetch_all_formulas.return_value = current
        mock_parser.compare_formulas.return_value = {
            "added": [
                {"name": "tool2", "desc": "New tool 2"},
                {"name": "tool3", "desc": "New tool 3"},
            ],
            "removed": [],
            "updated": [],
        }
        mock_parser.format_as_markdown.return_value = "# Newly Added"

        mock_console = Mock()
        mock_console_class.return_value = mock_console
        # Mock status as a context manager
        mock_status = MagicMock()
        mock_status.__enter__ = Mock(return_value=None)
        mock_status.__exit__ = Mock(return_value=None)
        mock_console.status.return_value = mock_status

        # Create args with limit
        args = Mock()
        args.debug = False
        args.limit = 1

        # Run command
        try:
            handle_new_command(args)
        except SystemExit:
            pass

        # Verify only 1 formula was passed to format (due to limit)
        format_call_args = mock_parser.format_as_markdown.call_args[0][0]
        assert len(format_call_args) == 1

    @patch("brew_parser.BrewParser")
    @patch("brew_parser.Console")
    def test_handle_new_command_no_new_formulas(
        self, mock_console_class, mock_parser_class
    ):
        """Test new command when there are no new formulas."""
        # Setup mocks
        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser

        # Mock no changes
        stored = [{"name": "tool1"}]
        mock_parser.load_stored_formulas.return_value = stored
        mock_parser.fetch_all_formulas.return_value = stored
        mock_parser.compare_formulas.return_value = {
            "added": [],
            "removed": [],
            "updated": [],
        }

        mock_console = Mock()
        mock_console_class.return_value = mock_console
        # Mock status as a context manager
        mock_status = MagicMock()
        mock_status.__enter__ = Mock(return_value=None)
        mock_status.__exit__ = Mock(return_value=None)
        mock_console.status.return_value = mock_status

        # Create args
        args = Mock()
        args.debug = False
        args.limit = None

        # Run command
        try:
            handle_new_command(args)
        except SystemExit:
            pass

        # Verify "no new formulas" message
        mock_console.print.assert_called()
        call_args = mock_console.print.call_args[0][0]
        assert "No new formulas since last update" in call_args


class TestMainFunction:
    """Test suite for the main() function and CLI interaction."""

    @patch("brew_parser.BrewParser")
    @patch("sys.argv", ["brew_parser.py"])
    def test_main_with_default_changes_flow(self, mock_parser_class):
        """Default run shows changes since last run and updates snapshot."""
        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser

        # Simulate previous snapshot and current formulas
        mock_parser.load_stored_formulas.return_value = []
        mock_parser.fetch_all_formulas.return_value = []
        mock_parser.compare_formulas.return_value = {
            "added": [],
            "removed": [],
            "updated": [],
        }
        mock_parser.format_diff_as_markdown.return_value = (
            "# Homebrew Formula Changes\nNo changes since last snapshot."
        )

        from brew_parser import main

        try:
            main()
        except SystemExit as e:
            assert e.code == 0

        mock_parser.load_stored_formulas.assert_called_once()
        mock_parser.fetch_all_formulas.assert_called_once()
        mock_parser.compare_formulas.assert_called_once()
        mock_parser._write_snapshot.assert_called_once()

    @patch("brew_parser.BrewParser")
    @patch("sys.argv", ["brew_parser.py", "--limit", "5", "--format", "json"])
    def test_main_with_limit_and_format(self, mock_parser_class):
        """Custom args: limit and json format work in default flow."""
        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser

        # Create sample diff
        sample_diff = {
            "added": [
                {"name": f"tool{i}", "versions": {"stable": "1.0"}} for i in range(10)
            ],
            "removed": [],
            "updated": [],
        }
        mock_parser.load_stored_formulas.return_value = []
        mock_parser.fetch_all_formulas.return_value = []
        mock_parser.compare_formulas.return_value = sample_diff

        from brew_parser import main

        try:
            main()
        except SystemExit as e:
            assert e.code == 0

        # Ensure snapshot was written after run
        mock_parser._write_snapshot.assert_called_once()

    @patch("brew_parser.BrewParser")
    @patch("sys.argv", ["brew_parser.py"])
    def test_main_with_api_error(self, mock_parser_class):
        """Test main() handling of API errors."""
        # Set up mock to raise exception
        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser
        mock_parser.fetch_all_formulas.side_effect = requests.RequestException(
            "Network error"
        )

        # Import and run main
        from brew_parser import main

        # Run main (should exit with error)
        with pytest.raises(SystemExit) as exc_info:
            main()

        # Should exit with non-zero code on error
        assert exc_info.value.code == 1
