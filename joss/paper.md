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

- Shared operational requirements across projects:
  - Reliable bidirectional communication with a central platform
  - Local buffering of data during network outages
  - Remote configuration and maintenance capabilities
  - Safe software updates without disrupting measurements
  - Ability to recover from failures without physical intervention

- Sensor networks differ mainly in:
  - sensor hardware
  - acquisition protocols
  - domain-specific processing
- Infrastructure needs are largely identical across projects
- A reusable architectural baseline reduces duplicated engineering effort

- The ThingsBoard Edge Gateway provides:
  - A stable and reusable gateway architecture
  - Clear separation between infrastructure and application logic
  - Persistent connectivity, buffering, and remote management
  - Supervision of an external, application-specific controller

- Research projects can:
  - Start from a proven gateway design
  - Implement only controller logic specific to their hardware
  - Reduce engineering overhead at project start
  - Deploy new sensor networks more rapidly

- Broader impact:
  - Architectural consistency across scientific projects
  - Improved long-term maintainability
  - Reuse beyond a single study or funding cycle
  - A documented reference architecture for sensor networks

# Design and Architecture

- Two-component architecture:
  - Edge Gateway (this software)
  - External Edge Controller (project-specific)
- Gateway responsibilities:
  - Connectivity to ThingsBoard
  - Persistence and buffering
  - Remote management and supervision
- Controller responsibilities:
  - Sensor hardware interaction
  - Data acquisition and processing
- Gateway runs as a long-lived Python process
- Controller runs in a Docker container
- Controller is not part of this repository
- Architecture supports continuous gateway availability during controller restarts and updates

# Functionality

- MQTT-based communication with ThingsBoard
- Local buffering of telemetry and logs
- Remote configuration via shared attributes
- Remote procedure calls for operational control
- Controller-only over-the-air (OTA) updates
- Rollback to previous controller versions
- Self-provisioning against ThingsBoard
- Graceful handling of network outages and controller failures

# Implementation

- Implemented in Python (version 3.12+)
- Modular code structure separating communication, persistence, and management
- SQLite used for lightweight local persistence
- Docker used for controller isolation
- Static type checking using mypy
- Documentation generated using Sphinx

# Mathematics

Footnote[^1]


# Citations

If you want to cite a software repository URL (e.g. something on GitHub without a preferred citation) then you can do it with the example BibTeX entry below for.

@IPCC_2021_WGI_SPM
[@IPCC_2021_WGI_SPM]

# Figures

Figures can be included like this:


# Author contributions

- Conceptual design of the gateway architecture
- Implementation of the Edge Gateway software
- Documentation and user guides
- Deployment and validation in a real-world sensor network
- Joint contribution to manuscript preparation

# Acknowledgements

- ICOS Cities framework
- Funding bodies (to be added)

# References

[^1]: https://thingsboard.io/