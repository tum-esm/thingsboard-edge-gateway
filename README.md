# Telemetry Edge Gateway (TEGAT)

![GitHub Release](https://img.shields.io/github/v/release/tum-esm/tegat?display_name=tag)
![GitHub Pre-Release](https://img.shields.io/github/v/release/tum-esm/tegat?include_prereleases&display_name=tag&logo=pre-release&label=pre-release)
[![DOI](https://img.shields.io/badge/DOI-10.5281/zenodo.20432416-blue)](https://doi.org/10.5281/zenodo.20432416)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPLv3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![mypy](https://github.com/tum-esm/tegat/actions/workflows/test-gateway.yaml/badge.svg)](https://github.com/tum-esm/tegat/actions)
[![Documentation](https://img.shields.io/badge/docs-online-brightgreen.svg)](https://tum-esm.github.io/TEGAT/)
<!-- [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.11111.svg)](https://doi.org/10.5281/zenodo.11111) -->

## Overview

**TEGAT** is a lightweight runtime that connects IoT devices to a central [ThingsBoard](https://thingsboard.io/docs/) server.
It acts as a reliable communication, management, and supervision layer between the IoT device and the cloud. 

The gateway is designed for unattended, long-term operation in constrained
environments. It is typically deployed on a small Linux-based system
(e.g. a Raspberry Pi) and runs continuously (typically inside a docker container). 
It enables remote configuration, software updates, and operational control without requiring physical access to the device.

## Features

- Resilient MQTT-based communication with ThingsBoard with automatic reconnection
- Tiered local buffering of telemetry, logs, and historical data using local SQLite databases for resilience
- Server-authoritative remote file management and mirroring
- OTA software updates with rollback support
- Remote procedure calls for operational control
- Self-provisioning against ThingsBoard at first startup
- Automated health monitoring and diagnostic telemetry
- Graceful handling of network outages and controller failures

## Architecture Overview

TEGAT follows a deliberately simple and robust architecture
that separates **infrastructure responsibilities** from **application logic**.

At a high level, the system consists of two cooperating components:

- **TEGAT (this project)**  
  A long-running Python process that maintains connectivity to ThingsBoard,
  handles communication, persistence, and remote management, and supervises the
  lifecycle of the controller. TEGAT is designed to remain stable and
  continuously available, even during controller restarts or software updates.

- **Controller Software**  
  An application-specific component running in a Docker container. The controller
  implements domain logic such as sensor control or data processing and can be
  updated, restarted, or replaced independently of the gateway. The controller
  software is not included in this repository and originates from an external GitHub repository.

This separation ensures that operational capabilities such as telemetry buffering,
remote configuration, and recovery actions remain available at all times, independently of the controller software.

A more detailed description of the runtime behavior and interactions between these
components is available in the documentation:

- [Remote File Management](https://tum-esm.github.io/TEGAT/user-guide/remote-file-management)
- [Remote Software Updates](https://tum-esm.github.io/TEGAT/user-guide/remote-software-update)
- [Remote Procedure Calls](https://tum-esm.github.io/TEGAT/user-guide/remote-procedure-calls)


## Quick Start

To quickly get started with a locally running DEMO application of TEGAT for testing purposes, follow the instructions
in the "demo"-section of the docs [here](https://tum-esm.github.io/TEGAT/getting-started/2_demo.html).


## Development and Type Checking

Production-level setup and installation steps are described in the
[Installation Guide](https://tum-esm.github.io/TEGAT/getting-started/0_index.html#).  
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

TEGAT ( _Telemetry Edge GATeway_ ) was originally developed as part of the
[**ACROPOLIS** CO₂ sensor network](https://amt.copernicus.org/articles/19/745/2026/) within the ICOS Cities framework. 
It is used as the communication and management layer for the
[ACROPOLIS-edge](https://github.com/tum-esm/ACROPOLIS-edge) controller software and the associated urban measurement network.

Although the gateway was designed and validated in the context of ACROPOLIS,
it is implemented as a standalone and reusable component suitable for any sensor network.


## Development Team

- Patrick Aigner [@patrickjaigner](https://github.com/patrickjaigner)
- Lars Frölich [@larsfroelich](https://github.com/larsfroelich)

## License

This project, with the notable exception of all files contained in the "demo" folder, is licensed under the AGPL-3.0 
[LICENSE](LICENSE).
