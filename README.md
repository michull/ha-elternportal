# Integration for Eltern-Portal

![Project Maintenance][maintenance-shield]
[![GitHub Release][releases-shield]][releases-link]
[![GitHub Activity][commits-shield]][commits-link]
[![License][license-shield]](LICENSE)

Unofficial integration for eltern-portal.org (by [art soft and more GmbH](https://artsoftandmore.com/))


**This integration will set up the sensor platform.**

Sensor name                               | Description
:---------------------------------------- | :------------------------------
`sensor.elternportal_name`                | Provide data from Eltern-Portal
`sensor.elternportal_name_elternbrief`    | Parent letters
`sensor.elternportal_name_fundsachen`     | Lost and found [planned]
`sensor.elternportal_name_klassenbuch`    | Class book (homework)
`sensor.elternportal_name_stundenplan`    | Timetable [planned]
`sensor.elternportal_name_termin`         | School calendar (school test)
`sensor.elternportal_name_schwarzesbrett` | Bulletin board [planned]


# Setup

## Installation via HACS

To add this integration, you can use this My button:

[![Open HACS repository on my HA](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=michull&repository=ha-elternportal&category=integration)

or do the following steps:

1. Ensure that HACS is installed
1. Open HACS
1. Click on the 3 dots in the top right corner.
1. Select "Custom repositories"
1. Set the repository to `michull/ha-elternportal`.
1. Select the type `integration`
1. Click the `ADD` button.
1. Search for and install the "elternportal" integration
1. **Restart Home Assistant**


## Manual installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
1. If you do not have a `custom_components` directory (folder) there, you need to create it.
1. In the `custom_components` directory (folder) create a new folder called `elternportal`.
1. Download _all_ the files from the `custom_components/elternportal/` directory (folder) in this repository.
1. Place the files you downloaded in the new directory (folder) you created.
1. **Restart Home Assistant**

## Configuration is done in the UI

After the restart, to add a school via the UI, you can use this My button:

[![Add integration to my HA](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=elternportal)

or do the following steps:

1. After the restart, in the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Elternportal"
1. Follow the configuration flow.

    Field name | Content
    :--------- | :------------------------------
    `school`   | School identifier (prefix of the official url: ________.eltern-portal.org)
    `username` | E-mail address of your account
    `password` | Password of your account

Note: please have a look at the [list of instances](INSTANCES.md)

[commits-link]: https://github.com/michull/ha-elternportal/commits/main
[commits-shield]: https://img.shields.io/github/commit-activity/y/michull/ha-elternportal.svg?style=for-the-badge
[elternportal]: https://www.eltern-portal.org
[license-shield]: https://img.shields.io/github/license/michull/ha-elternportal?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40michull-blue.svg?style=for-the-badge
[releases-link]: https://github.com/michull/ha-elternportal/releases
[releases-shield]: https://img.shields.io/github/release/michull/ha-elternportal.svg?style=for-the-badge&include_prereleases

