# Hubitat Elevation Maker API Interface

[![Test](https://github.com/Jelloeater/hubitatcontrol/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/Jelloeater/hubitatcontrol/actions/workflows/test.yml)
[![CodeQL](https://github.com/Jelloeater/hubitatcontrol/actions/workflows/codeql.yml/badge.svg?branch=main)](https://github.com/Jelloeater/hubitatcontrol/actions/workflows/codeql.yml)
[![Libraries.io dependency status for latest release](https://img.shields.io/librariesio/release/pypi/hubitatcontrol)](https://libraries.io/pypi/hubitatcontrol)

[![hubitatcontrol](https://snyk.io/advisor/python/hubitatcontrol/badge.svg)](https://snyk.io/advisor/python/hubitatcontrol)
![PyPI - Status](https://img.shields.io/pypi/status/hubitatcontrol)
[![PyPI](https://img.shields.io/pypi/v/hubitatcontrol)](https://pypi.org/project/hubitatcontrol/)
[![GitHub](https://img.shields.io/github/license/jelloeater/hubitatcontrol)](https://github.com/Jelloeater/hubitatcontrol/blob/main/LICENSE)

## Intro

This guide assumes you own a **Hubitat Elevation** home automation controller.

If you are interested in purchasing one, you can purchase a unit from the manufactures website at [hubitat.com](https://hubitat.com/products) or from [Amazon.com](https://www.amazon.com/Hubitat-Elevation-Home-Automation-Hub/dp/B07D19VVTX/)

## Changes
See [CHANGELOG.md](CHANGELOG.md) for current changes

## Setup

To get the required API keys, you will need to log in to your Hubitat admin interface.

See [Maker API Documentation](https://docs2.hubitat.com/en/apps/maker-api) for how to add the `MakerAPI` application and to generate new API keys

If you are using the cloud API endpoint for access, you will ALSO need to include the Cloud API key when setting up a new Hub object.

## Install

```shell
pip install hubitatcontrol
```

**Or if you want a copy direct from source**

```shell
pip install git+https://github.com/Jelloeater/hubitatcontrol.git
```

## Usage

### API
**Local Example**

```python
import hubitatcontrol as hc

hub = hc.Hub(host='http://192.168.1.100', token='Maker_Token',
app_id='Maker_App_ID') # Get Hub object to auth and poll against

# If you have a cloud based maker API, you can include the cloud token
# hub = hc.get_hub(host='https://cloud.hubitat.com', token='Maker_Token',
#                  app_id='Maker_App_ID', cloud_token='Cloud_API_token')

TEST_DEVICE = '1RGB'

device = hc.GetSingleDevice(hub).name(TEST_DEVICE)

# Turn on all the switches (includes lights)
device.turn_on() # Send command to device
print(device.switch)

# Get temprature from all sensors
for i in hc.GetDevices(hub).TemperatureSensor():
    print(f"{i.name} - {i.temperature}")

```


### CLI Interface
- If you have all the needed API keys added to your .env file, all you need to do is add them to your keyring
- Once loaded into the keyring, you can run the CLI from anywhere on your system

```bash
hubitatcontrol --help
hubitatcontrol load-env-to-keyring
hubitatcontrol ls
```

```text
❯ hubitatcontrol

 Usage: hubitatcontrol [OPTIONS] COMMAND [ARGS]...

 Hubitat Control CLI Interface

╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --install-completion        [bash|zsh|fish|powershell|pwsh]  Install completion for the specified shell. │
│                                                              [default: None]                             │
│ --show-completion           [bash|zsh|fish|powershell|pwsh]  Show completion for the specified shell, to │
│                                                              copy it or customize the installation.      │
│                                                              [default: None]                             │
│ --help                                                       Show this message and exit.                 │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────────────╮
│ clear-keyring                      Clear Keyring passwords                                               │
│ level                              Turn on a device via it's Device ID                                   │
│ load-env-to-keyring                Load .env file at exec location to keyring                            │
│ ls                                 Prints current devices from system keyring                            │
│ off                                Turn on a device via it's Device ID                                   │
│ on                                 Turn on a device via it's Device ID                                   │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

 Version: 1.1.2   Project: https://github.com/Jelloeater/hubitatcontrol
```

## Docs

[Located in /docs folder](docs)

You will need a .dot file browser for the class diagrams

**WIP: Setup ReadTheDocs auto gen**

## Issues / Features
See:

https://github.com/Jelloeater/hubitatcontrol/issues

## Structure

**Class Model**

```mermaid
flowchart LR
Specific_Device --> Abstract_Device_Class --> Device--> Hub
```

## Development setup

Testing is done with PyTest, you will need to set up the correct env vars for your local (or cloud) Hubitat API
See `.env.example`

If you are using a local API endpoint, please leave `HUBITAT_CLOUD_ID` blank in the `.env` file.

**Setup**

Install Go-Task --> <https://taskfile.dev/installation/>

```shell
task setup
task
```
