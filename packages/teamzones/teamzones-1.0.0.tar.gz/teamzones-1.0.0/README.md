# Teamzones

Given a set of time zones and a time, print the time in different timezones.

## Usage

```shell
tz at [--time-format=...] [--separator=...] <CSV of time zones> [time to get]
```

Example

```shell
❯ tz at 'Australia/Melbourne,Australia/Brisbane' 3pm
4pm AEDT / 3pm AEST
```

To find the list of valid time zones, run the command

```shell
tz list-timezones
```

## Development

### Set up

To install dependencies, do

```shell
poetry install --no-root
```

### Dev loop

```shell
poetry sync
python teamzones
```

### Install loop

```shell
poetry install
tz --help
```
