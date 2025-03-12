# OPTIC (OpenSearch Tools for Indices and Clusters)

## Table of Contents
* **[What is OPTIC?](#what-is-optic)**
* **[Requirements](#Requirements)**
  * [Python3 Installation](#python3-installation)
  * [Cluster Configuration File Setup](#cluster-configuration-file-setup)
  * [Settings File Setup](#settings-file-setup)
* **[Installation](#installation)**
  * [Prepare Python Virtual Environment](#prepare-python-virtual-environment)
  * [Clone Repository](#clone-repository)
  * [Install Project Dependencies](#install-project-dependencies)
  * [Initialize OPTIC](#initialize-optic)
* **[CLI Usage](#cli-usage)**
* **[OPTIC as Library](#optic-as-library)**
  * [Common Patterns](#common-patterns)
  * [get_cluster_info()](#get_cluster_info)
  * [get_index_info()](#get_index_info)
  * [get_alias_info()](#get_alias_info)

## What is OPTIC?
OPTIC (OpenSearch Tools for Indices and Clusters) is a Python language tool suite designed to offer OpenSearch Engineers
utilities to troubleshoot, analyze, and make changes to OpenSearch clusters and indices.  OPTIC is designed to offer
both a rich command line experience and a library that can be called from other pieces of code.

OPTIC's command line utilities are organized into a tool domain hierarchy (shown below).  This approach allows OPTIC tools to be
modular, reuse information, and be intuitively called from the command line (described in [CLI Usage](#cli-usage)).  Currently, OPTIC supports:
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

### Cluster Configuration File Setup
* A properly formatted cluster configuration file is necessary to use the OPTIC toolset.
* The default path for this configuration file is ```~/.optic/cluster-config.yaml``` (Can be defined in settings)
* A custom configuration file path can be specified in the settings file or using the Command Line Interface (detailed
in [Settings](#settings-file-setup) and [CLI Usage](#cli-usage))
* **The Configuration File allows users to easily store networking and authentication information for communicating with their OpenSearch Clusters.**
* **It also allows users to collect clusters into custom groups that can simplify cluster information gathering and administration**
* **A sample configuration file provided below <mark>can be generated using optic init</mark> (detailed in [Installation](#installation)):**
```yaml
clusters:
  cluster_1:
    url: https://testurl.com:9100
    username: my_username1
    password: my_password
    verify_ssl: true
  cluster_2:
    url: https://myurl.com:9200
    username: my_username2
    password: '****'
  my_cluster:
    url: https://onlineopensearchcluster.com:9300
    username: my_username3
    password: '****'
  cluster_3:
    url: https://anotherurl.com:9400
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


```
* The verify_ssl field is optional (default is true if omitted)

* The groups field is optional

* Cluster and groups should not have identical names

* It is recommended to put all string values containing YAML special characters in single quotes to prevent unintended behavior.  These characters can include {, }, [, ], ,, &, :, *, #, ?, |. -, <. >, =, !, %, @, \

### Settings File Setup
* A properly formatted settings file is necessary to use the OPTIC toolset.
* The default path for this configuration file is ```~/.optic/optic-settings.yaml```
* A custom settings file path can be specified using the Command Line Interface (detailed in [CLI Usage](#cli-usage))
* **The Settings File allows users to easily set preferences for their OPTIC tools.**
* **A default settings file provided below <mark>can be generated using optic init</mark> (detailed in [Installation](#installation)):**
```yaml
# File Paths
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
  ISM: '(.*)-ism-(\d{6})$'
  ISM_MALFORMED: '(.*)-ism$'
  SYSTEM: '(^\..*)$'
  DATED: '(.*)-(\d{4})\.(\d{2})\.(\d{2})$'

```
* It is recommended to put all string values containing YAML special characters in single quotes to prevent unintended behavior.  These characters can include {, }, [, ], ,, &, :, *, #, ?, |. -, <. >, =, !, %, @, \

## Installation
### Prepare Python Virtual Environment
We'll start by creating a new Python virtual environment to isolate our project's dependencies from other projects or
system-wide installations. This ensures that your project runs consistently on any machine with the same environment
setup.

**If you do not wish to set up a separate Python virtual environment for OPTIC, this step can be skipped**

#### Using pyenv
This approach requires setting up pyenv first.  Learn more at [pyenv's repository](https://github.com/pyenv/pyenv?tab=readme-ov-file#installation)
Additionally, this approach requires the virtualenv plugin for pyenv.  Learn more at [pyenv virtualenv's repo](https://github.com/pyenv/pyenv-virtualenv)
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

### Clone Repository
* Clone this repo
* Enter the optic directory that was just created using ```cd optic```

### Install Project Dependencies
* Once your virtual environment is active, upgrade the pip package manager to the latest version using:
```bash
pip install --upgrade pip
```
* If you wish to use OPTIC as a user, follow the instructions directly below.  If you wish to develop OPTIC, follow the
Developer Instructions

#### User Instructions
* This command will install the project dependencies from a local repository in the current working directory and allow use of the command line tools.
```bash
pip install .
```
#### Developer Instructions
* This command will install the standard project dependencies and development dependencies from the current working directory.
* These will be installed in editable mode, meaning
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

## CLI Usage
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

## OPTIC as Library
OPTIC is also designed to be able to be used as a library by external.  OPTIC exposes various functions and classes 
(listed in the top level __init__.py) for developers to call externally.  The recommended way to call OPTIC functionality
is described below by example.

### Common Patterns
The recommended way to call OPTIC functionality from code is generally as follows:
* Define cluster information programmatically (see examples below)
* Specify desired cluster and cluster group names to act on in a list (this can be any subset of the ones defined above)
* Specify any specific cluster properties required for an action in a dictionary (these vary by query and are provided below)
* This information is provided to OPTIC by constructing a ClusterConfig object using the information above
* Call the desired action w/ the ClusterConfig object as an argument and use any returned data as desired

### get_cluster_info()
Properties specific to get_cluster_info are:

    byte_type - specify a storage unit for the query (mb or gb)

The sample code below queries cluster information from a selection of clusters and prints the results:
```python
import optic
import json

cluster_info = {
    "clusters": {
        "cluster_1": {
            "url" : "https://exampleurl.com",
            "username": "example_username",
            "password": "****",
            "verify_ssl": False
        },
        "cluster_2": {
            "url" : "https://exampleurl2.com",
            "username": "example_username",
            "password": "****",
        },
        "cluster_3": {
            "url" : "https://exampleurl3.com",
            "username": "example_username",
            "password": "****",
        },
        "cluster_4": {
            "url" : "https://exampleurl4.com",
            "username": "example_username",
            "password": "****",
        }
    },
    "groups": {
        "group1": [
            "cluster_3",
            "cluster_4"
        ],
        "g2": [
            "cluster_2",
            "cluster_3"
        ]
    }
}
desired_clusters = ["cluster_3", "g2"]
desired_cluster_properties = {
    "byte_type": "mb"
}
cluster_generator = optic.ClusterConfig(cluster_info, desired_clusters, desired_cluster_properties)

cluster_info_response = optic.get_cluster_info(cluster_generator)
print("CLUSTER INFORMATION")
print(json.dumps(cluster_info_response, indent=3))
```
### get_index_info()
Properties specific to get_index_info are:

    index_search_pattern - specify a glob search pattern for the query
    index_types_dict - specify a dictionary with index_type_name -> regular_expression pairs

Additionally, get_index_info can support two more <mark>optional</mark> parameters that allow for more advanced filtering and sorting of data:

    filters - a dictionary that allows users to specify filters to exclude indices that meet certain condtions
    sort_by - a list that allows users to specify sort order for returned index data

    filters allows filters of the following types:
          "write_alias_only" - (bool) whether to report only indices that are targets of write aliases (True: only write alias targets reported, False: write alias targets excluded, None: no effect)
          "min_age" - (int) a minimum age in days for indices to be reported
          "max_age" - (int) a maximum age in days for indices to be reported
          "min_index_size" - (string) a minimum index size for indices to be reported (e.g. "7mb", "4.23gb", "1kb", etc)
          "max_index_size - (string) a maximum index size for indices to be reported (e.g. "7mb", "4.23gb", "1kb", etc)
          "min_shard_size" - (string) a minimum shard size for indices to be reported (e.g. "7mb", "4.23gb", "1kb", etc)
          "max_shard_size" - (string) a maximum shard size for indices to be reported (e.g. "7mb", "4.23gb", "1kb", etc)
          "min_doc_count" - (int) a minimum document count for indices to be reported
          "max_doc_count" - (int) a maximum document count for indices to be reported
          "type_filter"- (list[string]) a list of index types (as specified in index_types_dict) to exclude from report

    sort_by allows sorting by (age, name, write-alias, index-size, shard-size, doc-count, type, primary-shards, replica-shards)



The sample code below queries index information from a cluster and prints the results:
```python
import optic
import json

cluster_info = {
    "clusters": {
        "cluster_1": {
            "url" : "https://exampleurl.com",
            "username": "example_username",
            "password": "****",
            "verify_ssl": False
        },
        "cluster_2": {
            "url" : "https://exampleurl2.com",
            "username": "example_username",
            "password": "****",
        },
        "cluster_3": {
            "url" : "https://exampleurl3.com",
            "username": "example_username",
            "password": "****",
        },
        "cluster_4": {
            "url" : "https://exampleurl4.com",
            "username": "example_username",
            "password": "****",
        }
    },
    "groups": {
        "group1": [
            "cluster_3",
            "cluster_4"
        ],
        "g2": [
            "cluster_2",
            "cluster_3"
        ]
    }
}
desired_clusters = ["cluster_1"]
filters = {
    "write_alias_only": None,
    "min_age": 10,
    "max_age": None,
    "min_index_size": None,
    "max_index_size": None,
    "min_shard_size": "100kb",
    "max_shard_size": None,
    "min_doc_count": None,
    "max_doc_count": None,
    "type_filter": ["SYSTEM"],
}
sort_by = ["age"]
types_dict = {
  "ISM": '(.*)-ism-(\\d{6})$',
  "ISM_MALFORMED": '(.*)-ism$',
  "SYSTEM": '(^\\..*)$',
  "DATED": '(.*)-(\\d{4})\\.(\\d{2})\\.(\\d{2})$',
}
desired_cluster_properties = {
    "index_search_pattern": "*",
    "index_types_dict": types_dict,
}
cluster_generator = optic.ClusterConfig(cluster_info, desired_clusters, desired_cluster_properties)
index_info_response = optic.get_index_info(cluster_generator, filters, sort_by)
print("INDEX INFORMATION")
print(json.dumps(index_info_response, indent=3))
```

### get_alias_info()
Properties specific to get_alias_info are:

    index_search_pattern - specify a glob search pattern for the query

The sample code below queries alias information from a selection of clusters and prints the results:
```python
import optic
import json

cluster_info = {
    "clusters": {
        "cluster_1": {
            "url" : "https://exampleurl.com",
            "username": "example_username",
            "password": "****",
            "verify_ssl": False
        },
        "cluster_2": {
            "url" : "https://exampleurl2.com",
            "username": "example_username",
            "password": "****",
        },
        "cluster_3": {
            "url" : "https://exampleurl3.com",
            "username": "example_username",
            "password": "****",
        },
        "cluster_4": {
            "url" : "https://exampleurl4.com",
            "username": "example_username",
            "password": "****",
        }
    },
    "groups": {
        "group1": [
            "cluster_3",
            "cluster_4"
        ],
        "g2": [
            "cluster_2",
            "cluster_3"
        ]
    }
}
desired_clusters = ["cluster_3", "g2"]
desired_cluster_properties = {
    "index_search_pattern": "*",
}
cluster_generator = optic.ClusterConfig(cluster_info, desired_clusters, desired_cluster_properties)

cluster_info_response = optic.get_alias_info(cluster_generator)
print("ALIAS INFORMATION")
print(json.dumps(cluster_info_response, indent=3))
```


## Contributing

This project welcomes contributions from the community. Before submitting a pull request, please [review our contribution guide](./CONTRIBUTING.md)


## Security

Please consult the [security guide](./SECURITY.md) for our responsible security vulnerability disclosure process

## License

Copyright (c) [year,] year Oracle and/or its affiliates.
Copyright (c) 2024-2025 Oracle and/or its affiliates.

Released under the Universal Permissive License v1.0 as shown at
<https://oss.oracle.com/licenses/upl/>.
