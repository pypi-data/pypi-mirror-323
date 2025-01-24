from autodocify_cli.lib.services.Bard import BardService
from autodocify_cli.lib.services.Gemini import GeminiService
from autodocify_cli.lib.services.OpenAI import OpenAIService


def ai(prompt, llm: str = "gemini"):
    match llm:
        case "gemini":
            return GeminiService(prompt).run()
        case "openai":
            return OpenAIService(prompt).run()
        case "bard":
            return BardService(prompt).run()
