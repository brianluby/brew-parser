#! /usr/bin/env python3
"""
brew_parser.py - A tool to discover and explore new Homebrew formulas

This script fetches recently added formulas from Homebrew and displays
their descriptions and homepages in a clean markdown format.

Usage:
    python brew_parser.py [--days N] [--limit N]
"""

import json
import requests
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any
import argparse
import sys
import logging
import hashlib
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table


# Set up logging configuration
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class BrewParser:
    """
    Main class for interacting with Homebrew's API and processing formula data.

    This class handles:
    - Fetching formula data from Homebrew's API
    - Filtering formulas by date
    - Formatting output as markdown
    """

    def __init__(self) -> None:
        """Initialize the BrewParser with API endpoints and configuration."""
        # Homebrew's official API endpoint for formula metadata
        self.api_base = "https://formulae.brew.sh/api/formula"

        # Headers to identify our script (good API etiquette)
        self.headers = {
            "User-Agent": "brew-parser/1.0 (https://github.com/bluby/brew-parser)"
        }

        # Initialize rich console for pretty output
        self.console = Console()

        # Data directory for storing formula snapshots
        self.data_dir = Path.home() / ".brew-parser"
        self.data_dir.mkdir(exist_ok=True)

        # File paths for stored data
        self.stored_formulas_path = self.data_dir / "formulas.json"
        self.metadata_path = self.data_dir / "metadata.json"

    def fetch_all_formulas(self) -> List[Dict[str, Any]]:
        """
        Fetch the complete list of all formulas from Homebrew.

        Returns:
            List of formula dictionaries containing basic metadata

        Raises:
            requests.RequestException: If API request fails
        """
        try:
            logger.info("Fetching formula list from Homebrew API...")
            response = requests.get(
                self.api_base + ".json", headers=self.headers, timeout=30
            )
            response.raise_for_status()

            # Add type validation
            data = response.json()
            if not isinstance(data, list):
                raise ValueError(f"Expected list from API, got {type(data)}")

            logger.info(f"Successfully fetched {len(data)} formulas")
            return data

        except requests.RequestException as e:
            logger.error(f"Failed to fetch formulas: {e}")
            raise

    def get_formula_details(self, formula_name: str) -> Optional[Dict[str, Any]]:
        """
        Fetch detailed information about a specific formula.

        Args:
            formula_name: The name of the formula to look up

        Returns:
            Dictionary with formula details or None if not found
        """
        try:
            # Construct URL for specific formula
            url = f"{self.api_base}/{formula_name}.json"
            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code == 404:
                logger.warning(f"Formula '{formula_name}' not found")
                return None

            response.raise_for_status()

            # Add type validation
            data = response.json()
            if not isinstance(data, dict):
                raise ValueError(f"Expected dict from API, got {type(data)}")
            return data

        except requests.RequestException as e:
            logger.error(f"Failed to fetch details for {formula_name}: {e}")
            return None

    def filter_new_formulas(
        self, formulas: List[Dict[str, Any]], days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Filter formulas to only include those added within the specified days.

        Note: The Homebrew API doesn't provide creation dates directly,
        so this is a placeholder for future enhancement.

        Args:
            formulas: List of all formulas
            days: Number of days to look back (default: 7)

        Returns:
            List of formulas added within the time period
        """
        # TODO: Implement actual date filtering when we find a way to get
        # formula creation dates. For now, we'll return all formulas
        # and note this limitation in the output
        logger.warning(
            "Date filtering not yet implemented - showing all formulas. "
            "This feature requires additional data sources."
        )
        return formulas

    def format_as_markdown(self, formulas: List[Dict[str, Any]]) -> str:
        """
        Format formula data as clean markdown output.

        Args:
            formulas: List of formula dictionaries with details

        Returns:
            Formatted markdown string
        """
        if not formulas:
            return "# New Homebrew Formulas\n\nNo new formulas found."

        # Build markdown content
        markdown_lines = ["# New Homebrew Formulas\n"]
        markdown_lines.append(f"Found {len(formulas)} formulas\n")

        for formula in formulas:
            # Extract relevant fields with safe defaults
            name = formula.get("name", "Unknown")
            desc = formula.get("desc", "No description available")
            homepage = formula.get("homepage", "No homepage listed")
            version = formula.get("versions", {}).get("stable", "Unknown version")

            # Add formula section
            markdown_lines.extend(
                [
                    f"## {name}",
                    f"**Version:** {version}  ",
                    f"**Description:** {desc}  ",
                    f"**Homepage:** {homepage}  ",
                    "",  # Empty line between formulas
                ]
            )

        return "\n".join(markdown_lines)

    def calculate_file_hash(self, file_path: Path) -> str:
        """
        Calculate SHA256 hash of a file for change detection.

        This method is used to efficiently detect if formula data has changed
        by comparing file hashes instead of parsing and comparing JSON content.

        Args:
            file_path: Path to the file to hash

        Returns:
            SHA256 hash as hex string (64 characters)

        Note:
            Reads file in 4KB chunks to handle large files efficiently
            without loading entire file into memory
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            # Read in chunks to handle large files efficiently
            # 4096 bytes (4KB) is a common buffer size that balances
            # memory usage and I/O performance
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def update_stored_formulas(self) -> Tuple[bool, str]:
        """
        Download and store the latest formula data for future comparisons.

        This method:
        1. Fetches the latest formula list from Homebrew API
        2. Compares hash with existing data to detect changes
        3. Stores the new data and metadata if changed
        4. Creates ~/.brew-parser/ directory if it doesn't exist

        Returns:
            Tuple of (success: bool, message: str)
            - success: True if update succeeded, False on error
            - message: Human-readable status message

        Side Effects:
            - Creates ~/.brew-parser/formulas.json with formula data
            - Creates ~/.brew-parser/metadata.json with update metadata

        Example:
            >>> parser = BrewParser()
            >>> success, msg = parser.update_stored_formulas()
            >>> print(msg)
            "Successfully updated formula data. Total formulas: 7865"
        """
        try:
            # Fetch current formulas from Homebrew API
            logger.info("Fetching latest formula data...")
            formulas = self.fetch_all_formulas()

            # Check if we have existing data to compare
            # This allows us to detect if anything actually changed
            old_hash = None
            if self.stored_formulas_path.exists():
                old_hash = self.calculate_file_hash(self.stored_formulas_path)

            # Write new data with pretty printing for readability
            # indent=2 makes the JSON human-readable if user wants to inspect it
            # Store in a wrapper dictionary to maintain consistent format
            stored_data = {"formulas": formulas}
            with open(self.stored_formulas_path, "w") as f:
                json.dump(stored_data, f, indent=2)

            # Calculate hash of new data for future comparisons
            new_hash = self.calculate_file_hash(self.stored_formulas_path)

            # Store metadata about this update
            # This helps track when data was last updated and provides
            # quick stats without parsing the large formula file
            metadata = {
                "last_updated": datetime.now().isoformat(),
                "formula_count": len(formulas),
                "hash": new_hash,
            }
            with open(self.metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)

            # Determine if data actually changed
            if old_hash and old_hash == new_hash:
                return True, "Formula data is already up to date."
            else:
                return (
                    True,
                    f"Successfully updated formula data. "
                    f"Total formulas: {len(formulas)}",
                )

        except requests.RequestException as e:
            logger.error(f"Network error during update: {e}")
            return False, f"Network error: {str(e)}"
        except (IOError, OSError) as e:
            logger.error(f"File system error during update: {e}")
            return False, f"File system error: {str(e)}"
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON data during update: {e}")
            return False, f"Invalid JSON data: {str(e)}"

    def load_stored_formulas(self) -> Optional[List[Dict[str, Any]]]:
        """
        Load previously stored formula data from local cache.

        This method reads the formula data that was previously saved
        by update_stored_formulas(). Used for offline comparisons and
        detecting changes between updates.

        Returns:
            List of formula dictionaries if data exists, None otherwise
            Returns None if:
            - No stored data exists (first run)
            - File is corrupted or invalid JSON
            - Read permissions error

        Note:
            Does not fetch new data from API, only reads local cache
        """
        # Check if we have any stored data
        if not self.stored_formulas_path.exists():
            return None

        try:
            # Load and parse the stored JSON data
            with open(self.stored_formulas_path, "r") as f:
                stored_data: Dict[str, Any] = json.load(f)
                formulas = stored_data.get("formulas")
                if not isinstance(formulas, list):
                    raise ValueError("Invalid stored data format")
                return formulas
        except (IOError, OSError) as e:
            # Log error but don't crash - return None to indicate no data
            logger.error(f"Failed to read stored formulas file: {e}")
            return None
        except (json.JSONDecodeError, ValueError) as e:
            # Log error but don't crash - return None to indicate no data
            logger.error(f"Failed to parse stored formulas: {e}")
            return None

    def compare_formulas(
        self, old_formulas: List[Dict[str, Any]], new_formulas: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Compare two sets of formulas to find differences.

        This method performs a three-way comparison to detect:
        1. Added formulas (exist in new but not old)
        2. Removed formulas (exist in old but not new)
        3. Updated formulas (version changed between old and new)

        Args:
            old_formulas: Previous formula list (from stored data)
            new_formulas: Current formula list (freshly fetched)

        Returns:
            Dictionary with three keys:
            - 'added': List of newly added formulas
            - 'removed': List of removed formulas
            - 'updated': List of updated formulas with both old and new versions

        Example Return:
            {
                'added': [{'name': 'new-tool', 'desc': '...', ...}],
                'removed': [{'name': 'old-tool', 'desc': '...', ...}],
                'updated': [
                    {'name': 'tool', 'old_version': '1.0', 'new_version': '2.0', ...}
                ]
            }
        """
        # Create dictionaries for O(1) lookup by name
        # This is more efficient than nested loops for large formula lists
        old_by_name = {f["name"]: f for f in old_formulas}
        new_by_name = {f["name"]: f for f in new_formulas}

        # Get sets of formula names for set operations
        old_names = set(old_by_name.keys())
        new_names = set(new_by_name.keys())

        # Find differences using set operations
        # new_names - old_names gives us formulas that only exist in new
        added = [new_by_name[name] for name in (new_names - old_names)]

        # old_names - new_names gives us formulas that only exist in old
        removed = [old_by_name[name] for name in (old_names - new_names)]

        # Find updated formulas by checking version changes
        # old_names & new_names gives us formulas that exist in both
        updated = []
        for name in old_names & new_names:
            # Extract version info, defaulting to empty string if not found
            old_version = old_by_name[name].get("versions", {}).get("stable", "")
            new_version = new_by_name[name].get("versions", {}).get("stable", "")

            # Only consider it updated if version actually changed
            if old_version != new_version:
                # Include full formula data plus old version for display
                updated.append(
                    {
                        **new_by_name[name],  # All current formula data
                        "old_version": old_version,  # Add old version for comparison
                        "new_version": new_version,  # Explicitly include new version
                    }
                )

        # Return sorted results for consistent output
        return {
            "added": sorted(added, key=lambda x: x["name"]),
            "removed": sorted(removed, key=lambda x: x["name"]),
            "updated": sorted(updated, key=lambda x: x["name"]),
        }

    def format_diff_as_table(self, diff: Dict[str, List[Dict[str, Any]]]) -> None:
        """
        Format and display formula differences as rich tables.

        Creates visually appealing tables for added, removed, and updated
        formulas using the Rich library. Each category gets its own table
        with appropriate color coding:
        - Added: Green title, cyan names
        - Removed: Red title and names
        - Updated: Yellow title with version comparison

        Args:
            diff: Dictionary from compare_formulas() containing:
                  - 'added': List of new formulas
                  - 'removed': List of removed formulas
                  - 'updated': List of updated formulas

        Side Effects:
            Prints formatted tables to console

        Note:
            Long descriptions are truncated with ellipsis to maintain
            table readability. Full descriptions can be viewed with
            the regular 'brew_parser.py' command.
        """
        # Display newly added formulas with green styling for positive changes
        if diff["added"]:
            table = Table(title="[green]New Formulas[/green]")
            table.add_column("Name", style="cyan")
            table.add_column("Version", style="green")
            table.add_column("Description", style="white")

            for formula in diff["added"]:
                # Truncate long descriptions to keep table readable
                # 60 chars is a good balance for terminal width
                desc = formula.get("desc", "No description")
                if len(desc) > 60:
                    desc = desc[:60] + "..."

                table.add_row(
                    formula["name"],
                    formula.get("versions", {}).get("stable", "N/A"),
                    desc,
                )

            self.console.print(table)
            self.console.print()  # Empty line for spacing

        # Display removed formulas with red styling for attention
        if diff["removed"]:
            table = Table(title="[red]Removed Formulas[/red]")
            table.add_column("Name", style="red")
            table.add_column("Version", style="dim")
            table.add_column("Description", style="dim")

            for formula in diff["removed"]:
                desc = formula.get("desc", "No description")
                if len(desc) > 60:
                    desc = desc[:60] + "..."

                table.add_row(
                    formula["name"],
                    formula.get("versions", {}).get("stable", "N/A"),
                    desc,
                )

            self.console.print(table)
            self.console.print()

        # Display updated formulas with version comparison
        if diff["updated"]:
            table = Table(title="[yellow]Updated Formulas[/yellow]")
            table.add_column("Name", style="cyan")
            table.add_column("Old Version", style="dim")
            table.add_column("New Version", style="green")
            table.add_column("Description", style="white")

            for formula in diff["updated"]:
                # Slightly shorter description for 4-column table
                desc = formula.get("desc", "No description")
                if len(desc) > 50:
                    desc = desc[:50] + "..."

                table.add_row(
                    formula["name"],
                    formula.get("old_version", "N/A"),
                    formula.get("new_version", "N/A"),
                    desc,
                )

            self.console.print(table)
            self.console.print()

        # Print summary line with totals for each category
        self.console.print(
            f"[bold]Summary:[/bold] "
            f"{len(diff['added'])} added, "
            f"{len(diff['removed'])} removed, "
            f"{len(diff['updated'])} updated"
        )


def handle_update_command(args: argparse.Namespace) -> None:
    """
    Handle the 'update' subcommand to download and store latest formula data.

    This command fetches the current formula list from Homebrew API and
    stores it locally for future comparisons. It's the first step in
    tracking formula changes over time.

    Args:
        args: Parsed command line arguments

    Side Effects:
        - Creates ~/.brew-parser/ directory if needed
        - Downloads and stores formula data
        - Updates metadata file with timestamp
    """
    # Set debug logging if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # Initialize parser and console
    brew_parser = BrewParser()
    console = Console()

    try:
        # Perform the update with a nice status message
        with console.status("[bold blue]Updating formula database..."):
            success, message = brew_parser.update_stored_formulas()

        # Display result with appropriate styling
        if success:
            console.print(f"[green]✓[/green] {message}")
        else:
            console.print(f"[red]✗[/red] {message}")
            sys.exit(1)

    except KeyboardInterrupt:
        console.print("\n[yellow]Update interrupted by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        if args.debug:
            console.print_exception()
        sys.exit(1)


def handle_diff_command(args: argparse.Namespace) -> None:
    """
    Handle the 'diff' subcommand to show all changes since last update.

    This command compares the stored formula data with the current state
    from Homebrew API, showing added, removed, and updated formulas in
    formatted tables.

    Args:
        args: Parsed command line arguments

    Note:
        Requires running 'update' command at least once to establish baseline
    """
    # Set debug logging if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # Initialize parser and console
    brew_parser = BrewParser()
    console = Console()

    try:
        # Load stored formulas first
        stored_formulas = brew_parser.load_stored_formulas()
        if not stored_formulas:
            console.print(
                "[yellow]No stored formula data found.[/yellow]\n"
                "Run 'brew_parser.py update' first to establish a baseline."
            )
            sys.exit(1)

        # Fetch current formulas
        with console.status("[bold green]Fetching current formulas..."):
            current_formulas = brew_parser.fetch_all_formulas()

        # Compare and display differences
        with console.status("[bold blue]Analyzing changes..."):
            diff = brew_parser.compare_formulas(stored_formulas, current_formulas)

        # Display the differences in nice tables
        brew_parser.format_diff_as_table(diff)

    except requests.RequestException as e:
        console.print(
            f"[bold red]Error:[/bold red] Failed to fetch data from Homebrew: {e}"
        )
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        if args.debug:
            console.print_exception()
        sys.exit(1)


def handle_new_command(args: argparse.Namespace) -> None:
    """
    Handle the 'new' subcommand to show only newly added formulas.

    This is a filtered version of 'diff' that only shows formulas that
    were added since the last update. Useful for quickly seeing what's
    new without the noise of updates and removals.

    Args:
        args: Parsed command line arguments including optional --limit
    """
    # Set debug logging if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # Initialize parser and console
    brew_parser = BrewParser()
    console = Console()

    try:
        # Load stored formulas first
        stored_formulas = brew_parser.load_stored_formulas()
        if not stored_formulas:
            console.print(
                "[yellow]No stored formula data found.[/yellow]\n"
                "Run 'brew_parser.py update' first to establish a baseline."
            )
            sys.exit(1)

        # Fetch current formulas
        with console.status("[bold green]Fetching current formulas..."):
            current_formulas = brew_parser.fetch_all_formulas()

        # Compare to find new formulas
        with console.status("[bold blue]Finding new formulas..."):
            diff = brew_parser.compare_formulas(stored_formulas, current_formulas)

        # Get just the added formulas
        new_formulas = diff["added"]

        # Apply limit if specified
        if args.limit and args.limit > 0:
            new_formulas = new_formulas[: args.limit]

        # Format and display as markdown (reuse existing method)
        if new_formulas:
            # Temporarily replace the header for clarity
            markdown_output = brew_parser.format_as_markdown(new_formulas)
            markdown_output = markdown_output.replace(
                "# New Homebrew Formulas", "# Newly Added Homebrew Formulas"
            )
            console.print(Markdown(markdown_output))
        else:
            console.print("[green]No new formulas since last update.[/green]")

    except requests.RequestException as e:
        console.print(
            f"[bold red]Error:[/bold red] Failed to fetch data from Homebrew: {e}"
        )
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        if args.debug:
            console.print_exception()
        sys.exit(1)


def main() -> None:
    """
    Main entry point for the script.
    Handles command line arguments and orchestrates the workflow.

    The script supports multiple modes:
    1. Default: Show all formulas (legacy behavior)
    2. update: Download and store current formula state
    3. diff: Show all changes since last update
    4. new: Show only newly added formulas
    """
    # Create main parser with updated description
    parser = argparse.ArgumentParser(
        description="Discover and track new Homebrew formulas",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Show all formulas (with optional limit)
  %(prog)s --limit 10         # Show only first 10 formulas
  %(prog)s update             # Update local formula database
  %(prog)s diff               # Show all changes since last update
  %(prog)s new                # Show only new formulas since last update
  %(prog)s new --limit 5      # Show only 5 newest formulas
        """,
    )

    # Add subcommands for the new functionality
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Default command arguments (when no subcommand is used)
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of days to look back (not yet implemented)",
    )
    parser.add_argument("--limit", type=int, help="Limit number of formulas to display")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    # Update subcommand - downloads and stores current formula data
    update_parser = subparsers.add_parser(
        "update", help="Update local formula database with current data"
    )
    update_parser.add_argument(
        "--debug", action="store_true", help="Enable debug logging"
    )

    # Diff subcommand - shows all changes since last update
    diff_parser = subparsers.add_parser(
        "diff", help="Show all changes (added/removed/updated) since last update"
    )
    diff_parser.add_argument(
        "--debug", action="store_true", help="Enable debug logging"
    )

    # New subcommand - shows only newly added formulas
    new_parser = subparsers.add_parser(
        "new", help="Show only newly added formulas since last update"
    )
    new_parser.add_argument(
        "--limit", type=int, help="Limit number of new formulas to display"
    )
    new_parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    # Parse arguments
    args = parser.parse_args()

    # Route to appropriate handler based on command
    if args.command == "update":
        handle_update_command(args)
    elif args.command == "diff":
        handle_diff_command(args)
    elif args.command == "new":
        handle_new_command(args)
    else:
        # Default behavior - show all formulas (original functionality)
        # Set debug logging if requested
        if args.debug:
            logging.getLogger().setLevel(logging.DEBUG)

        # Initialize the parser and run original logic
        brew_parser = BrewParser()
        console = Console()

        try:
            # Fetch all formulas
            with console.status("[bold green]Fetching formulas from Homebrew..."):
                all_formulas = brew_parser.fetch_all_formulas()

            # Filter by date (placeholder for now)
            filtered_formulas = brew_parser.filter_new_formulas(all_formulas, args.days)

            # Apply limit if specified
            if args.limit and args.limit > 0:
                filtered_formulas = filtered_formulas[: args.limit]

            # Format and display
            markdown_output = brew_parser.format_as_markdown(filtered_formulas)
            console.print(Markdown(markdown_output))

        except requests.RequestException as e:
            console.print(
                f"[bold red]Error:[/bold red] Failed to fetch data from Homebrew: {e}"
            )
            sys.exit(1)
        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted by user[/yellow]")
            sys.exit(0)
        except Exception as e:
            console.print(f"[bold red]Unexpected error:[/bold red] {e}")
            if args.debug:
                console.print_exception()
            sys.exit(1)


if __name__ == "__main__":
    main()
