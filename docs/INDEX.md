# Documentation and Repository Index

This index provides a comprehensive navigation map across all documentation, implementation areas, governance artifacts, and historical specifications in `boq_system_v2`.

Document precedence is governed by [`docs/governance/DOCUMENT_AUTHORITY_INDEX_R1.md`](governance/DOCUMENT_AUTHORITY_INDEX_R1.md).

---

## 1. Top-Level Resumability & Product Direction

- **[`PROJECT_STATE.md`](../PROJECT_STATE.md)** — Current milestone, gate state, critical path, and resumability checkpoint (`AUTHORITATIVE_DOC`).
- **[`README.md`](../README.md)** — Project overview, product thesis, and core architecture (`AUTHORITATIVE_DOC`).
- **[`docs/product/PRODUCT_VISION_R3.md`](product/PRODUCT_VISION_R3.md)** — Core product vision, thesis, differentiator, and user journeys (`AUTHORITATIVE_DOC`).
- **[`docs/product/PRODUCT_PLAN_R3.md`](product/PRODUCT_PLAN_R3.md)** — Master roadmap, vertical slice sequencing, and delivery milestones (`AUTHORITATIVE_DOC`).
- **[`docs/product/PRODUCT_STRATEGY_DECISION_ARCHIVE_R2.md`](product/PRODUCT_STRATEGY_DECISION_ARCHIVE_R2.md)** — Historical record of product strategy decisions (`AUTHORITATIVE_DOC`).
- **[`docs/product/CORPUS_AND_BENCHMARK_STRATEGY_R1.md`](product/CORPUS_AND_BENCHMARK_STRATEGY_R1.md)** — Strategy for CAD/BIM corpus curation and benchmark standards (`AUTHORITATIVE_DOC`).

---

## 2. Governance and Structure

- **[`docs/governance/DOCUMENT_AUTHORITY_INDEX_R1.md`](governance/DOCUMENT_AUTHORITY_INDEX_R1.md)** — Canonical document authority and conflict resolution rules (`AUTHORITATIVE_DOC`).
- **[`docs/governance/REPOSITORY_MAP_R1.json`](governance/REPOSITORY_MAP_R1.json)** — Machine-readable classification map of repository directories and paths (`AUTHORITATIVE_DOC`).
- **[`docs/governance/REPOSITORY_HYGIENE_PLAN_R1.md`](governance/REPOSITORY_HYGIENE_PLAN_R1.md)** — Hygiene guidelines for binaries, generated files, and clean git history (`AUTHORITATIVE_DOC`).
- **Research Governance Charters (`docs/governance/research/`)**:
  - [`RESEARCH_PROGRAM_CHARTER_R1.md`](governance/research/RESEARCH_PROGRAM_CHARTER_R1.md) — Two-lane research governance structure.
  - [`RESEARCH_LANE_A_CHARTER_R1.md`](governance/research/RESEARCH_LANE_A_CHARTER_R1.md) — Technical Lane A (CAD/BIM, DWG, Parser).
  - [`RESEARCH_LANE_B_CHARTER_R1.md`](governance/research/RESEARCH_LANE_B_CHARTER_R1.md) — Commercial Lane B (Market, UX, Process).
  - [`RESEARCH_GOVERNANCE_INDEX_R1.md`](governance/research/RESEARCH_GOVERNANCE_INDEX_R1.md) — Index of research charters.

---

## 3. Subsystem Areas and Technical Specifications

### Parser Subsystem
- **Current Implementation:** `backend/engine/` (`pdf_dxf_parser.py`, `claude_web_extractor.py`, OCR utilities).
- **Historical Baseline Specification:** [`parser_design_spec.md`](../parser_design_spec.md), [`tech_spec_parser_v2.md`](../tech_spec_parser_v2.md) (`HISTORICAL_DOC`).
- **Test Suites:** `test_dxf_parser.py`, `tests/` (`CURRENT_IMPLEMENTATION`).

### Integration Subsystem
- **Active Milestone:** `PIS-CONTRACT-FREEZE-001` (Under QA review).
- **Role:** Contract mediation, coordinate transformation, unit normalization, and conflict gate enforcement.

### Solver Subsystem
- **Current Implementation:** `backend/engine/fajardo.py`, `backend/engine/dupa_loader.py`.
- **Baseline Audit & Golden Cases:** `tests/solver/baseline/`, `tests/solver/golden/` (`ACCEPTED_EVIDENCE`).
- **Historical Specification:** [`solver_design_spec.md`](../solver_design_spec.md), [`formula_exhaustive_handbook.md`](../formula_exhaustive_handbook.md) (`HISTORICAL_DOC`).

---

## 4. Accepted Research Evidence Branches

Research evidence is preserved in a cumulative, non-production archival branch chain:

- **`research/wave2-evidence`** (`815d44214a2f52dd34fbc05a0c2faab83b1feb95`)
  - Accepted Wave 2 research: Fajardo formula audit, solver baseline calculations, DPWH standards.
- **`research/wave3-evidence`** (`0631843aecfbcdbd3e30ac2e7c6a2f2d5794f449`)
  - Accepted Wave 3 research: Concrete, Earthworks, Forms, Finishes, Steel, Labor/Equipment norms.
- **`research/wave4-evidence`** (`e31a88eda52a6ce090209ff0fd0f763b5a12ff0c`)
  - Accepted Wave 4 research:
    - Lane A: CAD corpus audit (38 DWG drawings), native DWG reader benchmark (`ezdwg 0.11.0`), synthetic ParserBench.
    - Lane B: Takeoff market analysis, UX interaction models, Philippine estimating process workflows (with S31 author erratum).

---

## 5. Historical and Contextual Documents

The following root documents reflect earlier project iterations and are partially superseded:

- **[`tech_spec_v2.md`](../tech_spec_v2.md)** (`HISTORICAL_DOC`) — Early monolithic technical specification.
- **[`progress_report_v2.md`](../progress_report_v2.md)** (`HISTORICAL_DOC`) — Historical project progress report.
- **[`sample_solved_cases.md`](../sample_solved_cases.md)** (`HISTORICAL_DOC`) — Early exploratory solved examples.
- **[`outputs/`](../outputs/)** (`RUNTIME_GENERATED`) — Runtime logs, SVG overlays, and extracted session outputs.
- **[`backend/reference_data/`](../backend/reference_data/)** (`REFERENCE_DATA`) — Third-party CAD drawings, PDF books, price lists, and sample inputs.
