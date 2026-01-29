Quickstart
==========


Device Provisioning
-------------------

- Initial start of gateway + docker commands or link
- Device name will match hostname

.. code-block:: bash

    ./run_dockerized_gateway.sh #registers device with ThingsBoard and creates tb_access_token
    docker logs --tail 50 -f acropolis_edge_gateway