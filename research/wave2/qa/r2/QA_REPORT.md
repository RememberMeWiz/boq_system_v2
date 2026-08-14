# Independent Research Wave 2 QA Report R2

## Verdict

```text
QA_PASS_WITH_NOTES
```

## Executive determination

The PM-authorized Wave 2 correction cycle closes the semantic-count and portability gates that caused `QA_RETURNED` in QA R1.

Independent QA did not accept the TL recount at face value. The corrected corpora were canonicalized again with reviewer-written rules, the correction datasets were sampled under the Research QA Charter, validators were rerun from clean extracted copies, correction-sensitive numerical fixtures were independently recomputed, and correction custody was reconciled against the prior R1 packet.

There is no remaining blocking QA-return condition.

## Returned hard gates

| Task / gate | Corrected raw | QA distinct | Required | Result |
|---|---:|---:|---:|---|
| COST-001 escalation | 60 | 60 | 40 | PASS |
| REBAR-001 fabrication | 134 | 110 | 100 | PASS |
| REBAR-001 cutting stock | 174 | 160 | 150 | PASS |
| REBAR-001 multi-diameter inventory | 40 subset rows | **22 strict** | 20 | PASS WITH NOTE |
| RISK-001 uncertainty | 88 | 88 | 80 | PASS |
| RISK-001 contingency | 46 | 46 | 40 | PASS |
| RISK-001 parser boundary | 58 | 58 | 50 | PASS |
| RISK-001 revision risk | 58 | 58 | 50 | PASS |
| RISK-001 release gates | 84 | 84 | 75 | PASS |
| RISK-002 parser/solver boundary | 36 | 36 | 30 | PASS |

### Multi-diameter note

The TL reports 26 distinct material bodies in the `MULTI_DIAMETER_INVENTORY` subset. QA applies a stricter phase interpretation: a multi-diameter problem must contain at least two distinct demand diameters.

Four corrected rows are single-diameter despite the subset label:

- `CS-QA-MD-023`
- `CS-QA-MD-033`
- `CS-QA-MD-034`
- `CS-QA-MD-038`

Excluding them leaves **22 genuinely multi-diameter distinct problems**, still above the required 20. The TL count is therefore not repeated as the strict QA count, but the gate remains closed.

## Semantic-diversity review

QA excluded IDs, origin labels, semantic-dimension annotations, and narrative-only text from the independent signatures.

For COST, exact dates/numbers were not allowed to create uniqueness by themselves. QA reduced them to chronology, sign, and meaningful ordering relationships. All 60 corrected escalation cases still remained distinct, even with source identity removed from the signature.

For RISK, `required_action` prose and similar narrative fields were excluded where the core state already encoded the problem. The six corrected RISK corpora still recount as **88 / 46 / 58 / 58 / 84 / 36 distinct**.

All 24 newly added REBAR fabrication cases and all 24 newly added cutting-stock cases were inspected at material-input level. The additions introduce different geometry, bend/hook/lap/coupler conditions, demand/stock mixes, objectives, kerf, grade compatibility, offcut/job-sequence states, alternatives, ties and infeasibility conditions rather than renamed IDs.

## Correction-sensitive independent recalculation

QA independently recomputed:

- COST-001 corrected escalation numeric fixtures: **33/33 matched**.
- REBAR-001 fabrication lengths: **134/134 matched**, including **24/24** new correction cases.

The original 150 REBAR cutting-stock inputs and their 150 optimum records are byte-for-byte unchanged by case ID. Therefore the QA-R1 independent **50/50 EXACT_SMALL** dynamic-programming result remains applicable.

The prior independent numerical results for frozen/unaffected work are also preserved:

- COST-002 normalization: **74/74**.
- ONTOLOGY-002 dimensional cases: **36/36**.
- REBAR-002 correction conservation: **50/50**, covering 1,285 stock bars and 3,800 fabricated pieces.
- RISK-001 reference BOQ: nine line amounts and **PHP 628,327.51** direct-cost total.
- RISK-002 fit summaries: **8/8**.
- RISK-002 eligible P10-P90 coverage: **70/96 = 72.9167%**.

## Validator and package integrity

All R2 correction packages are checksum-clean before review. QA reran the documented validators from separate clean copies.

- COST: both packaged validator entry points exit 0; 948 checks, 0 failures.
- REBAR: pre-integrity PASS, benchmark validator PASS, post-integrity PASS.
- RISK: outer correction validator 29/29 PASS; RISK-001 57/57 PASS; RISK-002 34/34 PASS.

Complete pre/post tree hashing found **zero changed, added, or removed files** in all three working copies.

This closes the COST/REBAR path-root defects and RISK sealed-file mutation problem returned/noted in QA R1.

## Source verification continuity

QA R1 independently verified 25 registered external sources, including 25 primary/official/technical sources for the sampled purpose.

R2 did not modify the COST-001, REBAR-001, RISK-001, or RISK-002 source registers: all four corrected `source_register.csv` files are byte-identical to their R1 versions. Under the PM-authorized narrow recheck, the prior external-source verification is therefore preserved rather than falsely represented as a new retrieval exercise.

## Custody and dependency control

- R2 TL package `SHA256SUMS.txt`: 15/15 entries verified.
- COST correction manifest: 43 entries verified.
- REBAR correction manifest: 77 entries verified.
- RISK correction outer manifest: 153 entries verified.
- Nested RISK-001 manifest: 79 entries verified.
- Nested RISK-002 manifest: 45 entries verified.
- Every frozen package hash and byte size in the R2 immutable reference register matches the actual package preserved in the R1 TL packet.

Independent path comparison confirms the correction stayed within the authorized areas. Unrelated/frozen evidence was not regenerated simply to obtain new timestamps.

## Notes retained

1. The strict REBAR multi-diameter count is 22, not the TL's 26, because four labeled rows contain only one demand diameter. This does not reopen the gate.
2. The frozen `R2-ONTOLOGY-002` package still carries the QA-R1 packaging-hygiene note concerning tracked Python bytecode and post-validator checksum mutation in a normal bytecode-writing environment. R2 was not authorized to reopen that accepted-with-notes package.
3. Worker-supplied validators remain self-consistency/reproducibility tools unless independently reproduced. Passing them is not treated as methodology adoption.
4. Research QA pass does not adopt rate policy, construction methodology, rebar procurement policy, risk appetite/percentiles, production schemas, or protected-standard interpretations.

## Final QA disposition

Wave 2 research now supports its own completion claims sufficiently for PM consideration:

```text
QA_PASS_WITH_NOTES
```

This authorizes **no production implementation, Git merge, Repository Steward action, methodology adoption, commercial policy, or structural-domain decision by itself**.
