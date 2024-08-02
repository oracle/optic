# ** OPTIC version 1.0.0
# **
# ** Copyright (c) 2024 Oracle Corporation
# ** Licensed under the Universal Permissive License v 1.0
# ** as shown at https://oss.oracle.com/licenses/upl/

import os
from os import environ

from optic.common.exceptions import OpticConfigurationFileError

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


def initialize_optic(cluster_config_setup, settings_setup, shell_setup) -> None:
    """
    Sets up OPTIC's necessary user directories and files

    :param bool cluster_config_setup: Whether to set up cluster config
    :param bool settings_setup: Whether to set up settings file
    :param bool shell_setup: Whether to set up shell completion
    :return: None
    :rtype: None
    """
    if cluster_config_setup:
        setup_cluster_config()
    if settings_setup:
        setup_settings()
    if shell_setup:
        shell_env = get_shell_env()
        setup_shell_completion(shell_env)


def setup_cluster_config() -> None:
    """
    Sets up sample cluster config file

    :return: None
    :rtype: None
    :raises OpticConfigurationFileError: if file already exists
    """
    abs_path = os.path.expanduser("~/.optic/cluster-config.yaml")
    if not os.path.exists(os.path.expanduser("~/.optic")):
        os.makedirs(os.path.expanduser("~/.optic"))
    if os.path.exists(abs_path):
        raise OpticConfigurationFileError("Error: File already exists at " + abs_path)
    f = open(abs_path, "w")
    f.write(SAMPLE_CLUSTER_CONFIG)
    f.close()
    print("Sample cluster configuration file created at", abs_path)
    print("NOTE: This file contains dummy information that must be replaced")


def setup_settings() -> None:
    """
    Sets up default settings file

    :return: None
    :rtype: None
    :raises OpticConfigurationFileError: if file already exists
    """
    abs_path = os.path.expanduser("~/.optic/optic-settings.yaml")
    if not os.path.exists(os.path.expanduser("~/.optic")):
        os.makedirs(os.path.expanduser("~/.optic"))
    if os.path.exists(abs_path):
        raise OpticConfigurationFileError("Error: File already exists at " + abs_path)
    f = open(abs_path, "w")
    f.write(SAMPLE_SETTINGS)
    f.close()
    print("Default settings file created at", abs_path)


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


def setup_shell_completion(shell_env) -> None:
    """
    Sets up shell completion based off shell type

    :param str shell_env: Shell executable file path
    :return: None
    :rtype: None
    """
    match shell_env:
        case "/bin/zsh":
            if not os.path.exists(os.path.expanduser("~/.optic")):
                os.makedirs(os.path.expanduser("~/.optic"))
            abs_path = os.path.expanduser("~/.optic/.optic-complete.zsh")
            if os.path.exists(abs_path):
                raise OpticConfigurationFileError(
                    "Error: File already exists at " + abs_path
                )
            os.system("_OPTIC_COMPLETE=zsh_source optic > ~/.optic/.optic-complete.zsh")
            print("Shell completion script created at", abs_path)
            abs_path = os.path.expanduser("~/.zshrc")
            if not os.path.exists(abs_path):
                print(".zshrc not found at", abs_path)
                print("Creating .zshrc")
            f = open(abs_path, "a")
            f.write("\n")
            f.write("autoload -U +X compinit && compinit\n")
            f.write(". ~/.optic/.optic-complete.zsh")
            f.write("\n")
            f.close()
            print("Added shell completion script sourcing to ~/.zshrc")
        case "/bin/bash":
            if not os.path.exists(os.path.expanduser("~/.optic")):
                os.makedirs(os.path.expanduser("~/.optic"))
            abs_path = os.path.expanduser("~/.optic/.optic-complete.bash")
            if os.path.exists(abs_path):
                raise OpticConfigurationFileError(
                    "Error: File already exists at " + abs_path
                )
            os.system(
                "_OPTIC_COMPLETE=bash_source optic > ~/.optic/.optic-complete.bash"
            )
            print("Shell completion script created at", abs_path)
            abs_path = os.path.expanduser("~/.bashrc")
            if not os.path.exists(abs_path):
                print(".bashrc not found at", abs_path)
                print("Creating .bashrc")
            f = open(abs_path, "a")
            f.write("\n")
            f.write(". ~/.optic/.optic-complete.bash")
            f.write("\n")
            f.close()
            print("Added shell completion script sourcing to ~/.bashrc")

        case _:
            print("Non-supported shell environment", shell_env)

    print("Shell completion setup complete")
    print("RESTART shell to enable shell completion")
