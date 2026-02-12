Controller Repository
=====================

describes how the controller repository is structured and how to extend it with new controllers.

- Is its own GitHub repository and not part of the gateway's main codebase.
- Is developed and maintained independently, with its own release cycle.
- Is deployed via the OTA mechanism, allowing for updates without modifying the gateway's core code.
- Runs within docker containers, ensuring isolation and ease of deployment.
- Communicates via SQLite database

Example Controller
------------------

demo/example_controller/

- Is available in the demo folder
- Comes with the modules:
    - db communication module
    - example sensor/actuactor base classes
    - minimal main loop implementation
    - dockerfile for containerization
    - example requirement file for dependencies
    - venv for development


How is the Controller Repository Linked to the Gateway?
-------------------------------------------------------

