from pathlib import Path

import typer

from autodocify_cli.lib.utils import DEFAULT_EXCLUDED_EXTENSIONS


def merge_files(base_path: Path, files: list[str], exclude_extensions=None) -> str:
    """
    Merge the content of specified files into a single file, excluding files with certain extensions.

    Args:
        base_path (Path): The base directory containing the files.
        files (list): List of filenames to merge.
        exclude_extensions (list[str]): Extensions to exclude from merging.

    Returns:
        str: Merged content of the files.
    """
    if exclude_extensions is None:
        exclude_extensions = DEFAULT_EXCLUDED_EXTENSIONS

    try:
        # Filter out files with excluded extensions
        files_to_merge = [
            file for file in files if Path(file).suffix not in exclude_extensions
        ]

        if not files_to_merge:
            raise ValueError("No files to merge after applying exclusions.")

        typer.echo(f"Merging {len(files_to_merge)} files...")

        output_file = base_path / "merge.txt"

        # Merge file contents
        with open(output_file, "w", encoding="utf-8") as out_file:
            for file in files_to_merge:
                relative_path = base_path / file
                out_file.write(f"\n# ===== File: {relative_path} =====\n")
                with open(
                    relative_path, "r", encoding="utf-8", errors="ignore"
                ) as in_file:
                    out_file.write(in_file.read())
                    out_file.write("\n")
        with open(output_file, "r", encoding="utf-8") as merged_file:
            return merged_file.read()

    except Exception as e:
        typer.echo(f"An error occurred while merging files: {e}")
        return ""
