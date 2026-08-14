# Research A/B Cross-Team Interface Rules R2

## Worker identity

Workers remain:

```text
Research 1
Research 2
Research 3
Research 4
Research 5
Research 6
```

A/B identifies TL and QA lanes only.

## Default routing

```text
Research 1/2/3 → Research A TL → Research A QA
Research 4/5/6 → Research B TL → Research B QA
```

## Primary-owner examples

| Topic | Primary lane | Consulted lane |
|---|---|---|
| PDF/DWG corpus acquisition | A | B for competitor-use cases |
| Parser accuracy metrics | A | B for UX burden metrics |
| visual evidence localization | A | B for review UX |
| standards/source authority | A | B when commercial adoption matters |
| quantity ontology | A | B when BOQ classification matters |
| pricing/rate engine | B | A for units/ontology interfaces |
| competitor study | B | A for technical benchmark metrics |
| estimator UX | B | A for evidence constraints |
| process efficiency | B | A where technical gates are affected |
| global measurement standards | A | B for market implications |
| global pricing/tax/currency | B | A for canonical-unit interfaces |

## Cross-lane reassignment

PM may assign any Research 1-6 worker to either lane for a specific task.

Worker name does not change.

The assigned primary TL/QA route governs that task.

## No duplicate-worker rule

Do not duplicate the same research question across workers unless PM explicitly authorizes adversarial replication.

## PM arbitration

PM owns:
- routing disputes;
- conflicting recommendations;
- sequencing;
- adoption/defer/reject decisions.
