from __future__ import annotations

import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from .models import FailureSignature, ValidationOutcome


def _kind_from_message(message: str, nodeid: str) -> str:
    lowered = f"{message} {nodeid}".lower()
    if "duplicate_refund" in lowered:
        return "duplicate_refund"
    if "inventory_not_restored_qty_two" in lowered:
        return "inventory_not_restored_qty_two"
    if "inventory_not_restored" in lowered:
        return "inventory_not_restored"
    if "inventory_negative" in lowered:
        return "inventory_negative"
    return "unknown_failure"


def _severity_from_nodeid(nodeid: str) -> str:
    lowered = nodeid.lower()
    if "hard" in lowered:
        return "hard"
    return "soft"


def run_pytest_validation(workspace: Path) -> ValidationOutcome:
    report_name = "pytest_report.xml"
    xml_path = workspace / report_name

    if xml_path.exists():
        xml_path.unlink()

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests",
            "generated_tests",
            "-q",
            f"--junitxml={report_name}",
        ],
        cwd=workspace,
        capture_output=True,
        text=True,
        check=False,
    )

    outcome = ValidationOutcome(raw_summary={"pytest_exit_code": completed.returncode})

    if not xml_path.exists():
        outcome.hard_failures.append(
            FailureSignature(
                kind="pytest_runner_failure",
                severity="hard",
                nodeid="pytest",
                message=completed.stderr or completed.stdout or "pytest report missing",
            )
        )
        return outcome

    root = ET.parse(xml_path).getroot()
    for testcase in root.iter("testcase"):
        classname = testcase.attrib.get("classname", "")
        name = testcase.attrib.get("name", "")
        nodeid = f"{classname}::{name}"

        failure = testcase.find("failure")
        error = testcase.find("error")
        skipped = testcase.find("skipped")

        if failure is None and error is None and skipped is None:
            outcome.passed.append(nodeid)
            continue

        message = ""
        if failure is not None:
            message = failure.attrib.get("message", "") + " " + (failure.text or "")
        elif error is not None:
            message = error.attrib.get("message", "") + " " + (error.text or "")
        else:
            message = skipped.attrib.get("message", "")

        signature = FailureSignature(
            kind=_kind_from_message(message, nodeid),
            severity=_severity_from_nodeid(nodeid),
            nodeid=nodeid,
            message=message.strip(),
        )

        if signature.severity == "hard":
            outcome.hard_failures.append(signature)
        else:
            outcome.soft_failures.append(signature)

    return outcome