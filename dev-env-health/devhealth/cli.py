"""Developer Environment Health CLI.

This tool inspects a machine and produces a deterministic
developer-environment health report.
"""

from __future__ import annotations

import argparse
import json
import platform
import socket
import subprocess
import sys
from pathlib import Path
from typing import Any


# ---------------------------------------------------------
# Run a command and get its version
# ---------------------------------------------------------

def run_version(command: list[str]) -> str | None:
    """Run a version command safely.

    Returns:
        The first non-empty output line, or None if unavailable.
    """

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )

    except (OSError, subprocess.SubprocessError):
        return None

    output = (result.stdout or result.stderr).strip()

    if result.returncode != 0 or not output:
        return None

    for line in output.splitlines():
        line = line.strip()

        if line:
            return line

    return None


# ---------------------------------------------------------
# Check hostname resolution
# ---------------------------------------------------------

def hostname_resolves() -> bool:
    """Check whether the machine hostname resolves."""

    try:
        socket.gethostbyname(socket.gethostname())
        return True

    except OSError:
        return False


# ---------------------------------------------------------
# Determine overall health
# ---------------------------------------------------------

def overall_health(checks: list[dict[str, str]]) -> str:
    """Calculate the overall health from individual checks."""

    if any(check["status"] == "FAIL" for check in checks):
        return "FAIL"

    if any(check["status"] == "WARN" for check in checks):
        return "WARN"

    return "PASS"


# ---------------------------------------------------------
# Inspect the machine
# ---------------------------------------------------------

def inspect_machine() -> dict[str, Any]:
    """Inspect the current machine.

    The report intentionally avoids timestamps, random values,
    IP addresses, memory usage, disk usage, and network APIs
    so repeated runs remain deterministic.
    """

    commands = {
        "docker": ["docker", "--version"],
        "git": ["git", "--version"],
        "java": ["java", "-version"],
        "node": ["node", "--version"],
        "npm": ["npm", "--version"],
        "python": [sys.executable, "--version"],
    }

    tools: dict[str, str | None] = {}

    for name in sorted(commands):
        tools[name] = run_version(commands[name])

    checks: list[dict[str, str]] = []

    # Tool checks
    for name in sorted(tools):
        version = tools[name]

        if version:
            status = "PASS"
            details = version

        else:
            status = "WARN"
            details = f"{name} was not found on PATH"

        checks.append(
            {
                "name": f"{name}_installed",
                "status": status,
                "details": details,
            }
        )

    # Hostname check
    hostname = socket.gethostname()

    if hostname_resolves():
        hostname_status = "PASS"
    else:
        hostname_status = "WARN"

    checks.append(
        {
            "name": "hostname_resolves",
            "status": hostname_status,
            "details": hostname,
        }
    )

    # pip check
    pip_version = run_version(
        [
            sys.executable,
            "-m",
            "pip",
            "--version",
        ]
    )

    if pip_version:
        pip_status = "PASS"
        pip_details = "Python pip module"
    else:
        pip_status = "WARN"
        pip_details = "pip was not available"

    checks.append(
        {
            "name": "pip_available",
            "status": pip_status,
            "details": pip_details,
        }
    )

    # Sort checks for deterministic output.
    checks.sort(key=lambda check: check["name"])

    report: dict[str, Any] = {
        "schema_version": 1,

        "platform": {
            "architecture": platform.machine(),
            "os": platform.system(),
            "os_release": platform.release(),
            "python_implementation": platform.python_implementation(),
            "python_version": platform.python_version(),
        },

        "tools": tools,

        "checks": checks,

        "health": overall_health(checks),
    }

    return report


# ---------------------------------------------------------
# Render human-readable report
# ---------------------------------------------------------

def render_text(report: dict[str, Any]) -> str:
    """Convert a report into human-readable text."""

    platform_info = report["platform"]

    lines = [
        "DEVELOPER ENVIRONMENT HEALTH REPORT",
        "======================================",
        f"Health: {report['health']}",
        "",
        "Platform",
        "--------",
        (
            f"OS: {platform_info['os']} "
            f"{platform_info['os_release']}"
        ),
        f"Architecture: {platform_info['architecture']}",
        (
            f"Python: "
            f"{platform_info['python_implementation']} "
            f"{platform_info['python_version']}"
        ),
        "",
        "Tools",
        "-----",
    ]

    for name in sorted(report["tools"]):
        version = report["tools"][name]

        if version is None:
            version_text = "NOT FOUND"
        else:
            version_text = version

        lines.append(f"{name}: {version_text}")

    lines.extend(
        [
            "",
            "Checks",
            "------",
        ]
    )

    for check in report["checks"]:
        lines.append(
            f"[{check['status']}] "
            f"{check['name']}: "
            f"{check['details']}"
        )

    return "\n".join(lines)


# ---------------------------------------------------------
# Command-line interface
# ---------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    parser = argparse.ArgumentParser(
        prog="devhealth",
        description=(
            "Inspect a machine and produce a "
            "deterministic developer-environment health report."
        ),
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="print the report as JSON",
    )

    parser.add_argument(
        "--output",
        type=Path,
        help="write the report to a file",
    )

    args = parser.parse_args(argv)

    report = inspect_machine()

    if args.json:
        output = (
            json.dumps(
                report,
                indent=2,
                sort_keys=True,
            )
            + "\n"
        )

    else:
        output = render_text(report) + "\n"

    if args.output:
        args.output.write_text(
            output,
            encoding="utf-8",
        )

    else:
        print(output, end="")

    # Return 1 only if an actual FAIL exists.
    if report["health"] == "FAIL":
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())