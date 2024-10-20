# Integration for Eltern-Portal

![Project Maintenance][maintenance-shield]
[![GitHub Release][releases-shield]][releases-link]
[![GitHub Activity][commits-shield]][commits-link]
[![License][license-shield]](LICENSE)
[![Hassfest][hassfest-shield]][hassfest-link]
[![HACS][hacs-shield]][hacs-link]

Unofficial integration for eltern-portal.org


**This integration will set up the calendar and sensor platform.**

Platform | Sensor name                             | Description
:------- | :-------------------------------------- | :----------------------------------
Sensor   | `sensor.elternportal_base_id`           | Provide all data from Eltern-Portal
Calendar | `calendar.elternportal_appointments_id` | Calendar appointments (optional)
Calendar | `calendar.elternportal_registers_id`    | Calendar class register (optional)
Sensor   | `sensor.elternportal_register_id`       | Sensor Class register (optional)


# Setup

## Installation via HACS

To add this integration, you can use this My button:

[![Open HACS repository on my HA](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=michull&repository=ha-elternportal&category=integration)

or do the following steps:

1. Ensure you have [HACS](https://hacs.xyz/) installed in your Home Assistant instance.
1. In the HACS panel, click on "Integrations".
1. Click on the 3 dots in the top right corner.
1. Select "Custom repositories".
1. Set the repository to `michull/ha-elternportal`.
1. Set the type to `integration`
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

## Configuration is done via the user interface

After the restart, to add a school via the UI, you can use this My button:

[![Add integration to my HA](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=elternportal)

or do the following steps:

In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "elternportal" and follow the configuration flow:

### Page: Configuration

Field name       | Content
:--------------- | :------------------------------
`School code`    | School identifier (subdomain part of the official url: _____.eltern-portal.org)
`E-mail address` | E-mail address of your account
`Password`       | Password of your account

### Page: Option

Field name     | Section | Default | Description
:--------------| :------ | :------ | :----------
`Appointments` | Service | [ ]     | Schoolwork and other appointments
`Lessons`      | Service | [ ]     | Time table
`Letters`      | News    | [x]     | Letters to parents
`Polls`        | News    | [ ]     | 
`Registers`    | Service | [ ]     | Homework tasks
`Sick notes`   | Notes   | [ ]     | 

### Page: Option for appointments

Field name                    | Default | Content
:---------------------------- | :-----: | :------------------------------------
`Calendar for appointments`   |   [ ]   | Create an additional calendar?

### Page: Option for class registers

Field name                    | Default | Content
:---------------------------- | :-----: | :------------------------------------
`Start (min)`                 |    -6   | First date for the field start
`Start (max)`                 |    +2   | Last date for the field start
`Calendar for class register` |   [ ]   | Create an additional calendar?
`Sensor for class register`   |   [ ]   | Create an additional sensor?
`Completion (treshold)`       |    +1   | Treshold day on the field completion

With the default values the following rule apply:
1. Only entries with a start date greater or equal to the date 6 days before today are retrieved from Eltern-Portal.
2. Only entries with a start date less or equal to the date 2 days after today are retrieved from Eltern-Portal.
3. Only entries with a completion date greater or equal to tomorrow are shown in the additional sensor for register.


# Dashboard

The data of the sensor can be displayed on a dashboard with the help of markdown cards. See some examples [here](DASHBOARD.md).


# Legal Notice

This integration is not built, maintained, provided or associated with [art soft and more GmbH](https://artsoftandmore.com/) in any way.


[commits-link]: https://github.com/michull/ha-elternportal/commits/main
[commits-shield]: https://img.shields.io/github/commit-activity/y/michull/ha-elternportal.svg?style=for-the-badge

[license-shield]: https://img.shields.io/github/license/michull/ha-elternportal?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40michull-blue.svg?style=for-the-badge

[releases-link]: https://github.com/michull/ha-elternportal/releases
[releases-shield]: https://img.shields.io/github/release/michull/ha-elternportal.svg?style=for-the-badge&include_prereleases

[hassfest-link]: https://github.com/michull/ha-elternportal/actions/workflows/hassfest.yaml
[hassfest-shield]: https://img.shields.io/github/actions/workflow/status/michull/ha-elternportal/hassfest.yaml?style=for-the-badge

[hacs-link]: https://github.com/michull/ha-elternportal/actions/workflows/hacs.yaml
[hacs-shield]: https://img.shields.io/github/actions/workflow/status/michull/ha-elternportal/hacs.yaml?style=for-the-badge



