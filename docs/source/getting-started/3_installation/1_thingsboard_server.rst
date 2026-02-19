ThingsBoard server installation
===============================

This guide provides step-by-step instructions to set up a ThingsBoard server for the Acropolis project.

Prerequisites
-------------

- A server running Linux, e.g. Ubuntu 22.04 LTS

  - using a cloud hosting provider (e.g., DigitalOcean, AWS, Azure, GCP)

  - minimum specifications 1 vCPU (2 recommended), 2GB RAM

- Optional: A domain name pointing to the server's IP address

  - e.g., `subdomain.example.com`

  - choose from a paid domain name provider (e.g. namecheap.com) or use a subdomain of an existing domain (e.g. from within your institution)

  - point the domain's DNS A record to the server's IP address (`A <domain> <IP>`)

  - optional: create a trusted certificate for the domain using Let's Encrypt (e.g. using ``certbot certonly -d <domain>``) and add an automatic renewal cron job (e.g. ``0 0 * * * certbot renew --quiet``)

- Optional: Familiarize yourself with the `ThingsBoard documentation <https://thingsboard.io/docs/>`_.

Installation
------------

1. Optional: Update system packages and reboot

   .. code-block:: bash

      sudo apt update
      sudo apt upgrade -y
      sudo apt auto-remove -y
      sudo reboot

2. Optional: Set up a swapfile if your server has less than 2GB of RAM

   .. code-block:: bash

      sudo fallocate -l 4G /swapfile
      sudo chmod 600 /swapfile
      sudo mkswap /swapfile
      sudo swapon /swapfile
      echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

3. Install dependencies (``docker``, ``git``, ``jq``, ``curl``, ``ca-certificates``, ``nginx-full``, ``ufw``)

   .. code-block:: bash

      sudo apt install docker.io git jq curl ca-certificates nginx-full ufw

4. Install ``docker-compose`` (plugin)

   .. code-block:: bash

      # Add Docker's official GPG key:
      sudo apt update
      sudo apt install ca-certificates curl
      sudo install -m 0755 -d /etc/apt/keyrings
      sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
      sudo chmod a+r /etc/apt/keyrings/docker.asc
      # Add the repository to Apt sources:
      echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo \"$VERSION_CODENAME\") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
      # Install docker-compose
      sudo apt update
      sudo apt install docker-compose-plugin

5. Add your user to the ``docker`` group (log out/in afterwards)

   .. code-block:: bash

      sudo groupadd docker || true
      sudo usermod -aG docker $USER

6. Create data folders for ThingsBoard

   .. code-block:: bash

      mkdir -p ~/data/thingsboard_data/data
      mkdir -p ~/data/thingsboard_data/logs
      mkdir -p ~/data/kafka
      sudo chmod -R a+rw ~/data/

7. Generate a self-signed certificate for ThingsBoard SSL (skip if using a trusted certificate)

   - Run ``gen_certs.sh`` in a temporary directory on your local machine (script available in this repository under ``setup/ThingsBoard/gen_certs.sh``).

8. Copy files to the server

   - ``docker-compose.yml`` → ``~/docker-compose.yml``
   - ``self_signed_cert.crt`` → ``/etc/ssl/certs/self_signed_cert.crt``
   - ``self_signed_cert.key`` → ``/etc/ssl/certs/self_signed_cert.key``
   - ``nginx_thingsboard.conf`` → ``/etc/nginx/sites-available/thingsboard.conf``
   - ``nginx.conf`` → ``/etc/nginx/nginx.conf`` (overwrite existing file)

9. Remove default NGINX configuration

   .. code-block:: bash

      sudo rm /etc/nginx/sites-enabled/default

10. Set up firewall using ``ufw``

    .. code-block:: bash

       sudo ufw default deny incoming
       sudo ufw default allow outgoing
       sudo ufw allow ssh
       sudo ufw allow http
       sudo ufw allow https
       sudo ufw allow 8843
       sudo ufw enable

11. Reload NGINX and start Docker containers

    .. code-block:: bash

       sudo service nginx reload
       cd ~
       docker compose -f docker-compose.yml up -d

12. Watch live logs of ThingsBoard (initial startup takes several minutes)

    .. code-block:: bash

       docker logs -f thingsboard

    Wait until the following message appears:

    ``[main] INFO  o.t.s.ThingsboardServerApplication - Started ThingsBoard in x seconds``

13. Open the ThingsBoard web UI and log in with default credentials

    - Open ``<your-domain>`` in a web browser
    - Log in with:
      - username: ``sysadmin@thingsboard.org``
      - password: ``sysadmin``

14. Connect MQTT devices to ThingsBoard

    Use the following MQTT broker settings:

    - host: ``<your-domain>``
    - port: ``8843`` (SSL)
    - username: ``<access-token>`` (see below)

    See the `ThingsBoard MQTT API documentation <https://thingsboard.io/docs/reference/mqtt-api/>`_ for details.