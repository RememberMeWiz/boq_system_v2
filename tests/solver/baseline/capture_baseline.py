#!/usr/bin/env python3
"""Capture the immutable S0-001 solver baseline without editing production code.

Run from any directory:
    python tests/solver/baseline/capture_baseline.py

The script records environment metadata, raw command stdout/stderr, source hashes,
and two fresh-process executions of each deterministic solver sample.
"""

from __future__ import annotations

import argparse
import copy
import dataclasses
import hashlib
import json
import os
import platform
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path
from typing import Any, Callable

SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[3]
BASELINE_DIR = SCRIPT_PATH.parent
LOG_DIR = BASELINE_DIR / "logs"

REPOSITORY_URL = "https://github.com/RememberMeWiz/boq_system_v2"
BRANCH = "main"
COMMIT = "97f16aa3fd7b6d8e7cd364b6edc2ac303a5f54e6"

# Ensure the repository root is importable even when this file is launched by path.
sys.path.insert(0, str(REPO_ROOT))

from backend.engine.fajardo import (  # noqa: E402
    calculate_section_3_concrete_and_formworks,
    calculate_section_5_metals_and_rebar,
    run_full_takeoff,
)
from backend.engine.rebar_optimizer import (  # noqa: E402
    RebarCutDemand,
    RebarStockOptimizer,
)


SECTION_III_INPUT: list[dict[str, Any]] = [
    {
        "type": "footing",
        "class": "A",
        "count": 4,
        "length_m": 1.50,
        "width_m": 1.50,
        "height_m": 0.40,
    }
]

SECTION_V_WORKED_INPUT: list[dict[str, Any]] = [
    {
        "member": "footing_mat",
        "diameter_mm": 16.0,
        "count": 80,
        "member_length_m": 1.50,
        "cover_m": 0.075,
    }
]

# The existing automated test is labeled as the 218.90 kg worked case, but its
# input supplies 40 bars rather than the worked example's 80 bars for four footings.
# Capture it separately so both the documented case and the test's actual behavior
# are frozen without correcting either one.
SECTION_V_EXISTING_TEST_INPUT: list[dict[str, Any]] = [
    {
        "member": "footing_mat",
        "diameter_mm": 16.0,
        "count": 40,
        "member_length_m": 1.50,
        "cover_m": 0.075,
    }
]

FULL_13_TRADE_INPUT: dict[int, dict[str, Any]] = {
    2: {
        "footing_specs": [
            {
                "length_m": 1.5,
                "width_m": 1.5,
                "depth_m": 0.4,
                "count": 4,
            }
        ],
        "slab_area": 120.0,
        "slab_t": 0.10,
    },
    3: {
        "elements": [
            {
                "type": "footing",
                "class": "A",
                "count": 4,
                "length_m": 1.5,
                "width_m": 1.5,
                "height_m": 0.4,
            }
        ]
    },
    4: {
        "wall_elements": [
            {
                "length_m": 10.0,
                "height_m": 3.0,
                "thickness_mm": 150,
                "openings": [{"width_m": 1.5, "height_m": 1.5}],
            }
        ]
    },
    5: {
        "rebar_elements": [
            {
                "member": "generic",
                "diameter_mm": 16.0,
                "count": 20,
                "length_m": 6.0,
            }
        ],
        "structural_steel_kg": 150.0,
    },
    6: {"roof_plan_area": 100.0, "pitch_deg": 15.0, "ceiling_area": 90.0},
    7: {"windows_sqm": 12.0, "doors": [{"type": "panel", "count": 2}]},
    8: {"floor_area": 80.0, "wall_area": 30.0, "is_diagonal": False},
    9: {
        "masonry_area": 150.0,
        "ceiling_area": 90.0,
        "metal_area": 10.0,
        "is_rough_chb": False,
    },
    10: {"sanitary_run_m": 25.0, "water_run_m": 20.0, "fixtures_count": 4},
    11: {"outlets_count": 16, "homerun_m": 45.0},
    12: {"room_area_m2": 50.0, "pipe_run_m": 10.0},
    13: {"handrail_m": 8.0, "acp_m2": 15.0, "waterproofing_m2": 30.0},
}

REBAR_OPTIMIZER_INPUT: dict[str, Any] = {
    "diameter_mm": 20,
    "demands": [
        {
            "diameter_mm": 20,
            "required_length_m": 4.0,
            "quantity": 10,
            "element_ref": "Column Main",
        },
        {
            "diameter_mm": 20,
            "required_length_m": 5.8,
            "quantity": 5,
            "element_ref": "Beam Main",
        },
    ],
    "stock_lengths_m": [12.0, 9.0, 6.0],
}


DECLARED_PACKAGES: list[tuple[str, str]] = [
    ("flask", "flask"),
    ("ezdxf", "ezdxf"),
    ("PyMuPDF", "PyMuPDF"),
    ("pdfplumber", "pdfplumber"),
    ("openpyxl", "openpyxl"),
    ("pywebview", "pywebview"),
    ("requests", "requests"),
    ("pytest", "pytest"),
    ("pillow", "pillow"),
    ("matplotlib", "matplotlib"),
    ("svgwrite", "svgwrite"),
    ("pytesseract", "pytesseract"),
    ("opencv-python-headless", "opencv-python-headless"),
    ("google-genai", "google-genai"),
    ("pandas", "pandas"),
]

INTEGRITY_FILES = [
    "backend/engine/fajardo.py",
    "backend/engine/rebar_optimizer.py",
    "backend/engine/dupa_loader.py",
    "backend/engine/pdf_dxf_parser.py",
    "backend/engine/test_extraction_suite.py",
    "backend/engine/test_vector_diff.py",
    "test_fajardo_v2.py",
    "test_dxf_parser.py",
]


@dataclasses.dataclass(frozen=True)
class CommandSpec:
    id: str
    display: str
    argv: tuple[str, ...]
    category: str
    env_overrides: dict[str, str] = dataclasses.field(default_factory=dict)


def json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(json_bytes(value)).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, allow_nan=False, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    temp.replace(path)


def hash_integrity_files() -> dict[str, Any]:
    result: dict[str, Any] = {}
    for relative in INTEGRITY_FILES:
        path = REPO_ROOT / relative
        if path.exists():
            result[relative] = {
                "exists": True,
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        else:
            result[relative] = {"exists": False}
    return result


def dependency_versions() -> dict[str, Any]:
    versions: dict[str, Any] = {}
    for label, distribution in DECLARED_PACKAGES:
        try:
            versions[label] = {"installed": True, "version": metadata.version(distribution)}
        except metadata.PackageNotFoundError:
            versions[label] = {"installed": False, "version": None}
    return versions


def read_os_release() -> dict[str, str]:
    path = Path("/etc/os-release")
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key] = value.strip().strip('"')
    return values


def environment_payload() -> dict[str, Any]:
    sample_dir = REPO_ROOT / "backend/reference_data/sample_inputs"
    sample_files = sorted(
        str(path.relative_to(REPO_ROOT))
        for path in sample_dir.glob("*")
        if path.is_file()
    ) if sample_dir.exists() else []

    return {
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "repository": {
            "url": REPOSITORY_URL,
            "branch": BRANCH,
            "commit": COMMIT,
            "checkout_mode": "immutable-source reconstruction; not a Git clone",
        },
        "python": {
            "executable": sys.executable,
            "version": sys.version,
            "version_info": list(sys.version_info),
            "implementation": platform.python_implementation(),
        },
        "operating_system": {
            "platform": platform.platform(),
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "os_release": read_os_release(),
        },
        "dependencies_declared_in_requirements": dependency_versions(),
        "reference_input_files_present": sample_files,
        "reference_input_file_count": len(sample_files),
    }


def section_iii_case() -> dict[str, Any]:
    return calculate_section_3_concrete_and_formworks(copy.deepcopy(SECTION_III_INPUT))


def section_v_worked_case() -> dict[str, Any]:
    return calculate_section_5_metals_and_rebar(copy.deepcopy(SECTION_V_WORKED_INPUT))


def section_v_existing_test_case() -> dict[str, Any]:
    return calculate_section_5_metals_and_rebar(copy.deepcopy(SECTION_V_EXISTING_TEST_INPUT))


def full_13_trade_case() -> dict[str, Any]:
    return run_full_takeoff(copy.deepcopy(FULL_13_TRADE_INPUT))


def rebar_optimizer_case() -> dict[str, Any]:
    demands = [RebarCutDemand(**item) for item in copy.deepcopy(REBAR_OPTIMIZER_INPUT["demands"])]
    optimizer = RebarStockOptimizer(copy.deepcopy(REBAR_OPTIMIZER_INPUT["stock_lengths_m"]))
    result = optimizer.optimize_diameter(REBAR_OPTIMIZER_INPUT["diameter_mm"], demands)
    return dataclasses.asdict(result)


def execute_samples_once() -> dict[str, Any]:
    samples: list[tuple[str, str, Any, Callable[[], dict[str, Any]]]] = [
        (
            "section_iii_concrete_worked_case",
            "test_fajardo_v2.py::TestFajardoEngineV2::test_section_3_footing_concrete_worked_case",
            SECTION_III_INPUT,
            section_iii_case,
        ),
        (
            "section_v_reinforcement_worked_case",
            "sample_solved_cases.md §2.2 (four footings, 80 total bars)",
            SECTION_V_WORKED_INPUT,
            section_v_worked_case,
        ),
        (
            "section_v_existing_automated_test_case",
            "test_fajardo_v2.py::TestFajardoEngineV2::test_section_5_rebar_footing_mat_worked_case",
            SECTION_V_EXISTING_TEST_INPUT,
            section_v_existing_test_case,
        ),
        (
            "full_13_trade_takeoff_sample",
            "test_fajardo_v2.py::TestFajardoEngineV2::test_full_13_trade_takeoff_pipeline",
            FULL_13_TRADE_INPUT,
            full_13_trade_case,
        ),
        (
            "rebar_optimizer_sample",
            "test_fajardo_v2.py::TestRebarOptimizer::test_bin_packing_scrap_reduction",
            REBAR_OPTIMIZER_INPUT,
            rebar_optimizer_case,
        ),
    ]

    output: dict[str, Any] = {}
    for sample_id, source, sample_input, function in samples:
        result = function()
        # Round-trip through strict JSON now, so the stored object is exactly JSON-compatible.
        result_json_compatible = json.loads(json_bytes(result).decode("utf-8"))
        input_json_compatible = json.loads(json_bytes(sample_input).decode("utf-8"))
        output[sample_id] = {
            "source": source,
            "input": input_json_compatible,
            "output": result_json_compatible,
            "output_canonical_sha256": sha256_json(result_json_compatible),
        }
    return output


def run_command(spec: CommandSpec) -> dict[str, Any]:
    env = os.environ.copy()
    env.update(spec.env_overrides)
    completed = subprocess.run(
        list(spec.argv),
        cwd=REPO_ROOT,
        env=env,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )

    stdout_name = f"{spec.id}.stdout.txt"
    stderr_name = f"{spec.id}.stderr.txt"
    (LOG_DIR / stdout_name).write_text(completed.stdout, encoding="utf-8", newline="")
    (LOG_DIR / stderr_name).write_text(completed.stderr, encoding="utf-8", newline="")

    return {
        "id": spec.id,
        "category": spec.category,
        "command": spec.display,
        "argv": list(spec.argv),
        "shell_quoted_argv": shlex.join(spec.argv),
        "cwd": str(REPO_ROOT),
        "environment_overrides": spec.env_overrides,
        "exit_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "stdout_log": str((Path("tests/solver/baseline/logs") / stdout_name).as_posix()),
        "stderr_log": str((Path("tests/solver/baseline/logs") / stderr_name).as_posix()),
    }


def capture_fresh_process_sample_runs() -> tuple[list[dict[str, Any]], str]:
    process_runs: list[dict[str, Any]] = []
    for run_number in (1, 2):
        command = [sys.executable, str(SCRIPT_PATH), "--emit-samples-once"]
        completed = subprocess.run(
            command,
            cwd=REPO_ROOT,
            text=True,
            encoding="utf-8",
            errors="strict",
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError(
                f"sample subprocess run {run_number} failed with exit code "
                f"{completed.returncode}: {completed.stderr}"
            )
        payload = json.loads(completed.stdout)
        process_runs.append(
            {
                "run_number": run_number,
                "argv": command,
                "exit_code": completed.returncode,
                "stderr": completed.stderr,
                "payload": payload,
                "payload_canonical_sha256": sha256_json(payload),
            }
        )

    overall = "PASS" if process_runs[0]["payload"] == process_runs[1]["payload"] else "FAIL"
    return process_runs, overall


def build_current_outputs(process_runs: list[dict[str, Any]]) -> dict[str, Any]:
    first = process_runs[0]["payload"]
    second = process_runs[1]["payload"]
    sample_ids = list(first.keys())
    samples: dict[str, Any] = {}

    for sample_id in sample_ids:
        run_1 = first[sample_id]
        run_2 = second[sample_id]
        same_input = run_1["input"] == run_2["input"]
        same_output = run_1["output"] == run_2["output"]
        same_hash = run_1["output_canonical_sha256"] == run_2["output_canonical_sha256"]
        samples[sample_id] = {
            "source": run_1["source"],
            "input": run_1["input"],
            "run_1": {
                "output": run_1["output"],
                "output_canonical_sha256": run_1["output_canonical_sha256"],
            },
            "run_2": {
                "output": run_2["output"],
                "output_canonical_sha256": run_2["output_canonical_sha256"],
            },
            "determinism": {
                "inputs_equal": same_input,
                "outputs_equal": same_output,
                "canonical_hashes_equal": same_hash,
                "result": "PASS" if same_input and same_output and same_hash else "FAIL",
            },
        }

    return {
        "schema_version": 1,
        "repository": {"url": REPOSITORY_URL, "branch": BRANCH, "commit": COMMIT},
        "execution": {
            "method": "two independent fresh Python processes",
            "process_payload_hashes": [run["payload_canonical_sha256"] for run in process_runs],
            "all_samples_deterministic": all(
                sample["determinism"]["result"] == "PASS" for sample in samples.values()
            ),
        },
        "samples": samples,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit-samples-once", action="store_true")
    args = parser.parse_args()

    if args.emit_samples_once:
        json.dump(
            execute_samples_once(),
            sys.stdout,
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        sys.stdout.write("\n")
        return 0

    BASELINE_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    integrity_before = hash_integrity_files()
    atomic_write_json(BASELINE_DIR / "environment.json", environment_payload())

    python = sys.executable
    command_specs = [
        CommandSpec(
            id="01_git_ls_remote_main",
            category="repository_probe",
            display=f"git ls-remote --heads {REPOSITORY_URL} main",
            argv=("git", "ls-remote", "--heads", REPOSITORY_URL, "main"),
        ),
        CommandSpec(
            id="02_python_vv",
            category="environment",
            display="python -VV",
            argv=(python, "-VV"),
        ),
        CommandSpec(
            id="03_uname_a",
            category="environment",
            display="uname -a",
            argv=("uname", "-a"),
        ),
        CommandSpec(
            id="04_os_release",
            category="environment",
            display="cat /etc/os-release",
            argv=("cat", "/etc/os-release"),
        ),
        CommandSpec(
            id="05_reference_input_inventory",
            category="precondition",
            display="find backend/reference_data/sample_inputs -maxdepth 1 -type f -printf '%f\\n' | sort",
            argv=(
                "bash",
                "-lc",
                "find backend/reference_data/sample_inputs -maxdepth 1 -type f -printf '%f\\n' | sort",
            ),
        ),
        CommandSpec(
            id="10_pytest_ra",
            category="test",
            display="python -m pytest -ra",
            argv=(python, "-m", "pytest", "-ra"),
        ),
        CommandSpec(
            id="10a_pytest_solver_only",
            category="test",
            display="python -m pytest -ra test_fajardo_v2.py",
            argv=(python, "-m", "pytest", "-ra", "test_fajardo_v2.py"),
        ),
        CommandSpec(
            id="11_unittest_fajardo_v2",
            category="test",
            display="python -m unittest -v test_fajardo_v2.py",
            argv=(python, "-m", "unittest", "-v", "test_fajardo_v2.py"),
        ),
        CommandSpec(
            id="12_dxf_parser_script",
            category="test",
            display="python test_dxf_parser.py",
            argv=(python, "test_dxf_parser.py"),
        ),
        CommandSpec(
            id="13_extraction_suite_script",
            category="test",
            display="python backend/engine/test_extraction_suite.py",
            argv=(python, "backend/engine/test_extraction_suite.py"),
        ),
        CommandSpec(
            id="14_vector_diff_script",
            category="test",
            display="MPLBACKEND=Agg python backend/engine/test_vector_diff.py",
            argv=(python, "backend/engine/test_vector_diff.py"),
            env_overrides={"MPLBACKEND": "Agg"},
        ),
    ]

    command_results = [run_command(spec) for spec in command_specs]
    atomic_write_json(
        BASELINE_DIR / "command_runs.json",
        {
            "schema_version": 1,
            "repository": {"url": REPOSITORY_URL, "branch": BRANCH, "commit": COMMIT},
            "runs": command_results,
        },
    )

    process_runs, determinism_result = capture_fresh_process_sample_runs()
    current_outputs = build_current_outputs(process_runs)
    atomic_write_json(BASELINE_DIR / "current_outputs.json", current_outputs)

    integrity_after = hash_integrity_files()
    integrity_equal = integrity_before == integrity_after
    atomic_write_json(
        BASELINE_DIR / "source_integrity.json",
        {
            "schema_version": 1,
            "files": INTEGRITY_FILES,
            "before": integrity_before,
            "after": integrity_after,
            "unchanged": integrity_equal,
        },
    )

    summary = {
        "test_commands": [
            {
                "id": run["id"],
                "exit_code": run["exit_code"],
                "command": run["command"],
            }
            for run in command_results
            if run["category"] == "test"
        ],
        "determinism": determinism_result,
        "source_integrity": "PASS" if integrity_equal else "FAIL",
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if integrity_equal and determinism_result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
