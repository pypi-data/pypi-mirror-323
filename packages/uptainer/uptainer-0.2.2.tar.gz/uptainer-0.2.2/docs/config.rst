Configuration file
==================
The configuration file is in YAML format and includes several default settings. A comprehensive list of available options is provided below.

**PLEASE NOTE**: that all keys listed below represent an object nested under the **repos** key.

+-------------------------+-----------+-------------------+---------------------------------------------------------------------------------------------------+
| Key                     | Mandatory | Default           | Description                                                                                       |
+=========================+===========+===================+===================================================================================================+
| **name**                | True      |                   | An arbitrary name that you can use to trace all requests associated with that object in the logs. |
+-------------------------+-----------+-------------------+---------------------------------------------------------------------------------------------------+
| **image_repository**    | True      |                   | The remote container registry to be check.                                                        |
+-------------------------+-----------+-------------------+---------------------------------------------------------------------------------------------------+
| **git_ssh_url**         | True      |                   | The remote SSH GIT URL to use for pull and push data                                              |
+-------------------------+-----------+-------------------+---------------------------------------------------------------------------------------------------+
| **git_ssh_privatekey**  | False     | $HOME/.ssh/id_rsa | The ssh key to use for pull and push data.                                                        |
+-------------------------+-----------+-------------------+---------------------------------------------------------------------------------------------------+
| **git_branch**          | False     | main              | The git branch to use.                                                                            |
+-------------------------+-----------+-------------------+---------------------------------------------------------------------------------------------------+
| **git_values_filename** | True      |                   | The yaml file to modfy into the git repository.                                                   |
+-------------------------+-----------+-------------------+---------------------------------------------------------------------------------------------------+
| **values_key**          | True      |                   | The yaml key, in dot format, to update with the new version detected, something like 'image.tag'  |
+-------------------------+-----------+-------------------+---------------------------------------------------------------------------------------------------+
| **version_match**       | True      |                   | The regex used for allowed version to upgrade. It use 're.match' library in Python.               |
+-------------------------+-----------+-------------------+---------------------------------------------------------------------------------------------------+

The results its something like

.. code-block:: yaml

    repos:
    - name: My super project
      image_repository: ghcr.io/immich-app/immich-server
      git_ssh_url: git@gitlab.example:main/mysuperproject.git
      git_ssh_privatekey: /home/username/.ssh/foobar
      git_branch: main
      git_values_filename: values.yaml
      values_key: image.tag
      version_match: v1.[0-9]+.[0-9]+
    - name: My Other super project
      image_repository: ghcr.io/immich-app/immich-server
      git_ssh_url: git@gitlab.example:main/foobaz.git
      git_ssh_privatekey: /home/username/.ssh/foobar
      git_branch: main
      git_values_filename: values.yaml
      values_key: image.tag
      version_match: v0.[0-9]+.[0-9]+
