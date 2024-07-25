# OPTIC (OpenSearch Tools for Indices and Clusters)

## Table of Contents
* **[What is OPTIC?](#what-is-optic)**
* **[Requirements](#Requirements)**
  * [Python3 Installation](#python3-installation)
  * [Pip Installation](#pip-installation)
  * [Cluster Configuration File Setup](#cluster-configuration-file-setup)
  * [Settings File Setup](#settings-file-setup)
* **[Installation](#installation)**
  * [Clone Repository](#clone-repository)
  * [Prepare Python Virtual Environment](#prepare-python-virtual-environment)
  * [Install Project Dependencies](#install-project-dependencies)
  * [Initialize OPTIC](#initialize-optic)
* **[Usage](#usage)**

## What is OPTIC?
OPTIC (OpenSearch Tools for Indices and Clusters) is a Python language tool suite designed to offer OpenSearch Engineers
utilities to troubleshoot, analyze, and make changes to OpenSearch clusters and indices.  OPTIC is designed to offer
both a rich command line experience and a library that can be called from other pieces of code.

OPTIC's command line utilities are organized into a tool domain hierarchy (shown below).  This approach allows OPTIC tools to be
modular, reuse information, and be intuitively called from the command line (described in [Usage](#usage)).  Currently, OPTIC supports:
- ```cluster```:  Tool domain containing tools related to OpenSearch clusters
  - ```info```: Tool displaying key information (Health Status, Storage Percentage) about clusters
- ```index```:  Tool domain containing tools related to OpenSearch indices
  - ```info```: Tool displaying key information (Name, Age, Document Count, Index Size, etc.) about indices
- ```alias```:  Tool domain containing tools related to OpenSearch aliases
  - ```info```: Tool displaying key information (Index Targets, Write Target?, Filtered Alias?, etc.) about aliases

## Requirements
* Python **>3.12** is <mark>required</mark> to run the OPTIC toolset.

* Python package manager pip **>21.3** is <mark>required</mark>

* A properly formatted cluster configuration file is <mark>required</mark> to use OPTIC CLI

* A properly formatted settings file is <mark>required</mark> to use OPTIC CLI


### Python3 Installation

* Open the Terminal app (Mac) or a command line tool such as the Windows Command Prompt (Windows):
* Type the following command and press Enter:
    ```
    python3 --version
    ```

* If Python is installed, you will see a message like this:
    ```
    Python 3.x
    ```
    where ```x``` is the version of Python 3 installed

* If Python is not installed, you will get the following error:
    ```
    command not found: python3
    ```



If you see an error message, you can install Python using the official [Python website](https://www.python.org/downloads/)

### Pip Installation:
* Enter the following in the command line:
  ```
  pip -V
  ```

* Depending on your system, you may have to enter:
  ```
  python3 -m pip -V
  ```
If pip is not installed correctly, it can be installed using the [official instructions](https://pip.pypa.io/en/stable/installation/)

### Cluster Configuration File Setup
* A properly formatted cluster configuration file is necessary to use the OPTIC toolset.
* The default path for this configuration file is ```~/.optic/cluster-config.yaml``` (Can be defined in settings)
* A custom configuration file path can be specified in the settings file or using the Command Line Interface (detailed
in [Settings](#settings-file-setup) and [Usage](#usage))
* **The Configuration File allows users to easily store networking and authentication information for communicating with their OpenSearch Clusters.**
* **It also allows users to collect clusters into custom groups that can simplify cluster information gathering and administration**
* **A sample configuration file provided below <mark>can be generated using optic init</mark> (detailed in [Installation](#installation)):**
```yaml
clusters:
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


```
* The groups field is optional

* Cluster and groups should not have identical names

* It is recommended to put all settings string values in single quotes to prevent YAML escape characters from causing unintended behavior

### Settings File Setup
* A properly formatted settings file is necessary to use the OPTIC toolset.
* The default path for this configuration file is ```~/.optic/optic-settings.yaml```
* A custom settings file path can be specified using the Command Line Interface (detailed in [Usage](#usage))
* **The Settings File allows users to easily set preferences for their OPTIC tools.**
* **A default settings file provided below <mark>can be generated using optic init</mark> (detailed in [Installation](#installation)):**
```yaml
# File Paths
settings_file_path: '~/.optic/optic-settings.yaml'
default_cluster_config_file_path: '~/.optic/cluster-config.yaml'

# Terminal Customization
disable_terminal_color: False

# Cluster Info Settings
default_cluster_info_byte_type: 'gb'
storage_percent_thresholds:
  GREEN: 80
  YELLOW: 85
  RED: 100

# Index/Alias Info Settings
default_search_pattern: '*'
default_index_type_patterns:
  ISM: '(.*)-ism-(\d{6})$'
  ISM_MALFORMED: '(.*)-ism$'
  SYSTEM: '(^\..*)$'
  DATED: '(.*)-(\d{4})\.(\d{2})\.(\d{2})$'

```
* It is recommended to put all settings string values in single quotes to prevent YAML escape characters from causing unintended behavior

## Installation
### Clone Repository
* Navigate to a directory where you would like to have the OPTIC repository using ```cd <directory-path>```
* Clone the following repo: [https://cloudlab.us.oracle.com/gbucs/gpdaf/opensearch/optic](https://cloudlab.us.oracle.com/gbucs/gpdaf/opensearch/optic)
* Enter the optic directory that was just created using ```cd optic```

### Prepare Python Virtual Environment
We'll start by creating a new Python virtual environment to isolate our project's dependencies from other projects or
system-wide installations. This ensures that your project runs consistently on any machine with the same environment
setup.

**If you do not wish to set up a separate Python virtual environment for OPTIC, this step can be skipped**

#### Using pyenv
This approach requires setting up pyenv first.  Learn more at [pyenv's repository](https://github.com/pyenv/pyenv?tab=readme-ov-file#installation)
```bash
pyenv virtualenv <python-version> <virtual-env-name>

# Example (uses Python 3.12.2, use your desired version)
pyenv virtualenv 3.12.2 optic_3.12.2

# Activate Virtual Env
pyenv activate optic_3.12.2
```

#### Using venv
```bash
python3 -m venv <environment_name>

# Example
python3 -m venv env

# Activate Virtual Env
source env/bin/activate
```


### Install Project Dependencies
* Once your virtual environment is active, upgrade the pip package manager to the latest version using:
```bash
pip install --upgrade pip
```
* If you wish to use OPTIC as a user, follow the instructions directly below.  If you wish to develop OPTIC, follow the
Developer Instructions
#### User Instructions
* This command will install the project dependencies and allow use of the command line tools.
```bash
pip install .
```
#### Developer Instructions
* This command will install the standard project dependencies and development dependencies in editable mode, meaning
any changes made to the source files will be immediately available without reinstallation.
```bash
pip install -e '.[dev]'
```
* This command will install OPTIC's pre-commit hooks, which will run formatting and linting checks before making a commit.
```bash
pre-commit install
```


### Initialize OPTIC
OPTIC's CLI can be easily initialized using the built-in init function:
```bash
optic init
```
This will prompt the user for permission to write default configuration files and to set up automatic shell completion

## Usage
To use the OPTIC Command Line Interface, use the following format
```
optic <tool_domain> <tool_name> <command_line_options>
```
For a full list of OPTIC tool domains, enter:
```
optic --help
```
For a full list of OPTIC tools for a particular domain, enter:
```
optic <tool_domain> --help
```
For a full list of the command line options available for each tool, enter:
```
optic <tool_domain> <tool_name> --help
```
To run OPTIC with an alternate settings file path, enter:
```
optic --settings-path <custom_file_path> <tool_domain> <tool_name>
```
