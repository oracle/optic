import os
from os import environ

from optic.common.exceptions import OpticConfigurationFileError

SAMPLE_CLUSTER_CONFIG = """clusters:
  'cluster_1':
    url: 'https://testurl.com:46'
    username: 'my_username1'
    password: 'my_password'
    verify_ssl: true
  'cluster_2':
    url: 'https://myurl.com:9200'
    username: 'my_username2'
    password: '****'
    verify_ssl: true
  'my_cluster':
    url: 'https://onlineopensearchcluster.com:634'
    username: 'my_username3'
    password: '****'
    verify_ssl: true
  'cluster_3':
    url: 'https://anotherurl.com:82'
    username: 'my_username4'
    password: '****'
    verify_ssl: true

groups:
  'my_group':
    - 'cluster_1'
    - 'cluster_2'
    - 'cluster_3'
  'g2':
    - 'cluster_1'
    - 'my_cluster'
"""

SAMPLE_SETTINGS = """settings_file_path: '~/.optic/optic-settings.yaml'
default_cluster_config_file_path: '~/.optic/cluster-config.yaml'

default_cluster_info_byte_type: 'gb'

default_index_search_pattern: '*'
default_index_type_patterns:
  ISM: '(.*)-ism-(\\d{6})$'
  ISM_MALFORMED: '(.*)-ism$'
  SYSTEM: '(^\\..*)$'
"""


def initialize_optic(cluster_config_setup, settings_setup, shell_setup):
    if cluster_config_setup:
        setup_cluster_config()
    if settings_setup:
        setup_settings()
    if shell_setup:
        shell_env = get_shell_env()
        setup_shell_completion(shell_env)


def setup_cluster_config():
    abs_path = os.path.expanduser("~/.optic/cluster-config.yaml")
    if os.path.exists(abs_path):
        raise OpticConfigurationFileError("Error: File already exists at " + abs_path)
    f = open(abs_path, "w")
    f.write(SAMPLE_CLUSTER_CONFIG)
    f.close()
    print("Sample cluster configuration file created at", abs_path)
    print("NOTE: This file contains dummy information that must be replaced")


def setup_settings():
    abs_path = os.path.expanduser("~/.optic/optic-settings.yaml")
    if os.path.exists(abs_path):
        raise OpticConfigurationFileError("Error: File already exists at " + abs_path)
    f = open(abs_path, "w")
    f.write(SAMPLE_SETTINGS)
    f.close()
    print("Default settings file created at", abs_path)


def get_shell_env():
    # TODO: Make more robust to detect non-POSIX shells, shells-in-shells, etc.
    try:
        return environ["SHELL"]
    except KeyError:
        raise OpticConfigurationFileError("Error: Non-POSIX compliant shell")


def setup_shell_completion(shell_env):
    match shell_env:
        case "/bin/zsh":
            abs_path = os.path.expanduser("~/.optic/zsh-shell-completion.sh")
            if os.path.exists(abs_path):
                raise OpticConfigurationFileError(
                    "Error: File already exists at " + abs_path
                )
            f = open(abs_path, "w")
            f.write("autoload -U +X compinit && compinit\n")
            f.write("_OPTIC_COMPLETE=zsh_source optic")
            f.close()
            print("Shell completion script created at", abs_path)
            abs_path = os.path.expanduser("~/.zshrc")
            if not os.path.exists(abs_path):
                print(".zshrc not found at", abs_path)
                print("Creating .zshrc")
            f = open(abs_path, "a")
            f.write("\n")
            f.write(". ~/.optic/zsh-shell-completion.sh")
            f.write("\n")
            f.close()
            print("Added shell completion script sourcing to ~/.zshrc")
        case "/bin/bash":
            abs_path = os.path.expanduser("~/.optic/bash-shell-completion.sh")
            if os.path.exists(abs_path):
                raise OpticConfigurationFileError(
                    "Error: File already exists at " + abs_path
                )
            f = open(abs_path, "w")
            f.write("_OPTIC_COMPLETE=bash_source optic")
            f.close()
            print("Shell completion script created at", abs_path)
            abs_path = os.path.expanduser("~/.bashrc")
            if not os.path.exists(abs_path):
                print(".bashrc not found at", abs_path)
                print("Creating .bashrc")
            f = open(abs_path, "a")
            f.write("\n")
            f.write(". ~/.optic/bash-shell-completion.sh")
            f.write("\n")
            f.close()
            print("Added shell completion script sourcing to ~/.bashrc")

        case _:
            print("Non-supported shell environment", shell_env)

    print("Shell completion setup complete")
    print("RESTART shell to enable shell completion")
