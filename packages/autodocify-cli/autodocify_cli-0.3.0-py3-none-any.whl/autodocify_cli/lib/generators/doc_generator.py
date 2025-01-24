import os
import typer
from yaspin import yaspin
from autodocify_cli.lib.project_content_merger import merge_files
from autodocify_cli.lib.utils import get_git_tracked_files, technical_docs_prompt
from autodocify_cli.lib.services.ai_integration import ai


def generate_technical_docs(base_path: str, output_file: str, llm: str):
    """
    Generates a Docs.md file for the project by merging content from the specified base directory.

    Args:
        base_dir (str): The directory containing the project files to merge.
        output_file (str): The name of the output Technical docs file.
        llm (str): The AI language model to use, defaults to 'gemini'

    Returns:
        dict: A dictionary containing a success message or an error message.
    """
    try:
        # Get Tracked Files
        files = get_git_tracked_files(base_path)
        # Merge files from the specified directory into the output file
        content = merge_files(base_path, files)
        prompt = technical_docs_prompt(content)
        with yaspin(text="Genrating Docs file using AI...", color="cyan") as spinner:
            result = ai(prompt, llm)
            spinner.ok("DOCS Generated Using AI")

        with open(output_file, "w", encoding="utf-8") as out_file:
            out_file.write(result)
        os.remove(f"{base_path}/merge.txt")
        typer.echo(f"Docs generated successfully at {output_file}")
    except Exception as e:
        typer.echo(f"Failed to generate Docs: {str(e)}")
        return {"Error": f"Failed to generate Docs: {str(e)}"}
