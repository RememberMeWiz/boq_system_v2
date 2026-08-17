#!/usr/bin/env python3
"""Execute the exact 30 PM-accepted M2-2 negative fixtures."""
from __future__ import annotations

import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))

from backend.integration.m2_2_rc_beam_profile import M2RcBeamNetMeasuredRuntime

SCHEMA_DIR = ROOT / "schemas/integration"
MANIFEST = json.loads((HERE / "negative_fixture_manifest_v1.json").read_text())
BASE = json.loads((HERE / "base_blocked_readiness_snapshot_v1.json").read_text())


def main() -> int:
    runtime = M2RcBeamNetMeasuredRuntime(SCHEMA_DIR)
    baseline_digest = runtime.engineering_input_digest(BASE)
    results = []
    for item in MANIFEST["fixtures"]:
        fixture = json.loads((HERE / item["file"]).read_text())
        payload = fixture["payload"]
        result = runtime.evaluate(payload)
        expected = fixture["expected"]
        if expected == "NET_MEASURED_AND_DIGEST_UNCHANGED":
            passed = result["engineering_input_digest"] == baseline_digest
            observed = "NET_MEASURED_AND_DIGEST_UNCHANGED" if passed else "ENGINEERING_DIGEST_CHANGED"
        else:
            observed = result["outcome"]
            passed = observed == expected
        results.append({
            "case_id": item["case_id"],
            "expected": expected,
            "observed": observed,
            "pass": passed,
            "calculation_input": result["calculation_input"],
            "solver_called": result["solver_called"],
        })

    out = {
        "suite": "M2_RCBEAM_001_M2_2_NEGATIVE_FIXTURES_R1",
        "cases": len(results),
        "passed": sum(x["pass"] for x in results),
        "failed": sum(not x["pass"] for x in results),
        "results": results,
    }
    print(json.dumps(out, indent=2))
    return 0 if out["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
