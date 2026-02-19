# ThingsBoard Edge Gateway

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![mypy](https://github.com/tum-esm/thingsboard-edge-gateway/actions/workflows/test-gateway.yaml/badge.svg)](https://github.com/tum-esm/thingsboard-edge-gateway/actions)
[![Documentation](https://img.shields.io/badge/docs-online-brightgreen.svg)](https://tum-esm.github.io/thingsboard-edge-gateway/)
<!-- [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.11111.svg)](https://doi.org/10.5281/zenodo.11111) -->

## Overview

The **ThingsBoard Edge Gateway** is a lightweight runtime that connects locally
deployed edge controllers to a central [ThingsBoard](https://thingsboard.io/docs/) instance. It acts as a
reliable communication, management, and supervision layer between edge devices
and the cloud. 

The gateway is designed for unattended, long-term operation in constrained
environments. It is is typically deployed on a small Linux-based system
(e.g. a Raspberry Pi) and runs continuously as a
background service. It supports remote configuration, controller software updates,
and operational control without requiring physical access to the device.


## Features

- Resilient MQTT communication with automatic reconnection
- Offline buffering using local SQLite databases for resilience
- Remote configuration management for files and system settings
- Controller OTA updates with rollback support
- Remote Procedure Calls (RPCs) with a predefined command set
- Self-provisioning against ThingsBoard at first startup

## Architecture Overview

The ThingsBoard Edge Gateway follows a deliberately simple and robust architecture
that separates **infrastructure responsibilities** from **application logic**.

At a high level, the system consists of two cooperating components:

- **Edge Gateway**  
  A long-running Python process that maintains connectivity to ThingsBoard,
  handles communication, persistence, and remote management, and supervises the
  lifecycle of the controller. The gateway is designed to remain stable and
  continuously available, even during controller restarts or updates.

- **Edge Controller**  
  An application-specific component running in a Docker container. The controller
  implements domain logic such as sensor control or data processing and can be
  updated, restarted, or replaced independently of the gateway. The controller
  software is not included in this repository and originates from an external GitHub repository.

This separation ensures that operational capabilities such as telemetry buffering,
remote configuration, and recovery actions remain available at all times.

A more detailed description of the runtime behavior and interactions between these
components is available in the documentation:

- [Remote File Management](https://tum-esm.github.io/thingsboard-edge-gateway/user-guide/remote-file-management)
- [Remote Software Updates](https://tum-esm.github.io/thingsboard-edge-gateway/user-guide/remote-software-update)
- [Remote Procedure Calls](https://tum-esm.github.io/thingsboard-edge-gateway/user-guide/remote-procedure-calls)


## Development and Type Checking

Setup and installation are described in the
[Installation Guide](https://tum-esm.github.io/thingsboard-edge-gateway/getting-started).  
The following steps are intended for local development.

Install development dependencies:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -r dev-requirements.txt
```

Run static type checks:

```bash
bash scripts/run_mypy.sh
```


## Context and Origin

The ThingsBoard Edge Gateway was originally developed as part of the
[**ACROPOLIS** CO₂ sensor network](https://amt.copernicus.org/articles/19/745/2026/) within the ICOS Cities framework. It is used
as the communication and management layer for the
[ACROPOLIS-edge](https://github.com/tum-esm/ACROPOLIS-edge) controller software
and the associated urban measurement network.

Although the gateway was designed and validated in the context of ACROPOLIS,
it is implemented as a standalone and reusable component suitable for any sensor network.


## Development Team

- Patrick Aigner [@patrickjaigner](https://github.com/patrickjaigner)
- Lars Frölich [@larsfroelich](https://github.com/larsfroelich)