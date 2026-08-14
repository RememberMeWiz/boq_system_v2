# Contradiction Review — Wave 2 QA R2

## R1 blocking contradictions

The R1 QA return identified completion claims that contradicted the distinct-case evidence. The R2 corrections close those contradictions under an independent recount:

- COST-001 escalation: 60 distinct, minimum 40.
- REBAR-001 fabrication: 110 distinct, minimum 100.
- REBAR-001 cutting stock: 160 distinct, minimum 150.
- REBAR-001 strict multi-diameter inventory: 22 distinct, minimum 20.
- RISK-001 uncertainty / contingency / parser-boundary / revision / release gates: 88 / 46 / 58 / 58 / 84 distinct.
- RISK-002 parser/solver boundary: 36 distinct, minimum 30.

## QA note against TL wording

The TL reports 26 distinct cases in the `MULTI_DIAMETER_INVENTORY` subset. QA finds four of those rows contain only one distinct demand diameter:

- `CS-QA-MD-023`
- `CS-QA-MD-033`
- `CS-QA-MD-034`
- `CS-QA-MD-038`

QA therefore does not repeat the TL's 26 as the strict multi-diameter count. The strict count is 22 and still passes the required minimum of 20. This discrepancy is nonblocking but is preserved as a QA note.

## Cross-research reconciliation

The correction does not resolve or adopt the outstanding policy/domain decisions identified by the TL. Rate precedence, structural approval for splice/coupler alternatives, procurement objective hierarchy, offcut valuation, contingency percentile/risk appetite, exact production schema adoption, and protected-standard reliance remain outside QA adoption authority.

The RISK governance example `CON-021` remains a policy-decision example, not authority for production behavior.

No correction-sensitive contradiction was found that invalidates the prior independently reproduced arithmetic or the narrow R2 closure.

## Result

`NO_BLOCKING_CORRECTION_SENSITIVE_CONTRADICTION`

The appropriate verdict is `QA_PASS_WITH_NOTES`.
