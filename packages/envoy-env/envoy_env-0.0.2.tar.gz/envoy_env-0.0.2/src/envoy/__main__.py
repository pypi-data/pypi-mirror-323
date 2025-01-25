import re
import sys

import colorama
import typer
from colorama import Fore, Style
from typing_extensions import Annotated

from envoy.output import print_fail, print_pass, print_warn

app = typer.Typer()


@app.command()
def run(
    env_file: str,
    example_file: str,
    warn_additional_keys: Annotated[
        bool,
        typer.Option(
            help="Whether to warn when additional keys are found in the .env"),
    ] = False,
    warn_uninitialised_keys: Annotated[
        bool,
        typer.Option(
            help="Whether to warn when keys are found in the .env but not initialised with a value"
        )
    ] = False,
) -> None:
    fail_flag = False
    warning_flag = False

    if is_missing_keys(env_file, example_file):
        fail_flag = True

    if warn_additional_keys:
        print()
        if has_additional_keys(env_file, example_file):
            warning_flag = True

    if warn_uninitialised_keys:
        print()
        if has_uninitialised_keys(env_file):
            warning_flag = True

    print()
    if fail_flag:
        print(
            f"{
                Fore.RED
            }Checking complete with errors found, please fix the errors and try again.{
                Style.RESET_ALL
            }"
        )
        sys.exit(1)

    if warning_flag:
        print(f"{Fore.YELLOW}Checking complete with warnings found, please fix the warnings and try again.{
              Style.RESET_ALL}")
        sys.exit(0)

    print(f"{Fore.GREEN}Checking complete, no errors found!{Style.RESET_ALL}")


def is_missing_keys(env_file: str, example_file: str) -> bool:
    """Check for missing keys in the provided env file, that are present in the example file

    Args:
        env_file (str): The users environment file
        example_file (str): The example environment file

    Returns:
        bool: Whether the example file contains keys that are not in the users environment file
    """
    print(f"Checking for missing keys in file {
          Style.BRIGHT}{env_file}{Style.RESET_ALL}'\n")
    differences = _get_differences(env_file, example_file)
    for difference in differences:
        print_fail(
            f"Provided env file is missing attribute '{Style.BRIGHT}{
                difference
            }{Style.NORMAL}' which is in the example file"
        )

    if len(differences) > 0:
        return True
    else:
        print_pass(
            f"No differences found between '{Style.BRIGHT}{env_file}{
                Style.NORMAL
            }' and '{Style.BRIGHT}{example_file}{Style.NORMAL}'"
        )
        return False


def has_additional_keys(env_file: str, example_file: str) -> bool:
    """Check for additional keys in the user environment file, that are not present in the example file

    Args:
        env_file (str): The users environment file
        example_file (str): The example environment file

    Returns:
        bool: Whether the user environment file contains keys that are not in the example file
    """
    print(f"Checking for additional keys in file '{
        Style.BRIGHT}{env_file}{Style.RESET_ALL}'\n")
    differences = _get_differences(example_file, env_file)
    for difference in differences:
        print_warn(f"Provided env file had additional attribute '{
            Style.BRIGHT}{difference}{Style.NORMAL}' which is not in the example file")

    if len(differences) > 0:
        return True
    else:
        print_pass(
            f"No additional keys found between '{Style.BRIGHT}{env_file}{
                Style.NORMAL
            }' and '{Style.BRIGHT}{example_file}{Style.NORMAL}'"
        )


def has_uninitialised_keys(env_file: str) -> bool:
    """Check for uninitialised keys in the user environment file

    Args:
        env_file (str): The users environment file
        example_file (str): _description_

    Returns:
        bool: Whether the environment file contains uninitialised keys
    """
    print(f"Checking for uninitialised keys in file '{
          Style.BRIGHT}{env_file}{Style.RESET_ALL}'\n")
    entries = _get_env_entries(env_file, remove_value=False)
    uninitialised_keys = []
    for entry in entries:
        split_entry = entry.split("=")
        if len(split_entry) == 2 and split_entry[1] == "":
            uninitialised_keys.append(split_entry[0])

    if len(uninitialised_keys) > 0:
        for key in uninitialised_keys:
            print_warn(
                f"Provided env file has uninitialised key '{
                    Style.BRIGHT}{key}{Style.NORMAL}'"
            )
        return True
    else:
        print_pass(
            f"No uninitialised keys found in '{Style.BRIGHT}{env_file}{
                Style.NORMAL}'"
        )


def _get_env_entries(file: str, remove_value: bool = True) -> list:
    """Extracts the keys from a given env file

    Args:
        file (str): The path to the env file
        remove_value (bool): Whether to remove the value and "=" sign from the entry

    Returns:
        list: A list of keys found in the env file
    """
    keys = []
    with open(file, "r") as f:
        for line in f:
            if _is_env(line):
                if remove_value:
                    keys.append(line.split("=")[0].strip())
                else:
                    keys.append(line.strip())
    return keys


def _get_differences(env_file: str, example_file: str) -> list:
    """Gets the different env entries between the env file and the example file

    Args:
        env_file (str): The current active env file
        example_file (str): The example env file

    Returns:
        list: A list of the items available in the example file but not in the env file
    """
    env_keys = _get_env_entries(env_file)
    example_keys = _get_env_entries(example_file)

    return list(set(example_keys).difference(env_keys))


def _is_env(line: str) -> bool:
    """Takes a line and returns true if it is a valid .env line

    Args:
        line (str): The line, taken from the env file

    Returns:
        bool: Whether the line is a valid .env line
    """
    match = re.match(r"^[A-Z][A-Z0-9_]*=.*$", line)
    return match is not None


if __name__ == "__main__":
    colorama.init()
    app()
