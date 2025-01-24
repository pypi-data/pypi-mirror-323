import os
from pathlib import Path
import typer
from yaspin import yaspin
from autodocify_cli.lib.project_content_merger import merge_files
from autodocify_cli.lib.utils import get_git_tracked_files, test_prompt
from autodocify_cli.lib.services.ai_integration import ai


def generate_test_files(base_path: str, llm: str) -> dict:
    """
    Creates a 'tests' folder in the current working directory if it doesn't already exist,
    and writes a default test file inside it.

    Args:
        current_working_directory (str): The path to the current working directory.

    Returns:
        dict: A dictionary containing a success message or an error message.
    """
    try:
        cwd_path = Path(base_path)
        tests_folder = cwd_path / "tests"

        # Create 'tests' folder if it doesn't exist
        tests_folder.mkdir(exist_ok=True)

        # Create a test file in the folder
        test_file = tests_folder / "test_main.py"
        if not test_file.exists():
            files = get_git_tracked_files(base_path)
            # Merge files from the specified directory into the output file
            content = merge_files(base_path, files)
            prompt = test_prompt(content)
            result = ai(prompt, llm)
            with open(test_file, "w", encoding="utf-8") as file:
                file.write(result)
        else:
            files = get_git_tracked_files(base_path)
            # Merge files from the specified directory into the output file
            content = merge_files(base_path, files)
            prompt = test_prompt(content)
            with yaspin(
                text="Genrating test files using AI...", color="cyan"
            ) as spinner:
                result = ai(prompt, llm)
                spinner.ok("Test Files Generated Using AI")
            with open(test_file, "w", encoding="utf-8") as file:
                file.write(result)
            os.remove(f"{base_path}/merge.txt")
        typer.echo(f"Tests folder and file(s) are set up at {tests_folder}")
    except Exception as e:
        return {"Error": f"Failed to set up tests folder: {str(e)}"}
