# OPTIC (OpenSearch Tools for Indices and Clusters)

## Table of Contents
* [What is OPTIC?](#what-is-optic)
* [QuickStart](#quickstart)
* [Requirements](#requirements)
* [Installation](#installation)
  * [User Installation Instructions](#user-installation-instructions)
  * [Developer Installation Instructions](#developer-installation-instructions)
  * [Initialize OPTIC](#initialize-optic)
  * [Understanding OPTIC Configuration](#understanding-optic-configuration)
    * [Cluster Configuration File](#cluster-configuration-file)
    * [Settings File](#settings-file)
* [Using the OPTIC CLI](#using-the-optic-cli)
* [OPTIC as Library](#optic-as-library)
  * [Common Patterns](#common-patterns)
  * [get_cluster_info()](#get_cluster_info)
  * [get_index_info()](#get_index_info)
  * [get_alias_info()](#get_alias_info)

## What is OPTIC?
OPTIC (OpenSearch Tools for Indices and Clusters) is a Python language tool suite designed to offer OpenSearch users
utilities to troubleshoot, analyze, and make changes to OpenSearch clusters and indices.  OPTIC is designed to offer
both a rich command line experience and a library that can be called from other pieces of code.

OPTIC's command line utilities are organized into a tool domain hierarchy (shown below).  This approach allows OPTIC tools to be
modular, reuse information, and be intuitively called from the command line (described in [Using the OPTIC CLI](#using-the-optic-cli)).  Currently, OPTIC supports:
- ```cluster```:  Tool domain containing tools related to OpenSearch clusters
  - ```info```: Tool displaying key information (Health Status, Storage Percentage) about clusters
- ```index```:  Tool domain containing tools related to OpenSearch indices
  - ```info```: Tool displaying key information (Name, Age, Document Count, Index Size, etc.) about indices
- ```alias```:  Tool domain containing tools related to OpenSearch aliases
  - ```info```: Tool displaying key information (Index Targets, Write Target?, Filtered Alias?, etc.) about aliases


## QuickStart
To get started with OPTIC, follow these simple steps:

* Run the following command to install OPTIC from PyPI:
```sh
pip install opensearch-optic
```
* Initialize OPTIC and create default configuration files:
```sh
optic init
```

* Edit the generated `~/.optic/cluster-config.yaml` file to add your OpenSearch clusters information.


#### Example commands to get you started:

Display cluster information from the cluster named `cluster_1`:
```sh
optic cluster info -c cluster_1
```
Display cluster information from the group of clusters named `cluster_group`:
```sh
optic cluster info -c cluster_group
```

Find all indexes from the cluster `cluster_1`:
```sh
optic index info -c cluster_1
```

Find indexes from the cluster `cluster_1` that match the pattern `first-index*`:
```sh
optic index info -c cluster_1 -p "first-index*"
```

Find aliases from the cluster `cluster_1` that match the pattern `first-alias*`:
```sh
optic index info -c cluster_1 -p "first-alias*"
```

For more information, see the sections below for detailed instructions and usage examples.

## Requirements
* Python **>3.12** is <mark>required</mark> to run the OPTIC toolset.
* Python package manager pip **>21.3** is <mark>required</mark>


## Installation
### User Installation Instructions
For the quickest way to get started using OPTIC, follow these simple instructions below. If you would like to dig into the source code, or contribute back to the repository, take a look at our detailed [Developer Installation Instructions](#developer-installation-instructions) further on in the documentation.

* Upgrade the pip package manager to the latest version using:
```bash
pip install --upgrade pip
```

* This command will install the project from PyPI (Python Package Index) in the current working directory and allow use of the command line tools.
```bash
pip install opensearch-optic
```
* Follow the instructions in the [Initialize OPTIC](#initialize-optic) section to complete the setup.


### Developer Installation Instructions
* Clone this repo
* Enter the optic directory that was just created using ```cd optic```

* This command will install the standard project dependencies and development dependencies from the current working directory in editable mode, meaning any changes made to the source files will be immediately available without reinstallation.
```bash
pip install -e '.[dev]'
```
* This command will install OPTIC's pre-commit hooks, which will run formatting and linting checks before making a commit.
```bash
pre-commit install
```
* Follow the instructions in the [Initialize OPTIC](#initialize-optic) section to complete the setup.

### Initialize OPTIC
OPTIC's CLI can be easily initialized using the built-in init command:
```bash
optic init
```
This will prompt the user for permission to write default configuration files and to set up automatic shell completion.

### Understanding OPTIC Configuration
OPTIC relies on two configuration files created during the initialization process:
* [Cluster Configuration File](#cluster-configuration-file)
* [Settings File](#settings-file)

#### Cluster Configuration File
* A properly formatted cluster configuration file is necessary to use the OPTIC toolset.
* The default path for this configuration file is ```~/.optic/cluster-config.yaml``` (Can be defined in settings)
* A custom configuration file path can be specified in the settings file or using the Command Line Interface (detailed
in [Settings](#settings-file) and [Using the OPTIC CLI](#using-the-optic-cli))
* The Configuration File allows users to easily store networking and authentication information for communicating with their OpenSearch Clusters.
* It also allows users to collect clusters into custom groups that can simplify cluster information gathering and administration
* A sample configuration file provided below <mark>can be generated using the `optic init` command</mark> (see: [Initialize OPTIC](#initialize-optic)):
```yaml
clusters:
  prod-lga:
    url: https://prod-lga.example.com:9200
    username: oracle
    password: my_password
  prod-jfk:
    url: https://prod-jfk.example.com:9200
    username: oracle
    password: '****'
  prod-sfo:
    url: https://prod-sfo.example.com:9200
    username: oracle
    password: '****'
  stage-lga:
    url: https://stage-lga.example.com:9200
    username: oracle
    password: my_password
  stage-jfk:
    url: https://stage-jfk.example.com:9200
    username: oracle
    password: '****'
  stage-sfo:
    url: https://stage-sfo.example.com:9200
    username: oracle
    password: '****'
  dev-lga:
    url: https://dev-lga.example.com:9200
    username: oracle
    password: my_password
  dev-jfk:
    url: https://dev-jfk.example.com:9200
    username: oracle
    password: '****'
groups:
  dev:
    - dev-lga
    - dev-jfk
  stage:
    - stage-lga
    - stage-jfk
    - stage-sfo
  production:
    - prod-lga
    - prod-jfk

```
* The verify_ssl field is optional (default is true if omitted)
* The groups field is optional
* Cluster and groups should not have identical names
* It is recommended to put all string values containing YAML special characters in single quotes to prevent unintended behavior.  These characters can include {, }, [, ], ,, &, :, *, #, ?, |. -, <. >, =, !, %, @, \

#### Settings File
* A properly formatted settings file is necessary to use the OPTIC toolset.
* The default path for this configuration file is ```~/.optic/optic-settings.yaml```
* A custom settings file path can be specified using the Command Line Interface (detailed in [Using the OPTIC CLI](#using-the-optic-cli))
* The Settings File allows users to easily set preferences for their OPTIC tools.
* A default settings file provided below <mark>can be generated using the `optic init` command</mark> (see: [Initialize OPTIC](#initialize-optic)):
```yaml
# File Paths
cluster_config_file_path: ~/.optic/cluster-config.yaml

# Terminal Customization
disable_terminal_color: False

# Cluster Info Settings
byte_type: gb
storage_percent_thresholds:
  GREEN: 80
  YELLOW: 85
  RED: 100

# Index/Alias Info Settings
search_pattern: '*'
index_type_patterns:
  ISM: '(.*)-ism-(\d{6})$'
  ISM_MALFORMED: '(.*)-ism$'
  SYSTEM: '(^\..*)$'
  DATED: '(.*)-(\d{4})\.(\d{2})\.(\d{2})$'

```
* It is recommended to put all string values containing YAML special characters in single quotes to prevent unintended behavior.  These characters can include {, }, [, ], ,, &, :, *, #, ?, |. -, <. >, =, !, %, @, \


## Using the OPTIC CLI
For a full list of OPTIC tool domains, enter:
```
optic --help
```
To use the OPTIC Command Line Interface, use the following format
```
optic <tool_domain> <tool_name> <command_line_options>
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
optic --settings <custom_file_path> <tool_domain> <tool_name>
```

To display information about clusters from a group of clusters called `my_cluster_group`, enter:
```sh
optic cluster info -c my_cluster_group
```

**Example output:**

```
+Cluster Info-------------+--------+-----------------+
| Cluster                 | Status | Storage Use (%) |
+-------------------------+--------+-----------------+
| action-packed-cluster   | yellow | 80              |
| behind-the-scenes       | green  | 62              |
| cult-classics-cluster   | green  | 83              |
| scene-by-scene-cluster  | green  | 73              |
+-------------------------+--------+-----------------+
```


To find all indexes from a group of clusters called `my_cluster_group`, enter:
```sh
optic index info -c my_cluster_group
```

**Example output:**

```
+Index Info--------------------------------+-----+--------+----------------+------------+------------+-----+-----+-------------+--------------+
| Index                                    | Age | Type   | Document Count | Index Size | Shard Size | Pri | Rep | Write Alias | Cluster      |
+------------------------------------------+-----+--------+----------------+------------+------------+-----+-----+-------------+--------------+
| lord_of_the_indexes-ism-000100           | 12  | ISM    | 2033895        | 293.9mb    | 146.95mb   | 2   | 1   | True        | cluster_1    |
| lord_of_the_indexes-ism-000101           | 12  | ISM    | 2033895        | 293.9mb    | 146.95mb   | 2   | 1   | True        | cluster_1    |
| game_of_clusters-ism-000105              | 36  | ISM    | 8862623        | 8.1gb      | 4.05gb     | 2   | 1   | True        | cluster_2    |
| the_godfather_of_all_indexes-ism-001972  | 89  | ISM    | 683308950      | 19.1gb     | 9.55gb     | 2   | 1   | True        | cluster_3    |
+------------------------------------------+-----+--------+----------------+------------+------------+-----+-----+-------------+--------------+
```


The `index info` functionality supports pattern matching using wildcards. For instance, to find all indexes from cluster: `cluster_1` with a common prefix and displaying the results sorted by index name, you can use the following command:
```sh
optic index info -c cluster_1 -p "rocketship*" -s name
```

**Example output:**
```
+Index Info----------------------------+-----+--------+----------------+------------+------------+-----+-----+-------------+--------------+
| Index                                | Age | Type   | Document Count | Index Size | Shard Size | Pri | Rep | Write Alias | Cluster      |
+--------------------------------------+-----+--------+----------------+------------+------------+-----+-----+-------------+--------------+
| rocketship_communication-ism-000020  | 20  | ISM    | 234955         | 545.9mb    | 272.95mb   | 2   | 1   | True        | cluster_1    |
| rocketship_communication-ism-000021  | 20  | ISM    | 234955         | 545.9mb    | 272.95mb   | 2   | 1   | True        | cluster_1    |
| rocketship_navigation-ism-000021     | 64  | ISM    | 8862623        | 13.2gb     | 6.6gb      | 2   | 1   | True        | cluster_1    |
| rocketship_propulsion-ism-000203     | 58  | ISM    | 2033895        | 420.8kb    | 210.4kb    | 2   | 1   | True        | cluster_1    |
| rocketship_telemetry-ism-000064      | 80  | ISM    | 683308950      | 14.8gb     | 7.4gb      | 2   | 1   | True        | cluster_1    |
+--------------------------------------+-----+--------+----------------+------------+------------+-----+-----+-------------+--------------+
```

## OPTIC as Library
OPTIC is also designed to be able to be used as a library by external.  OPTIC exposes various functions and classes 
(listed in the top level `__init__.py`) for developers to call externally.  The recommended way to call OPTIC functionality
is described below by example.

### Common Patterns
The recommended way to call OPTIC functionality from code is generally as follows:
* Define cluster information programmatically (see examples below)
* Specify desired cluster and cluster group names to act on in a list (this can be any subset of the ones defined above)
* Specify any specific cluster properties required for an action in a dictionary (these vary by query and are provided below)
* This information is provided to OPTIC by constructing a ClusterConfig object using the information above
* Call the desired action w/ the ClusterConfig object as an argument and use any returned data as desired

### get_cluster_info()
The sample code below queries cluster information from a selection of clusters and prints the results:
```python
import optic
import json

cluster_config = {
    "clusters": {
        "prod-lga": {
            "password": "*******",
            "url": "https://prod-lga.example.com:9200",
            "username": "oracle",
        },
        "prod-jfk": {
            "password": "*******",
            "url": "https://prod-jfk.example.com:9200",
            "username": "oracle",
        },
        "prod-sfo": {
            "password": "*******",
            "url": "https://prod-sfo.example.com:9200",
            "username": "oracle",
        },
        "stage-lga": {
            "password": "*******",
            "url": "https://stage-lga.example.com:9200",
            "username": "oracle",
        },
        "stage-jfk": {
            "password": "*******",
            "url": "https://stage-jfk.example.com:9200",
            "username": "oracle",
        },
        "stage-sfo": {
            "password": "*******",
            "url": "https://stage-sfo.example.com:9200",
            "username": "oracle",
        },
         "dev-lga": {
            "password": "*******",
            "url": "https://dev-lga.example.com:9200",
            "username": "oracle",
        },
        "dev-jfk": {
            "password": "*******",
            "url": "https://dev-jfk.example.com:9200",
            "username": "oracle",
        },
        "dev-sfo": {
            "password": "*******",
            "url": "https://dev-sfo.example.com:9200",
            "username": "oracle",
        },
    },
    "groups": {
        "prod": ["prod-lga", "prod-jfk", "prod-sfo"],
        "stage": ["stage-lga", "stage-jfk", "stage-sfo"],
        "dev": ["dev-lga", "dev-jfk", "dev-sfo"],
    },
}


cluster_selection = ["prod", "dev-sfo"]
selected_clusters = optic.get_selected_clusters(
    optic.ClusterConfig(cluster_config), cluster_selection
)
cluster_info = optic.get_cluster_info(selected_clusters)

print("CLUSTER INFORMATION")
print(json.dumps(cluster_info, indent=3))
```
### get_index_info()
Properties specific to `get_index_info` are:

    search_pattern - specify a glob search pattern for the query
    index_type_patterns - specify a dictionary with index_type_name -> regular_expression pairs

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

cluster_config = {
    "clusters": {
        "prod-lga": {
            "password": "*******",
            "url": "https://prod-lga.example.com:9200",
            "username": "oracle",
        },
        "prod-jfk": {
            "password": "*******",
            "url": "https://prod-jfk.example.com:9200",
            "username": "oracle",
        },
        "prod-sfo": {
            "password": "*******",
            "url": "https://prod-sfo.example.com:9200",
            "username": "oracle",
        },
        "stage-lga": {
            "password": "*******",
            "url": "https://stage-lga.example.com:9200",
            "username": "oracle",
        },
        "stage-jfk": {
            "password": "*******",
            "url": "https://stage-jfk.example.com:9200",
            "username": "oracle",
        },
        "stage-sfo": {
            "password": "*******",
            "url": "https://stage-sfo.example.com:9200",
            "username": "oracle",
        },
         "dev-lga": {
            "password": "*******",
            "url": "https://dev-lga.example.com:9200",
            "username": "oracle",
        },
        "dev-jfk": {
            "password": "*******",
            "url": "https://dev-jfk.example.com:9200",
            "username": "oracle",
        },
        "dev-sfo": {
            "password": "*******",
            "url": "https://dev-sfo.example.com:9200",
            "username": "oracle",
        },
    },
    "groups": {
        "prod": ["prod-lga", "prod-jfk", "prod-sfo"],
        "stage": ["stage-lga", "stage-jfk", "stage-sfo"],
        "dev": ["dev-lga", "dev-jfk", "dev-sfo"],
    },
}

cluster_selection = ["stage", "prod-jfk"]
selected_clusters = optic.get_selected_clusters(
    optic.ClusterConfig(cluster_config), cluster_selection
)

sort_by = ["age"]
filters = {'max_age': 10}
optic_settings = {
    'search_pattern': '*departure*',
    'index_type_patterns': {'ISM': '(.*)-ism-(\\d{6})$'}
}

for cluster in selected_clusters:
    optic.configure_cluster(cluster, optic_settings)

index_info = optic.get_index_info(selected_clusters, filters, sort_by)

print("INDEX INFORMATION")
print(json.dumps(index_info, indent=3))
```

### get_alias_info()
Properties specific to `get_alias_info` are:

    search_pattern - specify a glob search pattern for the query

The sample code below queries alias information from a selection of clusters and prints the results:
```python
import optic
import json

cluster = optic.Cluster(**{
    "name": "stage-jfk",
    "url": "https://stage-jfk.example.com:9200",
    "auth" : {"password": "*******", "username": "oracle"},
    "search_pattern": '*air*'
    }
)

alias_info = optic.get_alias_info([cluster])
print("ALIAS INFORMATION")
print(json.dumps(alias_info, indent=3))
```


## Contributing

This project welcomes contributions from the community. Before submitting a pull request, please [review our contribution guide](./CONTRIBUTING.md)


## Security

Please consult the [security guide](./SECURITY.md) for our responsible security vulnerability disclosure process

## License

Copyright (c) 2024-2025 Oracle and/or its affiliates.

Released under the Universal Permissive License v1.0 as shown at
<https://oss.oracle.com/licenses/upl/>.
