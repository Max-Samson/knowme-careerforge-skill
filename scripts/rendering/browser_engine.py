"""Standard-library bridge to the single Node rendering/validation engine."""
import json
import subprocess
from pathlib import Path

ENGINE = Path(__file__).resolve().with_name("browser-engine.js")


def run(html, *, expected_pages=1, auto_heal=False, output_pdf=None):
    command = ["node", str(ENGINE), str(Path(html).resolve()),
               "--expected-pages", str(expected_pages)]
    if auto_heal:
        command.append("--auto-heal")
    if output_pdf is not None:
        command.extend(["--output", str(Path(output_pdf).resolve())])
    try:
        # The engine bounds browser operations and owns publication/cleanup.
        proc = subprocess.run(command, capture_output=True, text=True)
        result = json.loads(proc.stdout)
        if not isinstance(result, dict):
            raise ValueError('Engine result must be an object')
        expected_exit = {"PASS": 0, "FAIL": 1, "UNVERIFIED": 2}.get(result.get("status"))
        if (expected_exit is None or proc.returncode != expected_exit
                or not isinstance(result.get("errors"), list)
                or not isinstance(result.get("warnings"), list)
                or not isinstance(result.get("checks"), dict)
                or (result["status"] == "PASS" and (result["errors"] or any(
                    not isinstance(result["checks"].get(key), dict) or result["checks"][key].get("status") != "PASS"
                    for key in ('input', 'fonts', 'dom', 'pdf', 'text', 'output'))))):
            raise ValueError("Invalid engine result or exit-code mismatch")
        return result
    except (OSError, ValueError) as error:
        return {"status": "UNVERIFIED", "file": str(Path(html).resolve()),
                "expectedPages": expected_pages, "errors": [str(error)],
                "warnings": [], "checks": {"engine": {"status": "UNVERIFIED"}}}


def exit_code(result):
    return {"PASS": 0, "FAIL": 1, "UNVERIFIED": 2}[result["status"]]
