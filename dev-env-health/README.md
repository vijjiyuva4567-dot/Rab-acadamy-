# Dev Environment Health

A zero-dependency Python command-line tool that inspects a machine and produces a deterministic developer-environment health report.

## Features

- Detects OS, architecture, Python implementation/version, and hostname resolution.
- Checks common developer tools: Python, pip, Git, Node.js, npm, Java, and Docker.
- Produces human-readable or JSON reports.
- Uses stable sorting and does not include timestamps, random IDs, or network lookups.
- Returns exit code `0` for PASS/WARN and `1` for FAIL.
- Packaged as an installable command-line application.

## Install locally

```powershell
cd dev_env_health
python -m pip install .
```

Then run:

```powershell
devhealth
devhealth --json
devhealth --output health-report.txt
devhealth --json --output health-report.json
```

You can also run it without installing:

```powershell
python -m devhealth
```

## Determinism

The report intentionally excludes current time, usernames, IP addresses, process IDs, memory usage, disk free space, and other values that can change between runs. Tool discovery is based on PATH and versions are normalized to the first non-empty version line.

## Exit codes

- `0`: no failing checks (PASS or WARN)
- `1`: at least one FAIL check
