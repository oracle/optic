# OPTIC (Opensearch Tools for Indices and Cluster)

This project contains utilities for OpenSearch Engineers to troubleshoot and make changes to OpenSearch clusters

## Contents

- cluster_info:  Tool displaying key information (Health Status, Storage Percentage) about clusters
- index_info:  Tool displaying key information (Name, Age, Document Count, Index Size, etc.) about indices

## Requirements
Python **>3.12** is <mark>required</mark> to run the ```OPTIC``` toolset.

Python package manager pip **>21.3** is <mark>required</mark>

A properly formatted cluster configuration file is <mark>required</mark>

A properly formatted settings file is <mark>required</mark>


### To check if Python 3 is installed, follow these steps:

* Open the Terminal app (Mac) or a command line tool such as the Windows Cmmand Prompt (Windows):
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



If you see an error message, you can install Python using the official Python website https://www.python.org/downloads/

### To check if pip is up to date:
* Enter the following in the command line:
  ```
  pip -V
  ```

* Depending on your system, you may have to enter:
  ```
  python3 -m pip -V
  ```
If pip is not installed correctly, it can be installed using the official instructions
https://pip.pypa.io/en/stable/installation/

### Cluster Configuration File Setup
* A properly formatted cluster configuration file is necessary to use the OPTIC toolset.
* The default path for this configuration file is ```~/.optic/cluster-config.yaml``` (Can be defined in settings)
* A custom configuration file path can be specified in the settings file or using the Command Line Interface (detailed later in this README)
* #### The Configuration File allows users to easily store networking and authentication information for communicating with their OpenSearch Clusters.
* #### It also allows users to collect clusters into custom groups that can simplify cluster information gathering and administration
* #### A sample configuration file is provided below:
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
### Settings File Setup
* A properly formatted settings file is necessary to use the OPTIC toolset.
* The default path for this configuration file is ```~/.optic/optic-settings.yaml```
* A custom settings file path can be specified using the Command Line Interface (detailed later in this README)
* #### The Settings File allows users to easily preferences for their OPTIC tools.
* #### A sample settings file is provided below:
```yaml
default_cluster_config_file_path: '~/.optic/cluster-config.yaml'

default_cluster_info_byte_type: 'gb'

default_index_search_pattern: '*'
default_index_type_patterns:
  ISM: '(.*)-ism-(\d{6})$'
  ISM_MALFORMED: '(.*)-ism$'
  SYSTEM: '(^\..*)$'

```
* It is recommended to put all settings string values in single quotes to prevent escape characters from causing unintended behavior

## Installation

## Use
To use the OPTIC Command Line Interface, use the following format
```
optic <tool_name> <command_line_options>
```
For a full list of OPTIC tools, enter:
```
optic --help
```
To initialize OPTIC with an alternate settings file path, enter:
```
optic --settings-path <custom_file_path> <tool_name>
```
For a full list of the command line options available for each tool, enter:
```
optic <tool_name> --help
```