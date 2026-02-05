MQTT Communication
==================

This section covers all communication with ThingsBoard via MQTT, including
telemetry, attributes, and inbound message routing.

MQTT Client
-----------

.. automodule:: modules.mqtt
   :members:
   :undoc-members: False

Message Handlers
----------------

The following modules process inbound MQTT messages and dispatch them to the
appropriate subsystems.

File Definition Update
^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: on_mqtt_msg.check_for_files_definition_update
   :members:
   :no-index:

File Hashes Update
^^^^^^^^^^^^^^^^^^

.. automodule:: on_mqtt_msg.check_for_file_hashes_update
   :members:
   :no-index:

File Content Update
^^^^^^^^^^^^^^^^^^^

.. automodule:: on_mqtt_msg.check_for_file_content_update
   :members:
   :no-index:

OTA Update Check
^^^^^^^^^^^^^^^^

.. automodule:: on_mqtt_msg.check_for_ota_updates
   :members:
   :no-index: