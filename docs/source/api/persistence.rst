Local Data Persistence
======================

This section documents the local persistence layer used by the Edge Gateway for
buffering, archiving, and recovery.

SQLite Abstraction
------------------

.. automodule:: modules.sqlite
   :members:
   :undoc-members: False

Database Schemas
----------------

Controller Archive
^^^^^^^^^^^^^^^^^^

.. automodule:: db_schemas.controller_archive_table
   :members:

Controller Messages
^^^^^^^^^^^^^^^^^^^

.. automodule:: db_schemas.controller_messages_table
   :members:

Pending Messages
^^^^^^^^^^^^^^^^

.. automodule:: db_schemas.pending_messages_table
   :members: