# ACROPOLIS CO<sub>2</sub> Sensor Network

This repository contains the software and hardware blueprints for the measurement systems deployed at the edge of the **ACROPOLIS** (Autonomous and Calibrated Roof-top Observatory for MetroPOLItan Sensing) CO<sub>2</sub> sensor network. This initial network consists of twenty prototype systems evenly distributed across the city of Munich. The project is part of [**ICOS Cities**](https://www.icos-cp.eu/projects/icos-cities), funded by the European Union's Horizon 2020 Research and Innovation Programme under grant agreement No. **101037319**.

<br/>

## Key Features

- **Non-Expert Setup**: The software is designed for easy deployment, requiring minimal technical expertise for setup and operation.
- **Scalability**: The network infrastructure allows for seamless scaling, enabling easy expansion to a larger number of devices and locations.
- **Remote Software and Configuration Update**: Supports remote updates for software and configuration, ensuring continuous improvement and easy deployment of changes.
- **Offline Data Backup**: SQLite implementation serves as a local backup for measurement data.
- **ThingsBoard Integration**: All measurements are transmitted via MQTT to a hosted ThingsBoard instance for centralized data collection and analysis.

<br/>

## Software Components

- **Edge Controller**: An autonumous software managing sensors and actors and running within a Docker container for isolated and consistent deployment.
- **Edge Gateway**: A standalone process managing the active edge controller container version, implementing a MQTT client to act as a communication gateway, and acting as the endpoint for remote commands.

<br/>

## Repository Overview

- Docs
- Setup
- Software

<br/>

## System Overview

Each edge system is managed by a Raspberry Pi 4, utilizing an LTE hat (NB-IoT) for internet connectivity. The primary sensor is the Vaisala GMP343 CO<sub>2</sub> sensor, accompanied by auxiliary BME280 and SHT45 sensors for environmental monitoring. Airflow is regulated by a brushless membrane pump and 2/2 valves, which switch between the sampling head and calibration tanks. Additionally, a Vaisala WXT-532 wind sensor is co-located with the sampling head to monitor wind conditions. The system includes a UPS and battery backup to ensure uninterrupted operation.

<br/>

## Software Architecture

<img src="docs/pictures/ACROPOLIS-Architecture-8.svg">

<br/>

## Related Work

Aigner et. al.: Advancing Urban Greenhouse Gas Monitoring: Development and Evaluation of a High-Density CO2 Sensor Network in Munich. ICOS Science Conference 2024, Versailles, France, 10.-12. Sept, [Link](https://www.icos-cp.eu/news-and-events/science-conference/icos2024sc/all-abstracts)

<br/>

## Current Development Team:

- Patrick Aigner [@patrickjaigner](https://github.com/patrickjaigner)
- Lars Frölich [@larsfroelich](https://github.com/larsfroelich)

<br/>

## Past Development Team Members:

- Felix Böhm [@empicano](https://github.com/empicano)
- Moritz Makowski [@dostuffthatmatters](https://github.com/dostuffthatmatters)
- Adrian Schmitt
