# AutoDocify CLI

## Overview

AutoDocify CLI is a command-line interface (CLI) tool designed to automate the generation of project documentation, including README files and technical documentation, using AI models.  It streamlines the documentation process, saving developers valuable time and effort.  The tool supports multiple Large Language Models (LLMs) such as Gemini, OpenAI, and Bard, offering flexibility and choice.

[//]: # (This is a comment, it will not appear in the README)

[TOC]


## Table of Contents

* [Installation Instructions](#installation-instructions)
* [Usage Guide](#usage-guide)
* [Configuration](#configuration)
* [Technical Details](#technical-details)
* [Contribution Guidelines](#contribution-guidelines)
* [License](#license)
* [FAQs](#faqs)
* [Support](#support)


## Installation Instructions

**Prerequisites:**

* Python 3.7 or higher
* `pip` (Python package installer)

**Installation:**

1. Clone the repository:
   ```bash
   git clone <REPOSITORY_URL>
   cd <PROJECT_DIRECTORY>
   ```

2. Create a `.env` file in the `autodocify_cli/core/env_files` directory  based on the `.env.example` file (if provided) and populate it with your API keys for the LLMs you intend to use (Gemini, OpenAI).

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage Guide


AutoDocify CLI offers several commands to automate different documentation tasks:

* **`autodocify greet [name]`:**  Greets the user.  Replace `[name]` with your name (optional).
* **`autodocify generate-readme [base_dir] [output_file] [llm]`:** Generates a README.md file.  `[base_dir]` specifies the project directory (defaults to the current directory). `[output_file]` specifies the name of the output README file (defaults to `README.md`). `[llm]` specifies the LLM to use (`gemini`, `openai`, or `bard`, defaults to `gemini`).
* **`autodocify generate-tests [base_dir] [llm]`:** Generates test files for the project. `[base_dir]` specifies the project directory (defaults to the current directory). `[llm]` specifies the LLM to use (`gemini`, `openai`, or `bard`, defaults to `gemini`).
* **`autodocify generate-docs [base_dir] [output_file] [llm]`:** Generates technical documentation. `[base_dir]` specifies the project directory (defaults to the current directory). `[output_file]` specifies the name of the output documentation file (defaults to `DOCS.md`). `[llm]` specifies the LLM to use (`gemini`, `openai`, or `bard`, defaults to `gemini`).

**Example:**

To generate a README using the Gemini LLM:

```bash
autodocify generate-readme . my_readme.md gemini
```

This command will generate a `my_readme.md` file in the current directory.


## Configuration

The tool is configured using environment variables specified in a `.env` file located at `autodocify_cli/core/env_files/.env`. This file should contain the following keys:

* `GEMINI_API_KEY`: Your Google Gemini API key.
* `OPENAI_API_KEY`: Your OpenAI API key.
* `OPENAI_MODEL`: The OpenAI model to use (e.g., `gpt-3.5-turbo`).


## Technical Details

* **Programming Language:** Python
* **Frameworks/Libraries:** Typer, Rich, Yaspin, Pydantic-Settings, Google Generative AI (for Gemini), OpenAI Python library.
* **Architecture:** The CLI uses Typer for command-line argument parsing, Rich for console output formatting, Yaspin for loading indicators, and integrates with various AI services for documentation generation.

## Contribution Guidelines

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them with clear and concise messages.
4. Push your branch to your forked repository.
5. Create a pull request describing your changes.


## License

This project is licensed under the <INSERT LICENSE NAME> License - see the [LICENSE](LICENSE) file for details.


## FAQs

* **Q: What happens if the API key is missing or invalid?**  A: The tool will output an error message indicating that the API key is missing or invalid and will not be able to generate documentation.

* **Q:  Which LLMs are supported?** A: Currently, Gemini, OpenAI, and Bard are supported.  Support for additional LLMs may be added in the future.

* **Q: How can I customize the output?** A:  The prompts used to generate the documentation can be adjusted in the `prompt_templates` directory.  You can also modify the output formatting using Rich's styling options.


## Support

For support or to report issues, please open an issue on the [GitHub repository](<REPOSITORY_URL>).
