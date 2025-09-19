Copyright (c) 2024-2025, Oracle and/or its affiliates. All rights reserved.

# OPTIC CHANGELOG

All notable changes to the OPTIC project will be documented in
this file. This project adheres to [Semantic Versioning](http://semver.org/).

# 2.0.0
* refactor:! 💥 rename CLI options to better align with functionality
* feat: 🚸 cli defaults now show settings defined in optic-settings.yaml
* feat: 🚸 optic init now allows for specifying custom destination for created configuration files
* fix: 🗑️ remove CLI options that were not intended for CLI interface
  * storage_percent_thresholds
  * index_type_patterns
* refactor: 🚸 rename Cluster attribute `creds` to `auth`
* refactor: 🏗️ Cluster objects are updated with all optic-settings, instead of only cli options
  * enables additional configuration options in optic-settings.yaml that are not part of cli
* refactor: 🏗️ get_cluster_info, get_index_info, get_alias_info now use Cluster object as argument instead of ClusterConfig
* refactor: 🧑‍💻 shorten Cluster object custom_name attribute to name
* refactor: 🧑‍💻 Settings class renamed to OpticSettings to align with filename and ClusterConfig class name 
* refactor: 🧑‍💻 index_type_dict attribute in IndexInfo object renamed to index_type_patterns to match configuration setting


# 1.5.1
* chore: 🔧 updated metadata to include all changes from 1.5.0 🤦🏼‍♂️ 

# 1.5.0
* feat: 🥅 add retry logic to OpenSearch API calls 
* fix: 🩹 moved API call notification messages to correctly report order of actions
* test: ✅ successful request, retry until success, and retry exhaustion tests created
* fix: 🩹 None is no longer supported as default for password

# 1.4.6
* docs: 📝 add quick start section

# 1.4.5
* docs: 📝 update usage examples

# 1.4.4
* chore: ⬆️ update requests dependency

# 1.4.3
* chore: ⬆️ update urllib3 dependency

# 1.4.2
* docs: ✏️ update project URLs on pyproject.toml

# 1.4.1
* docs: 📝 update installation instructions

# 1.4.0
* refactor: ♻️ move optic init logic to initialize_service.py

# 1.3.0
* fix: ✅ add tests for cli commands

# 1.2.1
* fix: 🩹do not output report header for empty cluster list

# 1.2.0
* chore: 👷 update code quality action
* chore: 🔥 remove version validation single action
* fix: 💚 update version validation action
* feat: 👷‍♂️ add version validation action
* fix: 🚚 rename job long description
* feat: 👷‍♂️ add code quality check action
* chore: 🙈 updated gitignore

# 1.1.1
* feat: 🎉 initial release
