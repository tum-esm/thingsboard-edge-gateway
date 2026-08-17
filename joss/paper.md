---
title: 'TEGAT: A Lightweight and Reusable Gateway for Scientific Sensor Networks'
tags:
  - Gateway
  - ThingsBoard
  - IoT
  - Python
  - ACROPOLIS
  - MQTT
  - Sensor network
  - Sensor management
  - Real-time Measurement
  - Data persistence

authors:
  - name: Lars Frölich
    orcid: 0009-0000-1579-7727
    equal-contrib: true
    corresponding: false
    affiliation: 1
  - name: Patrick Aigner
    orcid: 0000-0002-1530-415X
    equal-contrib: true
    corresponding: true
    affiliation: 1
  - name: Jia Chen
    orcid: 0000-0002-6350-6610
    equal-contrib: false
    corresponding: true
    affiliation: 1
affiliations:
    - name: Environmental Sensing and Modeling, Technical University of Munich (TUM), Munich, Germany
      index: 1
date: 17 August 2026
bibliography: paper.bib
---

# Summary

TEGAT (Telemetry Edge Gateway) is a lightweight, general-purpose open source software built for managing and monitoring networks of IoT devices. 
It is built to integrate with the ThingsBoard platform and was designed specifically for operating distributed 
sensor networks for scientific research.
Originally developed for and validated in the ACROPOLIS urban CO2 sensor network, it is network-agnostic and can be used with a wide range of sensor hardware.
TEGAT offers a stable and reusable architectural baseline for distributed sensor networks, enabling users to 
focus on application-specific logic while relying on a field-tested software solution for communication, data 
persistence, and remote management of sensor devices.
It is designed to be robust against network and power outages, crashes, and other failures, thus reducing the risk of 
data loss, system downtime, or the need for physical intervention.
Application-specific and hardware interfacing logic is delegated to a user-provided Controller Software which is managed 
and deployed by TEGAT, thus separating infrastructure and application logic.

# Statement of need

Distributed sensor networks are a critical tool in scientific research and widely used across disciplines, enabling 
long-term, continuous sensor measurements. While they vary in the size and type of sensor hardware and data processing
protocols used, such networks often face common infrastructure challenges:
Physical access to sensor devices is often limited or costly, which can be exacerbated by challenges in 
scaling networks to large numbers of deployed sensors. Sensor networks often need to provide continuous
measurements while operating unattended for extended periods of time, all while network connectivity and system 
power can be intermittent or unreliable.
Although these challenges vary across deployments, they translate into a common set of infrastructure requirements:

- Reliable bidirectional communication
- Local buffering of data during network outages
- Remote configuration and maintenance capabilities
- Safe remotely initiated software updates
- Ability to recover from failures without physical intervention
- Seamless addition and removal of devices from the network

TEGAT addresses these infrastructure requirements to significantly reduce the engineering overhead associated 
with deploying and maintaining sensor networks. This enables network operators to focus on application-specific software instead. 
TEGAT leverages the ThingsBoard IoT platform [@ThingsBoard], a robust open source software, which was chosen for its 
maturity (10+yrs in development) and scalability.
The flexible design of TEGAT, combined with the ThingsBoard IoT platform, enables users to configure customized 
sensor networks, seamlessly integrate additional sensors into existing networks, as well as making it possible to reuse 
infrastructure across multiple research projects.

# State of the Field
Other existing solutions already cover a variety of the features provided by the combination of TEGAT and ThingsBoard,
though there are different tradeoffs and limitations to consider with each approach:
Some solutions are designed around an on-site centralized "edge" server which collects data from multiple connected 
sensor devices. Examples include thin-edge.io [@thin-edge] and ThingsBoard's own product ThingsBoard Edge [@thingsboard-edge]. 
These architectures benefit from sensor network layouts where many sensor devices share a local network, such as large 
factory or office buildings, but face limitations when sensors are deployed individually in remote locations.
Some subset of our features can be covered with commercial solutions: For example, Amazon's AWS IoT [@AWS-IoT] and Microsoft
Azure IoT Edge [@Azure-IoT-Edge] products are IoT cloud-platforms similar to ThingsBoard, and Balena Cloud [@BalenaCloud] offers reliable device 
management and software updates of IoT device fleets similar to TEGAT's OTA and RPC functionality. However, projects
building on top of such products are dependent on their future pricing and availability, and require
continuous funding.
Finally, a combination of open source solutions can offer a similar feature set: Examples are the Eclipse Foundation's Kura [@EF-kura] 
and Kapua [@EF-kapua] projects, as well as the Linux Foundation's Fledge [@fledge] and KubeEdge [@kubeedge] projects. In both cases, these unfortunately lack data visualization dashboards and software maturity. Finally, the Ivy project [@Makowski2025] doesn't separate application and infrastructure logic, making software updates brittle. For example, 
any crashes not covered by the test suite may result in permanent downtime requiring on-site fixes.

# Software Architecture

The software is based on a three-component architecture (see \autoref{fig:architecture}):

- (1) TEGAT (this software)
- (2) Controller Software (user provided)
- (3) ThingsBoard IoT Platform

Both TEGAT (1) and the Controller Software (2) are deployed on the same IoT sensor device, with TEGAT 
acting as intermediary between the Controller Software and the ThingsBoard platform which runs on a remote server. 
This design strictly separates the infrastructure and application logic, and divides responsibilities between all three components:
TEGAT (1) is designed to be lightweight and robust, performing only essential functions like forwarding telemetry 
to ThingsBoard and managing the deployment of the Controller Software. It communicates with the ThingsBoard platform via 
a secure MQTT [@MQTT-spec] connection.
The Controller Software (2) is provided by the user and is responsible for handling application-specific logic such as 
controlling actuators and collecting and processing sensor data. It is deployed inside a Docker [@merkel2014docker] container 
environment and communicates with TEGAT via an intermediary database.
Finally, the ThingsBoard platform (3) is deployed remotely and acts as a centralized data storage and network 
management system. It is built to be highly scalable, both in the number of connected devices and in
the amount of data received and stored. It is also highly customizable, supporting arbitrary sensor data formats and
protocols.
Decoupling TEGAT from the Controller Software ensures that corrective actions, such as 
reverting to a stable software version or adjusting configurations, can be performed remotely without risking system 
connectivity or requiring on-site intervention.
In case a newly deployed Controller Software version fails to start or contains errors, TEGAT remains operational
and continues to communicate with the ThingsBoard platform. 

![Software architecture for on-device (green) and off-premise (blue) components. Purple boxes show the three main architecture components TEGAT (1), Controller Software (2), and the ThingsBoard IoT Platform (3). Dashed boxes show local files. \label{fig:architecture}](figures/figure1.png)

## Software Design and Implementation
The TEGAT software is written in Python [@Python]. It follows a modular design, encapsulating independent
functionality such as logging, database access, or communication into separate software modules. During an 
initial setup phase, communication is established with the ThingsBoard platform using MQTT via TLS, and the device is 
provisioned in the ThingsBoard platform if needed. The software subsequently enters a steady-state main loop which 
performs one task per iteration, with higher priority tasks, such as processing incoming MQTT messages, executed first. 
This design ensures operational reliability and efficiency.
TEGAT receives telemetry data from the Controller Software via a local SQLite database [@SQLite], which is used to
buffer messages between the two software components for additional fault tolerance. TEGAT then forwards the 
telemetry data to the ThingsBoard platform via MQTT, and stores a copy of the data in a local database for additional 
redundancy (e.g. to backfill data gaps on-demand).
TEGAT also manages the deployment of the Controller Software through the host system's Docker daemon: If the Controller 
Software's Docker container is not running or has not provided a recent heartbeat, 
TEGAT attempts to start it using an exponential backoff strategy.
Besides managing the Controller Software and forwarding telemetry data, TEGAT provides the following core features: 

- (1) Remote procedure calls (RPC)
- (2) Over-the-air (OTA) updates of the Controller Software
- (3) Remote file management

RPCs (1) enable users to invoke one of several predefined commands on TEGAT, e.g. remotely rebooting the 
sensor device. This mechanism is primarily intended for operational control and diagnostics that must be executed 
on-demand without direct access to the device.
The OTA update feature (2) enables users to remotely deploy new versions of the Controller Software to the device, for
example to fix bugs or add new features. By the same mechanism, users can also easily downgrade the Controller Software
This feature leverages the Git [@git] version control system to manage the software
version history: Users can specify a specific commit hash or tag. TEGAT then builds a Docker image based on the 
corresponding source code.
TEGAT also provides a mechanism for directly creating, reading, and writing files on the sensor device using the remote file management feature (3). 
As Linux [@LinuxKernel] systems provide extensive access to operating system functionality through files, 
this feature has a particularly wide range of applications. 
Typical use cases are managing software configuration files for the Controller Software and configuring on-device drivers and 
system daemons.
More technical details can be found in the documentation[^1], which is built on Sphinx [@Sphinx].
To make TEGAT's source code more robust, its codebase is statically typed.
Developers can perform local type checks using mypy [@mypy], which is also deployed as a continuous integration pipeline using
GitHub Actions.
For integration testing, a demo application is provided which deploys a ThingsBoard server alongside TEGAT and an example implementation of the Controller Software. This example implementation also serves as a starting point for developers.


# Research impact statement

TEGAT has been validated in the ACROPOLIS urban CO2 sensor network [@ACROPOLIS2026] within the ICOS Cities project. ACROPOLIS-edge [@ACROPOLIS-edge] serves as an example of a successful deployment of TEGAT in a real world use case. During this deployment, it continuously ran over 18 months across 17 devices, transmitted over 100 million messages to ThingsBoard, deployed over 250 OTA updates across the network, and processed over 1000 triggers from remote procedure calls and remote file management operations. 


[^1]: https://tum-esm.github.io/TEGAT/user-guide/

# Author contributions

LF, PA, designed the software architecture, implemented the software, wrote documentation and user guides, deployed and validated the software as part of the ACROPOLIS sensor network, and wrote the manuscript. JC is the principal investigator and scientific lead of the ICOS Cities project in Munich. All authors reviewed the manuscript.

# Acknowledgements and funding

This work has been funded by: PAUL, Pilot Applications in Urban Landscapes – Towards integrated 
city observatories for greenhouse gases (ICOS Cities), funded by the European Union's Horizon 2020 Research and Innovation 
Programme (grant agreement no. 101037319). Furthermore, the work is partly supported by the Horizon Europe European Research 
Council (ERC) Consolidator Grant CoSense4Climate (grant no. 101089203, PI: Jia Chen).

# AI usage disclosure

Generative AI tools were used to assist with language refinement, formatting, and editorial support during manuscript preparation, and to aid documentation of the codebase and online materials. All AI-assisted outputs were reviewed and approved by the authors.

# References