---
title: 'Fancy Title of the Paper'
tags:
  - Gateway
  - Thingsboard
  - IoT
  - Python
  - ACROPOLIS
authors:
  - name: Lars Frölich
    orcid: 0009-0000-1579-7727
    equal-contrib: true
    corresponding: true
    affiliation: 1
  - name: Patrick Aigner
    orcid: 0000-0002-1530-415X
    equal-contrib: true
    corresponding: true
    affiliation: 1
affiliations:
    - name: Environmental Sensing and Modeling, Technical University of Munich (TUM), Munich, Germany
      index: 1
date: 06 February 2026
bibliography: paper.bib
---

# Summary

- Introduce the ThingsBoard Edge Gateway as reusable research software
- Describe it as a lightweight gateway for scientific sensor networks
- Emphasize separation of infrastructure and application logic
- Highlight controller-agnostic design and reuse across projects
- Reference validation in a real-world scientific deployment

# Statement of need

- Scientific sensor networks are widely used across disciplines
- Typical use cases include long-term, continuous measurements
- Deployments often operate unattended for months or years
- Physical access to devices is limited or costly
- Network connectivity can be intermittent or unreliable

- Sensor networks differ mainly in:
  - sensor hardware
  - acquisition protocols
  - domain-specific processing
- Infrastructure needs are largely identical across projects
  - Reliable bidirectional communication with a central platform
  - Local buffering of data during network outages
  - Remote configuration and maintenance capabilities
  - Safe software updates without disrupting measurements
  - Ability to recover from failures without physical intervention
- A reusable architectural baseline reduces duplicated engineering effort

- Research projects can:
  - Start from a proven gateway design
  - Implement only controller logic specific to their hardware
  - Reduce engineering overhead at project start
  - Deploy new sensor networks more rapidly

- The ThingsBoard Edge Gateway provides:
  - A stable and reusable gateway architecture
  - Clear separation between infrastructure and application logic
  - Persistent connectivity, buffering, and remote management
  - Supervision of an external, application-specific controller

- Broader impact:
  - Architectural consistency across scientific projects
  - Reuse beyond a single study or funding cycle

# State of the Field

Main difference to others. We integrate the gateway in the edge device. This allows to deploy single devices at different locations without the need of a on location mist/fog gateway.

Open Source:
Local Gateways:
- Thingsboard Edge (local gateway, on location server): https://github.com/thingsboard/thingsboard-edge
- Thin Edge (split edge gateway and light on device): https://thin-edge.io/

Similar architectures:
- (On Device, Java Virtual Machine) Eclipse Kura: https://www.eclipse.org/kura/
- Ivy: https://joss.theoj.org/papers/10.21105/joss.08862
- IoT Fledge (north, south stack, no OTA): https://github.com/fledge-iot/fledge

Commercial:
- AWS IoT Greengrass (full stack, closed source): https://aws.amazon.com/greengrass/
- Azure IoT Edge (gateway mist): https://azure.microsoft.com/en-us/services/iot-edge/

Alternatives to Thingsboard:
- Kube Edge (remote sw management): https://kubeedge.io/en/
- Belena (Device OS + backend stack): https://www.balena.io/
- Tenta: https://joss.theoj.org/papers/10.21105/joss.07311


# Software Design

- Two-component architecture:
  - Edge Gateway (this software)
  - External Edge Controller (project-specific, we provide an example implementation)
- Good Scaling properties:
  - Multiple controllers can be supervised by a single gateway
  - Controllers can be added or removed from the network as needed 
- Gateway functionality:
  - MQTT-based communication with ThingsBoard
  - Local buffering of telemetry and logs
  - Remote configuration via shared attributes
  - Remote procedure calls for operational control
  - Controller-only over-the-air (OTA) updates
  - Rollback to previous controller versions
  - Self-provisioning against ThingsBoard
  - Graceful handling of network outages and controller failures
- Controller responsibilities:
  - Sensor hardware interaction
  - Data acquisition and processing
- Gateway runs as a long-lived Python process within a Docker container
- Controller is managed as a Docker container
- Architecture supports continuous gateway availability during controller restarts and updates

## Implementation

- Implemented in Python (version 3.12+)
- Modular code structure separating communication, persistence, and management
- SQLite used for lightweight local persistence
- Docker used for controller isolation
- Static type checking using mypy
- Documentation generated using Sphinx

# Research impact statement

- The ThingsBoard Edge Gateway has been validated in a real-world scientific deployment within the ICOS Cities framework. It has enabled reliable data collection from a network of environmental sensors in an urban setting @ACROPOLIS2026.
- Example implementation @ACROPOLIS-edge


# Citations

- ThingsBoard[^1] @ThingsBoard2026 
- Docker @merkel2014docker
- Python @Python
- SQLite @SQLite
- Mypy @mypy
- Sphinx @Sphinx
- Paho MQTT Client @paho

[^1]: https://thingsboard.io/


# Author contributions

- Conceptual design of the gateway architecture
- Implementation of the Edge Gateway software
- Documentation and user guides
- Deployment and validation in a real-world sensor network
- Joint contribution to manuscript preparation

# Acknowledgements

- ICOS Cities framework
- Funding bodies (to be added)

# AI usage disclosure

Generative AI tools were used to assist with language refinement, formatting, and editorial support during manuscript preparation, and to generate docstrings and aid documentation of the codebase and online materials. All AI-assisted outputs were reviewed and approved by the authors to ensure accuracy, technical correctness, and integrity.
