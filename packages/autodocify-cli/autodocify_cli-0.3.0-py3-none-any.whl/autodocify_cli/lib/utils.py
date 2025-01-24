import subprocess
from pathlib import Path
import typer
from autodocify_cli.lib.loaders.yaspin import show_loader
from autodocify_cli.lib.prompt_templates.readme_prompt_template import (
    readme_prompt_template,
)
from autodocify_cli.lib.prompt_templates.technical_doc_prompt_template import (
    technical_doc_prompt_template,
)
from autodocify_cli.lib.prompt_templates.test_prompt_template import (
    test_doc_prompt_template,
)


from pathlib import Path
import subprocess
import typer


# Centralized exclusions
DEFAULT_EXCLUDED_PATHS = [
    ".github/workflows",
    "tests",
    "CHANGELOG.md",
]
DEFAULT_EXCLUDED_EXTENSIONS = [
    ".log",
    ".tmp",
    ".yml",
    ".yaml",
    ".gitignore",
    ".json",
    ".lock",
    ".toml",
    ".md",
]


def greet_user(name: str = "Comrade") -> str:
    """
    Returns a greeting message.

    Args:
        name (str): Name of the user to greet. Defaults to "Comrade".

    Returns:
        str: Greeting message.
    """
    return f"Hello, {name}! Welcome to AutoDocify."


def get_base_path(base_dir: str = None) -> Path:
    """
    Returns the base path for the project directory.

    Args:
        base_dir (str): Path to the base directory. Defaults to the current working directory.

    Returns:
        Path: Resolved Path object for the base directory.

    Raises:
        typer.Exit: If the directory does not exist.
    """
    base_dir = Path(base_dir or Path.cwd())
    if not base_dir.exists():
        typer.echo(f"Error: The directory {base_dir} does not exist.")
        raise typer.Exit(code=1)
    return base_dir


def get_git_tracked_files(
    base_path: Path, excluded_paths=None, excluded_extensions=None
) -> list[str]:
    """
    Retrieve a list of all files tracked by Git in the given directory,
    excluding deleted files, as well as user-defined excluded files, folders, or extensions.

    Args:
        base_path (Path): The base path of the git repository.
        excluded_paths (list[str]): Paths (files or folders) to exclude.
        excluded_extensions (list[str]): File extensions to exclude.

    Returns:
        list[str]: A list of files tracked by Git, excluding specified files and extensions.
    """
    if excluded_paths is None:
        excluded_paths = DEFAULT_EXCLUDED_PATHS
    if excluded_extensions is None:
        excluded_extensions = DEFAULT_EXCLUDED_EXTENSIONS

    try:
        # Get the list of tracked files
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=base_path,
            text=True,
            capture_output=True,
            check=True,
        )
        tracked_files = result.stdout.strip().split("\n")

        # Get the list of deleted files not yet committed
        deleted_result = subprocess.run(
            ["git", "ls-files", "--deleted"],
            cwd=base_path,
            text=True,
            capture_output=True,
            check=True,
        )
        deleted_files = deleted_result.stdout.strip().split("\n")

        # Filter out deleted files, excluded paths, and excluded extensions
        valid_files = [
            file
            for file in tracked_files
            if file not in deleted_files
            and not any(
                file == path or file.startswith(f"{path}/") for path in excluded_paths
            )
            and not any(file.endswith(ext) for ext in excluded_extensions)
        ]

        if not valid_files:
            typer.echo("No valid files found to merge in the repository.")
        else:
            typer.echo(f"Found {len(valid_files)} valid files.")

        return valid_files

    except subprocess.CalledProcessError as e:
        typer.echo(f"Error retrieving tracked files: {e}")
        return []


def ai_service(file_path: str, llm: str) -> None:
    """
    Placeholder function for selecting AI service based on the language model (llm).

    Args:
        file_path (str): Path to the file being processed.
        llm (str): Language model identifier (e.g., "gemini", "openai", "bard").
    """
    typer.echo(f"Using {llm}")
    match llm:
        case "gemini":
            pass
        case "openai":
            pass
        case "bard":
            pass
    pass


def readme_prompt(content: str) -> str:
    """
    Generates a README prompt based on the provided content.

    Args:
        content (str): Content to be included in the README prompt.

    Returns:
        str: The generated README prompt.
    """
    return f"""
    {readme_prompt_template}

    Here is the project content:
    {content}
    """


def technical_docs_prompt(content: str) -> str:
    """
    Generates a technical documentation prompt based on the provided content.

    Args:
        content (str): Content to be included in the technical documentation prompt.

    Returns:
        str: The generated technical documentation prompt.
    """
    return f"""
   {technical_doc_prompt_template}

    Here is the project content:
    {content}
    """


def test_prompt(content: str) -> str:
    """
    Generates a test prompt based on the provided content.

    Args:
        content (str): Content to be included in the test prompt.

    Returns:
        str: The generated test prompt.
    """
    return f"""
    {test_doc_prompt_template}

    Here is the project content:
    {content}
    """
