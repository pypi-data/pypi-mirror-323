"""
Helper class for printing user-readable stylised output
"""
from colorama import Back, Style


def print_fail(content: str) -> None:
    """Prints a formatted error string to the console

    Args:
        content (str): String to output with error
    """
    print(Back.RED + " FAIL \t" + Style.RESET_ALL + " " + content)


def print_warn(content: str) -> None:
    """Prints a formatted warning string to the console

    Args:
        content (str): String to output with warning
    """
    print(Back.YELLOW + " WARN \t" + Style.RESET_ALL + " " + content)


def print_pass(content: str) -> None:
    """Prints a formatted pass string to the console

    Args:
        content (str): String to output with pass
    """
    print(Back.GREEN + " PASS \t" + Style.RESET_ALL + " " + content)
