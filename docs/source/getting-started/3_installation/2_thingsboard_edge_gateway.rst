Thingsboard-edge-gateway Installation
=====================================
This guide details installation of the thingsboard-edge-gateway project on an IoT end-device. It assumes a thingsboard
server has been set up already and can be connected to via MQTT.

Install Dependencies
--------------------

Update the package list and install required dependencies:

.. code-block:: bash

    sudo apt update && sudo apt upgrade -y
    sudo apt install -y \
        build-essential libssl-dev libbz2-dev \
        libexpat1-dev liblzma-dev zlib1g-dev \
        libffi-dev openssl docker.io git \
        libsqlite3-dev wget

Python
------
.. code-block:: bash

    wget https://www.python.org/ftp/python/3.12.8/Python-3.12.8.tgz
    sudo tar zxf Python-3.12.8.tgz
    cd Python-3.12.8
    sudo ./configure --enable-optimizations --enable-loadable-sqlite-extensions
    sudo make -j 4
    sudo make install
    curl -sSL https://install.python-poetry.org/ | python3.12 -

Download Gateway
----------------

You can download the latest release of ThingsBoard Edge Gateway from the GitHub repository:

.. code-block:: bash

    cd /home/pi/
    mkdir gateway
    cd gateway
    git init
    git clone https://github.com/tum-esm/thingsboard-edge-gateway.git

Folder structure:
- ".env.template": Template for environment variable configuration - rename to ".env" and edit as needed


Download Controller
-------------------

.. code-block:: bash

    cd /home/pi/
    mkdir controller
    cd controller
    git init
    git clone <...>


