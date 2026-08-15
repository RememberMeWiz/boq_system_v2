# Wave 4 Research Lane A Evidence Archive

## Disposition

- **PM Disposition:** Accepted as reference evidence only.
- **Evidence Class:** CAD/BIM extraction methodology, multi-discipline DWG corpus analysis, native DWG reader toolchain evaluation, and synthetic parser ground-truth benchmark design.
- **Merge Status:** Archival reference branch only. No merge to `main` is authorized or implied.

## Scope and Contents

This archive preserves the complete, verified closure evidence chain for Wave 4 Research Lane A:
1. `RESEARCH_1_R4_CAD_001` — Multi-discipline real CAD corpus register & metadata audit (38 unique DWG drawings).
2. `RESEARCH_2_R4_DWG_001` — Native DWG/DXF source and benchmark program (object-level native reader verification with `ezdwg 0.11.0`, layer reliability study, failure mode corpus).
3. `RESEARCH_3_R4_PARSER_001` — Synthetic ParserBench & ground-truth verification suite.

The nested Tech Review package (`packages/RESEARCH_A_WAVE4_TECH_REVIEW_R1.zip`) embeds the three sealed worker research packages.

## Important Limitations and Governance Notice

- **Corpus Inventory Limitation:** The registered repository CAD corpus inventory represents candidate discovery and metadata classification, not fully adjudicated commercial quantity truth.
- **DWG Walkthrough Scope:** The three successful native object-level real-DWG walkthroughs prove reader capability on specific binary formats (AC1018, AC1032) and do not constitute universal AutoCAD format family compatibility.
- **Synthetic ParserBench Boundary:** Synthetic DXF fixture tests and independent transform oracle calculations are regression controls, not empirical production solver calibration or real-world takeoff accuracy metrics.
- **Reference-Only Evidence:** Accepted research does not authorize production code adoption, parser schema modification, or merge to `main`.
