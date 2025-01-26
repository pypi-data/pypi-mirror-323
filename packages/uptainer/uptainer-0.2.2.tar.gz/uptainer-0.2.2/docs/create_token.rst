Create Token
============

Github
------
Authentication with a GitHub token is required to access images hosted on GitHub Packages (ghcr.io).

1. Go to https://github.com/settings/tokens
2. Click on **Generate new token** -> **Generate new token (classic)**
3. Please provide a descriptive name in the **Note** field and a suitable **Expiration** according to your policies.
4. You need these scopes: **repo:public_repo** and **read:packages**
5. Click on **Generate Token**
6. Export it using:

.. code-block:: bash

    export GITHUB_API_TOKEN="ghp_...."


DockerHub
---------
DockerHub currently imposes a soft rate limit on API requests. If you anticipate exceeding this limit, you will need to generate and export a personal access token as outlined below.

1. Go to https://app.docker.com/settings/personal-access-tokens
2. Click on **Generate new Token**
3. Please provide a descriptive name in the **Access Token Description** field and a suitable **Expiration date** according to your policies.
4. Click on **Generate**
5. Export it using:

.. code-block:: bash

    export DOCKERHUB_API_TOKEN="dckr_pat_..."
