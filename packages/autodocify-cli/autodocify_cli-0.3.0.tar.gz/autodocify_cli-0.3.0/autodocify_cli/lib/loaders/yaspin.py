from yaspin import yaspin
from yaspin.spinners import Spinners


def show_loader(task_name: str, spinner_style: str = "earth", color: str = "cyan"):
    """
    Reusable yaspin loader for displaying task progress.

    Args:
        task_name (str): The name of the task to display while loading.
        spinner_style (str): The style of the spinner. Default is 'dots'.
        color (str): The color of the spinner. Default is 'cyan'.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            with yaspin(Spinners[spinner_style], text=f"{task_name}...", color=color) as spinner:
                try:
                    result = func(*args, **kwargs)
                    spinner.ok("✔")
                    return result
                except Exception as e:
                    spinner.fail("✘")
                    raise e
        return wrapper
    return decorator
