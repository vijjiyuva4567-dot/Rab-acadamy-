import json
import unittest

from devhealth.cli import (
    overall_health,
    render_text,
)


class TestDevHealth(unittest.TestCase):

    def test_health_precedence(self):
        checks = [
            {
                "name": "first",
                "status": "WARN",
                "details": "warning",
            },
            {
                "name": "second",
                "status": "PASS",
                "details": "passed",
            },
        ]

        self.assertEqual(
            overall_health(checks),
            "WARN",
        )

        checks.append(
            {
                "name": "third",
                "status": "FAIL",
                "details": "failed",
            }
        )

        self.assertEqual(
            overall_health(checks),
            "FAIL",
        )

    def test_json_is_deterministic(self):
        report = {
            "schema_version": 1,
            "health": "PASS",
            "platform": {
                "architecture": "AMD64",
                "os": "Windows",
                "os_release": "11",
                "python_implementation": "CPython",
                "python_version": "3.13.1",
            },
            "tools": {
                "git": "git version 2.0",
                "python": "Python 3.13.1",
            },
            "checks": [],
        }

        first = json.dumps(
            report,
            indent=2,
            sort_keys=True,
        )

        second = json.dumps(
            report,
            indent=2,
            sort_keys=True,
        )

        self.assertEqual(first, second)

        self.assertNotIn(
            "timestamp",
            first,
        )

    def test_text_report(self):
        report = {
            "health": "PASS",

            "platform": {
                "os": "Windows",
                "os_release": "11",
                "architecture": "AMD64",
                "python_implementation": "CPython",
                "python_version": "3.13.1",
            },

            "tools": {
                "git": "git version 2.0",
            },

            "checks": [
                {
                    "name": "git_installed",
                    "status": "PASS",
                    "details": "git version 2.0",
                }
            ],
        }

        text = render_text(report)

        self.assertIn(
            "DEVELOPER ENVIRONMENT HEALTH REPORT",
            text,
        )

        self.assertIn(
            "Platform",
            text,
        )

        self.assertIn(
            "Tools",
            text,
        )

        self.assertIn(
            "[PASS] git_installed",
            text,
        )


if __name__ == "__main__":
    unittest.main()