# ** OPTIC
# **
# ** Copyright (c) 2024-2025 Oracle Corporation
# ** Licensed under the Universal Permissive License v 1.0
# ** as shown at https://oss.oracle.com/licenses/upl/

import os
from os import environ

from optic.common.exceptions import OpticConfigurationFileError
from optic.common.helpers import prompt_question
from optic.common.optic_color import OpticColor

CONFIG_BASE_DIR = "~/.optic"

SAMPLE_CLUSTER_CONFIG = """clusters:
  cluster_1:
    url: https://testurl.com:46
    username: my_username1
    password: my_password
  cluster_2:
    url: https://myurl.com:9200
    username: my_username2
    password: '****'
  my_cluster:
    url: https://onlineopensearchcluster.com:634
    username: my_username3
    password: '****'
  cluster_3:
    url: https://anotherurl.com:82
    username: my_username4
    password: '****'

groups:
  my_group:
    - cluster_1
    - cluster_2
    - cluster_3
  g2:
    - cluster_1
    - my_cluster

"""

SAMPLE_SETTINGS = """# File Paths
settings_file_path: ~/.optic/optic-settings.yaml
default_cluster_config_file_path: ~/.optic/cluster-config.yaml

# Terminal Customization
disable_terminal_color: False

# Cluster Info Settings
default_cluster_info_byte_type: gb
storage_percent_thresholds:
  GREEN: 80
  YELLOW: 85
  RED: 100

# Index/Alias Info Settings
default_search_pattern: '*'
default_index_type_patterns:
  ISM: '(.*)-ism-(\\d{6})$'
  ISM_MALFORMED: '(.*)-ism$'
  SYSTEM: '(^\\..*)$'
  DATED: '(.*)-(\\d{4})\\.(\\d{2})\\.(\\d{2})$'

"""

OPTIC_COLOR = OpticColor()


def initialize_optic() -> None:
    """
    Initializes the Optic configuration by setting up the cluster configuration,
    default settings, and shell completion.

    :return: None
    :rtype: None
    """
    setup_cluster_config()
    setup_settings()
    setup_shell_completion()


def setup_cluster_config() -> None:
    """
    Sets up sample cluster config file

    :return: None
    :rtype: None
    """
    cluster_config_path = os.path.expanduser(f"{CONFIG_BASE_DIR}/cluster-config.yaml")

    # Prompts user for permission to create cluster config file if file does not exists
    if not validate_file_exists(cluster_config_path):
        create_cluster_config = prompt_question(
            f"Would you like to create a cluster configuration file at "
            f"{OPTIC_COLOR.OK_CYAN}{cluster_config_path}{OPTIC_COLOR.STOP}?"
        )
        if create_cluster_config:
            if not os.path.exists(os.path.expanduser(CONFIG_BASE_DIR)):
                os.makedirs(os.path.expanduser(CONFIG_BASE_DIR))

            f = open(cluster_config_path, "w")
            f.write(SAMPLE_CLUSTER_CONFIG)
            f.close()
            print(
                f"Sample cluster configuration file created: "
                f"{OPTIC_COLOR.OK_CYAN}{cluster_config_path}{OPTIC_COLOR.STOP}"
            )
            print(
                f"{OPTIC_COLOR.WARNING}NOTE:{OPTIC_COLOR.STOP} "
                f"This file contains dummy information that must be replaced"
            )
    else:
        print(
            f"Cluster configuration file: "
            f"{OPTIC_COLOR.OK_CYAN}{cluster_config_path}{OPTIC_COLOR.STOP} "
            "already exists"
        )


def setup_settings() -> None:
    """
    Sets up default settings file

    :return: None
    :rtype: None
    """
    settings_file_path = os.path.expanduser(f"{CONFIG_BASE_DIR}/optic-settings.yaml")

    # Prompts user for permission to create a settings file
    if not validate_file_exists(settings_file_path):
        create_settings_file = prompt_question(
            f"Would you like to set up a settings file at "
            f"{OPTIC_COLOR.OK_CYAN}{settings_file_path}{OPTIC_COLOR.STOP}?"
        )
        if create_settings_file:
            if not os.path.exists(os.path.expanduser(CONFIG_BASE_DIR)):
                os.makedirs(os.path.expanduser(CONFIG_BASE_DIR))

            f = open(settings_file_path, "w")
            f.write(SAMPLE_SETTINGS)
            f.close()
            print(
                f"Default settings file created: "
                f"{OPTIC_COLOR.OK_CYAN}{settings_file_path}{OPTIC_COLOR.STOP}"
            )
    else:
        print(
            f"Settings file: {OPTIC_COLOR.OK_CYAN}{settings_file_path}{OPTIC_COLOR.STOP} already exists"
        )


def get_shell_configuration_file(extension):
    """
    Returns the path to a shell configuration file based on the given extension.

    Args:
    extension (str): The shell type (e.g., "bash", "zsh").

    Returns:
    str: The path to the shell configuration file.
    """
    return os.path.expanduser(f"~/.{extension}rc")


def get_shell_env() -> str:
    """
    Gets shell type from environment variable
    :return: Shell executable file path
    :rtype: str
    :raises OpticConfigurationFileError: if $SHELL environment variable is not set
    """
    # TODO: Make more robust to detect non-POSIX shells, shells-in-shells, etc.
    try:
        return environ["SHELL"]
    except KeyError:
        raise OpticConfigurationFileError("Error: Non-POSIX compliant shell")


def setup_shell_completion() -> None:
    """
    Sets up shell completion based off shell type

    :param str shell_env: Shell executable file path
    :return: None
    :rtype: None
    """
    shell_env = get_shell_env()
    match shell_env:
        case "/bin/zsh":
            configure_shell_to_use_completion("zsh")
        case "/bin/bash":
            configure_shell_to_use_completion("bash")
        case _:
            print("Non-supported shell environment", shell_env)


def configure_shell_to_use_completion(extension) -> None:
    """
    Configures the shell to use completion by creating a shell completion script
    and appending it to the shell configuration file.

    The script is created and appended to the shell configuration file (.bashrc or .zshrc).

    Args:
        extension (str): The type of shell (e.g., "bash", "zsh").

    Returns:
        None
    """

    # Shell complete file path
    shell_complete_path = os.path.expanduser(
        f"{CONFIG_BASE_DIR}/.optic-complete.{extension}"
    )

    # Prompts user for permission to setup shell completion
    # in case a shell complete file does not exist
    if not validate_file_exists(shell_complete_path):
        create_shell_completion = prompt_question(
            f"Would you like to set up shell completion?\n{OPTIC_COLOR.WARNING}NOTE:{OPTIC_COLOR.STOP}"
            f"This will involve appending a command to source it to your shell configuration file"
        )
        if create_shell_completion:
            # Create config base dir if it doesn't exist
            if not os.path.exists(os.path.expanduser(CONFIG_BASE_DIR)):
                os.makedirs(os.path.expanduser(CONFIG_BASE_DIR))

            # Create .optic-complete script file
            os.system(  # noqa: S605, S607
                f"_OPTIC_COMPLETE={extension}_source optic > {CONFIG_BASE_DIR}/.optic-complete.{extension}"
            )
            print(
                f"Shell completion script created: {OPTIC_COLOR.OK_CYAN}{shell_complete_path}{OPTIC_COLOR.STOP}"
            )

            # Shell configuration file (.bashrc or .zshrc)
            shell_configuration_file = get_shell_configuration_file(extension)

            # Validate that shell configuration file exists (.bashrc or .zshrc)
            # and create it if it doesn't exist
            if not os.path.exists(shell_configuration_file):
                print(f"File: {shell_configuration_file} not found at")
                print(f"Creating {shell_configuration_file}")

            # Open shell complete file path and append
            # shell completion script sourcing
            f = open(shell_configuration_file, "a")
            f.write("\n")

            if extension == "zsh":
                f.write("autoload -U +X compinit && compinit\n")

            f.write(f". {CONFIG_BASE_DIR}/.optic-complete.{extension}")
            f.write("\n")
            f.close()

            print(
                f"Added shell completion script sourcing to: "
                f"{OPTIC_COLOR.OK_CYAN}{shell_configuration_file}{OPTIC_COLOR.STOP}"
            )
            print("Shell completion setup complete")
            print("RESTART shell to enable shell completion")
    else:
        print("Shell completion is already setup")


def validate_file_exists(file_path: str) -> bool:
    """
    Checks if the given file path exists and is a file.

    Args:
        file_path (str): Path to the file.

    Returns:
        bool: True if the file exists, False otherwise.
    """
    return os.path.isfile(file_path)
