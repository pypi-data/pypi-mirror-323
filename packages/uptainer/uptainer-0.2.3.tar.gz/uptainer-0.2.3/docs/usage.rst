=====
Usage
=====

CLI Tool
--------

0. (OPTIONAL) Create and activate a Python virtual environment to isolate project dependencies from the system's global libraries.

.. code-block:: bash

    python3 -m venv .venv
    . ./.venv/bin/activate

1. Install the package using:

.. code-block:: bash

    pip install uptainer


2. Download the latest config sample from Github

.. code-block:: bash

    wget "https://raw.githubusercontent.com/asbarbati/uptainer/refs/heads/develop/config.sample.yaml"

3. Edit the config based your scenarios follow the :doc:`configuration guide <config>`.

4. Export the environment variable named "GITHUB_API_TOKEN" (:doc:`How to create the tokens </create_token>`)

.. code-block:: bash

    export GITHUB_API_TOKEN="ghp_...."

5. Run it using:

.. code-block:: bash

    uptainer --config-file <path of your config yml>

6. Verify the results on the logs.


Helm Chart
----------

0. Adding Helm repository

.. code-block:: bash

    helm repo add asbarbati-helm https://asbarbati.github.io/helm-charts/

1. Download the latest package using

.. code-block:: bash

    helm fetch asbarbati-helm/uptainer

2. De-compress the package

.. code-block:: bash

    tar xfz uptainer-<VERSION>.tgz

3. Create a secret with the SSH private key.

.. code-block:: bash

    kubectl create secret generic uptainer-sshkey --from-file=ssh-privatekey=/path/to/.ssh/id_rsa

4. Adding the reference in the values.yaml file like

.. code-block:: yaml

  - name: sshkey
    secret:
      secretName: uptainer-sshkey

5. Edit the values for your scenarios.

6. Install it

.. code-block:: bash

    helm install uptainer asbarbati-helm/uptainer -f values.yaml
