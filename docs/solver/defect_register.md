# Solver Defect Register

**Task IDs:** S0-002, S0-003
**Repository branch:** `main`
**Source commit:** `97f16aa3fd7b6d8e7cd364b6edc2ac303a5f54e6`
**Scope:** evidence and proposed regression coverage only. No defect is corrected here.

## Classification rules

- **CONFIRMED:** supplied code, documentation, example, schema, or executable reproduction proves the stated mismatch.
- **NOT CONFIRMED:** the inspected evidence contradicts the suspicion.
- **INCONCLUSIVE:** current behavior is known, but supplied authorities conflict or do not establish the intended rule.
- **Critical:** a silent-success path can fabricate/omit a materially necessary result or persist an estimate unrelated to the input.
- **High:** likely material quantity/cost omission or distortion.
- **Medium:** bounded calculation, test, scope, provenance, or audit defect.
- **Low:** ambiguity/maintainability concern with no proven numerical error.

## Required ten-item investigation

| # | Investigation | Assessment | Register evidence |
|---:|---|---|---|
| 1 | Excavation working clearance described per side but added only once | **CONFIRMED** | DEF-001 |
| 2 | Parsed inputs may inherit sample-project values | **CONFIRMED** | DEF-002 |
| 3 | BOQ costs may use a sum of quantities with incompatible units | **CONFIRMED** | DEF-003 |
| 4 | Slab count may not be applied to slab concrete volume | **CONFIRMED** | DEF-004 |
| 5 | Concrete raw/net/waste/procurement states may be collapsed | **CONFIRMED** | DEF-005 |
| 6 | Unsupported rebar diameters may use a default unit weight | **CONFIRMED** | DEF-006 |
| 7 | Cuts longer than stock may remain unresolved without error | **CONFIRMED** | DEF-007 |
| 8 | Reinforcement tests may assert only positive output | **CONFIRMED** | DEF-008 |
| 9 | Rounding may occur before pricing | **CONFIRMED** | DEF-009 |
| 10 | Rates, formulas, and pricing may be coupled in one module | **CONFIRMED** | DEF-010 |

All ten requested suspicions are **CONFIRMED**. None of the ten is classified NOT CONFIRMED or INCONCLUSIVE.

## Register totals

| Dimension | Count |
|---|---:|
| Total findings | 29 |
| Confirmed | 25 |
| Not confirmed | 0 |
| Inconclusive | 4 |
| Critical | 3 |
| High | 11 |
| Medium | 14 |
| Low | 1 |

## Reproduction exhibits

| Exhibit | Current result | Reference/expected result |
|---|---|---|
| Section II handbook footing | 6.728 m3 excavation; 2.502 m3 backfill | 9.248 m3; 5.475 m3 per formula_exhaustive_handbook.md:55-69 |
| Section III slab count | count 1 = 10.0 m3; count 3 = 10.0 m3 | count should scale under the current public count contract |
| Section V test fixture | 40 bars = 109.47 kg | test docstring says 218.90 kg; solved case uses 80 bars |
| Unsupported 14 mm optimizer input | 6 m = 3.70 kg using 0.617 kg/m | d^2/162.2 gives about 7.25 kg |
| 13 m cut, 12 m maximum stock | required 20.51 kg; purchased 0.00 kg; no patterns/error | must be rejected/unresolved or explicitly spliced |
| One tempered-glass door | two complete sets are priced | stated allowance is 2 percent, not 100 percent |

## Detailed findings

### DEF-001 - Earthwork working clearance is applied once instead of once on each side

| Field | Finding |
|---|---|
| Defect ID | DEF-001 |
| Title | Earthwork working clearance is applied once instead of once on each side |
| Assessment | CONFIRMED |
| Severity | High |
| Affected function | calculate_section_2_earthworks |
| Affected outputs | excavation_m3, backfill_m3, earthwork cost, labor_manday, equipment_hours |
| Evidence | The function contract calls clearance_m a working clearance per side at backend/engine/fajardo.py:243-249, but excavation dimensions are L + clr and W + clr at lines 258-267. The handbook defines per-side clearance and its worked case uses 1.2 + 0.5 in both directions at formula_exhaustive_handbook.md:41-61. Reproduction of that case returns 6.728 m3 excavation and 2.502 m3 backfill instead of 9.248 m3 and 5.475 m3. |
| Expected behavior | For a clearance c measured on each side, use (L + 2c)(W + 2c)HN before calculating displaced volume and backfill. |
| Current behavior | Uses (L + c)(W + c)HN. |
| Possible business impact | Systematic undermeasurement of excavation, backfill, labor, equipment utilization, and cost. The handbook case is understated by 2.520 m3 of excavation and 2.973 m3 of backfill. |
| Recommended test | test_section_2_clearance_is_added_to_both_sides: use the handbook F-1 inputs and assert excavation_m3 == 9.248 and backfill_m3 == 5.475. |
| Proposed correction | Change the excavation dimensions to L + 2 * clr and W + 2 * clr after the regression test is approved. |
| Confidence level | High. Code, contract text, handbook formula, and executable reproduction agree on the mismatch. |

### DEF-002 - Parsed projects inherit quantities from SAMPLE_PROJECT_INPUTS

| Field | Finding |
|---|---|
| Defect ID | DEF-002 |
| Title | Parsed projects inherit quantities from SAMPLE_PROJECT_INPUTS |
| Assessment | CONFIRMED |
| Severity | Critical |
| Affected function | _schedules_to_project_inputs; process_drawing |
| Affected outputs | project_inputs and all Section II-XIII quantities/costs, persisted BOQ, API summary |
| Evidence | The adapter starts with deepcopy(SAMPLE_PROJECT_INPUTS) at backend/app.py:617-621. It clears only footing_specs, concrete elements, wall elements, and rebar elements at lines 623-627. Sample slab_area/slab_t and every Section VI-XIII input remain at lines 371-425. Empty or partial schedules therefore retain unrelated sample-project values. |
| Expected behavior | A parsed project should be built from an empty canonical input object. Missing trades should be zero, absent, or explicitly unresolved, never populated from a demo project unless demo mode was explicitly selected. |
| Current behavior | Every adapter call begins with the demo project, then selectively overwrites a small structural subset. |
| Possible business impact | A real drawing can receive phantom roofing, doors, tiles, painting, plumbing, electrical, mechanical, special works, slab bedding, and other costs. The result can be persisted and returned as a successful project estimate. |
| Recommended test | test_adapter_does_not_inherit_sample_project: pass empty schedules and a footings-only schedule, then assert no SAMPLE_PROJECT_INPUTS values appear in Sections II or VI-XIII. |
| Proposed correction | Initialize a blank project-input schema and move SAMPLE_PROJECT_INPUTS behind an explicit demo-only path. |
| Confidence level | High. The data copy and selective clearing are direct and deterministic. |

### DEF-003 - BOQ section cost is allocated through a sum of incompatible quantity units

| Field | Finding |
|---|---|
| Defect ID | DEF-003 |
| Title | BOQ section cost is allocated through a sum of incompatible quantity units |
| Assessment | CONFIRMED |
| Severity | High |
| Affected function | _takeoff_to_boq_rows |
| Affected outputs | BOQ material_unit_cost, labor_unit_cost, equipment_unit_cost, total_unit_cost, total_amount |
| Evidence | backend/app.py:478-484 sums every positive scalar in a section quantity dictionary into total_qty_sum, without regard to unit, then divides aggregate section cost by that sum. The same denominator can combine m3, m2, kg, liters, meters, pieces, counts, BTU, or tons. Lines 466-474 independently label each row with different units. |
| Expected behavior | Each BOQ line should carry its own measured quantity, unit, rate key/source, and extended cost. Quantities with different dimensions must never share one arithmetic allocation base. |
| Current behavior | All scalar quantities in a section receive the same artificial unit cost produced by aggregate cost divided by a mixed-unit sum. |
| Possible business impact | BOQ unit rates have no physical meaning, row amounts can misrepresent cost composition, and downstream comparison or procurement by item becomes unreliable even when the section total is arithmetically close. |
| Recommended test | test_boq_adapter_never_divides_cost_by_mixed_units: feed a synthetic section containing 1 m3 and 100 L with separate costs, then assert unit-specific rates and exact section reconciliation without a shared denominator. |
| Proposed correction | Emit canonical cost lines from the calculators and map those lines directly into BOQ rows. |
| Confidence level | High. The incompatible-unit denominator is explicit in code. |

### DEF-004 - Slab count is ignored in concrete volume

| Field | Finding |
|---|---|
| Defect ID | DEF-004 |
| Title | Slab count is ignored in concrete volume |
| Assessment | CONFIRMED |
| Severity | High |
| Affected function | calculate_section_3_concrete_and_formworks |
| Affected outputs | concrete_volume_m3, volume_by_class_m3, cement_bags, sand_m3, gravel_m3, labor, equipment, cost |
| Evidence | The function reads N = el.get("count", 1) at backend/engine/fajardo.py:338-342. Footing, column, and beam formulas multiply by N at lines 344-356, while the slab branch computes v = A * t at lines 357-360. Reproduction with identical 100 m2 by 0.10 m slabs returns 10.0 m3 for both count 1 and count 3. |
| Expected behavior | Slab volume should be A * t * N when area describes one repeated slab instance, or the input contract should prohibit count and require aggregate area. |
| Current behavior | The public contract accepts count but the slab formula discards it. |
| Possible business impact | Repeated floors or identical slab panels can be undercounted by a multiple, carrying the same error into materials, labor, equipment, and cost. |
| Recommended test | test_section_3_slab_count_scales_volume: with zero waste, assert count 1 returns 10.0 m3 and count 3 returns 30.0 m3. |
| Proposed correction | Apply N in the slab branch or remove count and enforce aggregate-area semantics after choosing one contract. |
| Confidence level | High. Direct code inspection and executable reproduction match. |

### DEF-005 - Concrete net, waste-adjusted, and procurement quantities are collapsed

| Field | Finding |
|---|---|
| Defect ID | DEF-005 |
| Title | Concrete net, waste-adjusted, and procurement quantities are collapsed |
| Assessment | CONFIRMED |
| Severity | High |
| Affected function | calculate_section_3_concrete_and_formworks; _takeoff_to_boq_rows; boq_items_v2 schema |
| Affected outputs | concrete_volume_m3, volume_by_class_m3, materials, BOQ quantity, persisted solver result |
| Evidence | backend/engine/fajardo.py:364-380 immediately adds waste and retains only total_volume and volume_by_class. Cement and plywood are then rounded up at lines 382-397. The handbook explicitly distinguishes net/gross, trade waste, and discrete rounding at formula_exhaustive_handbook.md:176-177. The solved footing case reports 3.60 m3 and 33 bags at sample_solved_cases.md:23-31, while the test treats 3.78 m3 and 35 bags as the same primary quantity at test_fajardo_v2.py:28-36. |
| Expected behavior | Retain at least net measured volume, waste allowance/rate, waste-adjusted order volume, and discrete procurement quantities as separate named states. |
| Current behavior | concrete_volume_m3 means waste-adjusted volume, and some material fields already mean rounded procurement quantity. No raw/net/procurement lineage survives. |
| Possible business impact | Reviewers cannot tell what was measured, what was added as waste, or what was rounded for purchase. Documentation, BOQ, and pricing can refer to different states using the same label. |
| Recommended test | test_section_3_preserves_quantity_states: for the 4-footing case assert net 3.60 m3, waste-adjusted 3.78 m3, and procurement cement 35 bags in distinct fields. |
| Proposed correction | Introduce explicit quantity-state fields without changing the approved formulas, then choose which state drives each price and BOQ row. |
| Confidence level | High. The missing states and document/test mismatch are directly observable. |

### DEF-006 - Unsupported rebar diameters silently use the 10 mm unit weight

| Field | Finding |
|---|---|
| Defect ID | DEF-006 |
| Title | Unsupported rebar diameters silently use the 10 mm unit weight |
| Assessment | CONFIRMED |
| Severity | High |
| Affected function | RebarStockOptimizer.optimize_diameter |
| Affected outputs | total_required_weight_kg, total_purchased_weight_kg, total_scrap_weight_kg |
| Evidence | backend/engine/rebar_optimizer.py:38-52 defines selected diameters and uses REBAR_UNIT_WEIGHTS.get(diameter_mm, 0.617). Therefore every unsupported diameter receives 0.617 kg/m, the 10 mm value. A 14 mm by 6 m cut is reported as 3.70 kg, while the engine formula d^2/162.2 in backend/engine/fajardo.py:63-65 gives about 7.25 kg. |
| Expected behavior | Reject unsupported diameters with a clear validation error, or derive unit weight from the same approved d^2/162.2 rule and record that derivation. |
| Current behavior | Unknown diameter values silently use 0.617 kg/m. |
| Possible business impact | Required and purchased weight, scrap weight, hauling, and any future price based on optimizer weight can be understated materially. |
| Recommended test | test_optimizer_rejects_or_correctly_derives_unsupported_diameter: pass 14 mm and assert either a validation exception or approximately 1.208 kg/m, never 0.617 kg/m. |
| Proposed correction | Remove the default constant and centralize diameter validation/unit-weight calculation. |
| Confidence level | High. The fallback and reproduction are unambiguous. |

### DEF-007 - Cuts longer than available stock disappear from procurement without an error

| Field | Finding |
|---|---|
| Defect ID | DEF-007 |
| Title | Cuts longer than available stock disappear from procurement without an error |
| Assessment | CONFIRMED |
| Severity | Critical |
| Affected function | RebarStockOptimizer.optimize_diameter; optimize_rebar API adapter |
| Affected outputs | purchased_bars, patterns, total_purchased_weight_kg, scrap_percentage, API status |
| Evidence | If no stock length can fit a remaining cut, backend/engine/rebar_optimizer.py:101-109 breaks the loop. The comment says split with lap splice, but no split or unresolved record is created. Lines 111-128 still calculate required weight from all cuts and purchased weight only from patterns. A 13 m 16 mm demand returns required 20.51 kg, purchased 0.0 kg, no patterns, zero scrap, and no error. backend/app.py:978-992 returns status success. |
| Expected behavior | Fail closed with an actionable overlength error, or apply an approved splice/split rule and expose the generated pieces, lap length, and added procurement. |
| Current behavior | The unresolved cut remains in required weight but vanishes from purchase patterns and is not surfaced. |
| Possible business impact | A cutting schedule can claim successful optimization while purchasing no steel for a required bar. This can create direct site shortage and structural fabrication risk. |
| Recommended test | test_optimizer_overlength_cut_is_never_silent: submit one 13 m cut with max stock 12 m and require either an exception/unresolved list or explicit splice patterns with positive purchased weight. |
| Proposed correction | Add validation before packing and a structured unresolved-demands result; implement lap splitting only after its engineering rule is approved. |
| Confidence level | High. The silent break and zero-purchase reproduction are definitive. |

### DEF-008 - The reinforcement worked-case test does not assert the documented result

| Field | Finding |
|---|---|
| Defect ID | DEF-008 |
| Title | The reinforcement worked-case test does not assert the documented result |
| Assessment | CONFIRMED |
| Severity | Medium |
| Affected function | test_section_5_rebar_footing_mat_worked_case |
| Affected outputs | Test confidence for Section V rebar_weight_kg |
| Evidence | test_fajardo_v2.py:38-49 names 218.90 kg in the docstring but asserts only rebar_weight_kg > 0. The fixture count is 40, while sample_solved_cases.md:63-73 derives 20 bars per footing times 4 footings, or 80 bars. Current output for the test fixture is 109.47 kg; 80 bars produces 218.94 kg using the exact d^2/162.2 formula. |
| Expected behavior | The fixture should represent the documented case and assert the approved numerical result within a stated tolerance. |
| Current behavior | Any positive weight passes, including approximately half the stated case. |
| Possible business impact | A major regression in bar count, hooks, cover, or unit weight can pass the existing suite. |
| Recommended test | test_section_5_rebar_footing_mat_exact_worked_case: use 80 bars and assert the approved result, with the expected value reconciled between rounded handbook table weight and exact formula weight. |
| Proposed correction | Fix the fixture and replace the positivity assertion only after the normative expected value is approved. |
| Confidence level | High. Test source and executable output directly prove the gap. |

### DEF-009 - Displayed rounded quantities are reused for pricing

| Field | Finding |
|---|---|
| Defect ID | DEF-009 |
| Title | Displayed rounded quantities are reused for pricing |
| Assessment | CONFIRMED |
| Severity | Medium |
| Affected function | Shared behavior across calculate_section_* functions and _cost_line |
| Affected outputs | Material, labor, equipment, and total costs |
| Evidence | Examples include concrete materials/volume rounded or ceiled before _cost_line at backend/engine/fajardo.py:377-397, earthwork quantities rounded before pricing at lines 282-294, and AC tons rounded to 2 decimals before pricing at lines 870-880. For a 1 m2 mechanical input, raw load is 0.058333 tons but 0.06 is priced, adding PHP 52.50 at the current material plus labor rate before other lines. |
| Expected behavior | Preserve high-precision calculation quantities, apply procurement rounding only to discrete purchase units, and round monetary output at the final currency stage. |
| Current behavior | Many display-rounded or procurement-rounded fields are the direct price basis, without labeling which rounding rule applies. |
| Possible business impact | Small distortions accumulate across many lines; early ceilings can also be intentional procurement effects but are indistinguishable from display rounding. |
| Recommended test | test_pricing_uses_raw_quantity_except_approved_procurement_rounding: use fractional continuous quantities and assert cost from unrounded values while discrete bags/pieces follow their explicit rule. |
| Proposed correction | Carry raw, display, and procurement quantities separately and select the price basis per line. |
| Confidence level | High for occurrence; medium for total materiality because impact depends on project scale and approved procurement rules. |

### DEF-010 - Rate constants, quantity formulas, and pricing behavior are coupled in one module

| Field | Finding |
|---|---|
| Defect ID | DEF-010 |
| Title | Rate constants, quantity formulas, and pricing behavior are coupled in one module |
| Assessment | CONFIRMED |
| Severity | Medium |
| Affected function | backend/engine/fajardo.py module; _rate; _cost_line; Sections II-XIII calculate_section_* functions; Section I general-requirements calculator |
| Affected outputs | All section quantities and direct costs |
| Evidence | The same module defines formula constants at backend/engine/fajardo.py:49-127, the illustrative DPWH_RATES table at lines 130-212, cost helpers at lines 215-230, and all section calculators at lines 241-1017. Sections II-XIII call module-global rate keys through the current pricing helpers. Section I is different: it uses percentage constants and a fixed permit amount directly. |
| Expected behavior | Quantity calculations should be testable independently of an injected, versioned rate source; rate changes should not require editing the formula module. |
| Current behavior | Formula logic and price lookup share global state and release/version boundaries. |
| Possible business impact | Rate refreshes risk calculation-code changes, quantity tests can accidentally depend on prices, and result provenance cannot identify which external rate set was used. |
| Recommended test | test_quantity_results_are_rate_source_independent: run identical inputs against two injected rate sets and assert identical quantities with only costs changing. |
| Proposed correction | Introduce a rate-provider boundary and immutable rate-set metadata in a later architecture task; do not change formulas in this task. |
| Confidence level | High. Module composition and direct calls are explicit. |

### DEF-011 - Footing BAR X and BAR Y schedules are collapsed to one direction

| Field | Finding |
|---|---|
| Defect ID | DEF-011 |
| Title | Footing BAR X and BAR Y schedules are collapsed to one direction |
| Assessment | CONFIRMED |
| Severity | High |
| Affected function | _schedules_to_project_inputs |
| Affected outputs | Section V rebar_elements and rebar_weight_kg for footing mats |
| Evidence | backend/app.py:672-687 reads one nested rebar object or selects f.get("BAR X") or f.get("BAR Y"). The first truthy direction wins. It emits one footing_mat item, multiplies one count by footing count, and always uses length_m rather than mapping the perpendicular run to width_m. |
| Expected behavior | Map BAR X and BAR Y independently, preserving each diameter, count/spacing derivation, direction, and corresponding run dimension. |
| Current behavior | At most one direction is represented and rectangular-footing width can be ignored. |
| Possible business impact | Footing reinforcement can be omitted by roughly one direction or assigned the wrong cut length, materially understating weight and cost. |
| Recommended test | test_adapter_maps_both_footing_bar_directions: use a 1.5 m by 2.0 m footing with distinct BAR X and BAR Y entries and assert two rebar groups with their correct counts and run lengths. |
| Proposed correction | Emit separate directional rebar elements after defining a canonical parser schedule shape. |
| Confidence level | High. The boolean-or selection and single append are direct. |

### DEF-012 - Beam and slab reinforcement schedules are not mapped into Section V

| Field | Finding |
|---|---|
| Defect ID | DEF-012 |
| Title | Beam and slab reinforcement schedules are not mapped into Section V |
| Assessment | CONFIRMED |
| Severity | High |
| Affected function | _schedules_to_project_inputs |
| Affected outputs | Section V rebar_elements, rebar_weight_kg, tie wire, reinforcement cost |
| Evidence | The beam loop at backend/app.py:762-772 appends only a concrete element. The slab loop at lines 774-783 also appends only concrete. Rebar mapping exists for footings and column main bars at lines 672-687 and 742-760, but there is no beam main/stirrup or slab-bar mapping in the adapter. |
| Expected behavior | Recognized beam and slab reinforcement schedules should create Section V inputs, or the adapter should flag them as unsupported/unresolved rather than omit them. |
| Current behavior | Parsed beam/slab reinforcement data has no path to the section calculator. |
| Possible business impact | A structural takeoff can omit major reinforcement categories while still returning success. |
| Recommended test | test_adapter_maps_or_rejects_beam_and_slab_rebar: provide parsed beam stirrups/main bars and slab bars, then assert Section V groups or explicit blocking issues. |
| Proposed correction | Add canonical beam/slab rebar mapping only after parser field authority and formulas are defined. |
| Confidence level | High within the inspected solver-facing adapter. |

### DEF-013 - Hardcoded geometry and class fallbacks contradict the adapter zero-hardcoding claim

| Field | Finding |
|---|---|
| Defect ID | DEF-013 |
| Title | Hardcoded geometry and class fallbacks contradict the adapter zero-hardcoding claim |
| Assessment | CONFIRMED |
| Severity | High |
| Affected function | _schedules_to_project_inputs |
| Affected outputs | Section II-V quantities and costs generated from incomplete parsed schedules |
| Evidence | The docstring states dimensions, counts, and rebar are derived dynamically at backend/app.py:605-615. The implementation substitutes footing 1.5 m by 1.5 m by 0.4 m at lines 643-662, column 0.40 m by 0.40 m and 3.20 m at lines 730-735, beam 250 mm by 400 mm by 4.50 m at lines 762-768, slab 120 m2 by 100 mm at lines 774-779, and wall 14 m by 3.20 m by 150 mm at lines 785-791. Concrete classes are also forced to A or B. |
| Expected behavior | Missing required dimensions/classes should remain unresolved or trigger validation. Defaults may be used only when the source contract explicitly defines them and they are labeled in the result. |
| Current behavior | Incomplete schedule rows become plausible positive geometry with no uncertainty marker. |
| Possible business impact | OCR/parser omissions can be transformed into fabricated but credible-looking quantities and costs. |
| Recommended test | test_adapter_missing_required_geometry_is_blocking: pass schedule rows with labels but no dimensions and assert no positive solver geometry is created and a structured issue is returned. |
| Proposed correction | Replace geometry fallbacks with required-field validation and source/provenance metadata. |
| Confidence level | High. The contradiction and literal defaults are explicit. |

### DEF-014 - A 2 percent tempered-glass door allowance can double small door counts

| Field | Finding |
|---|---|
| Defect ID | DEF-014 |
| Title | A 2 percent tempered-glass door allowance can double small door counts |
| Assessment | CONFIRMED |
| Severity | High |
| Affected function | calculate_section_7_doors_and_windows |
| Affected outputs | Tempered glass door procurement cost and Section VII total |
| Evidence | backend/engine/fajardo.py:663-675 multiplies installed tempered-glass door count by 1.02 and then applies math.ceil before pricing complete door sets. One installed door is therefore priced as two sets. With zero jamb and no windows, reproduction returns PHP 27,400, exactly two material and labor door-set rates. |
| Expected behavior | A 2 percent allowance should remain a separately visible allowance or use an approved project-level procurement rule that does not silently convert 2 percent into 100 percent for one door. |
| Current behavior | Every positive count below 50 receives at least one whole extra door set. |
| Possible business impact | Small projects can be materially overestimated; one door is doubled, ten doors receive an effective 10 percent quantity allowance. |
| Recommended test | test_tempered_door_allowance_does_not_double_one_set: assert one installed set remains one procurement set with a separately traceable 2 percent allowance under the approved policy. |
| Proposed correction | Separate installed count, waste/contingency allowance, and procurement count instead of ceiling count * 1.02. |
| Confidence level | High for the doubling behavior; medium-high for the preferred commercial treatment pending business approval. |

### DEF-015 - BOQ conversion ignores material dictionaries and Section I line items

| Field | Finding |
|---|---|
| Defect ID | DEF-015 |
| Title | BOQ conversion ignores material dictionaries and Section I line items |
| Assessment | CONFIRMED |
| Severity | High |
| Affected function | _takeoff_to_boq_rows |
| Affected outputs | BOQ rows, local/Supabase persistence, exported BOQ detail |
| Evidence | backend/app.py:454-460 reads mats but iterates only quantities. Nested quantity maps and basis_direct_cost are skipped at lines 460-462. Section I stores its priced components in line_items and only basis_direct_cost in quantities at backend/engine/fajardo.py:941-955, so it emits no BOQ row. Cement, sand, gravel, tie wire, rivets, pipe pieces, waterproofing, and other material fields are not emitted as their own lines. |
| Expected behavior | Every priced cost line should be represented or intentionally aggregated into a traceable BOQ item, including a Section I lump-sum breakdown. |
| Current behavior | Cost-bearing material/line-item fields disappear and their aggregate cost is smeared across surviving scalar quantity rows. |
| Possible business impact | The persisted/exported BOQ cannot be reconciled item by item to the solver, and major procurement lines can be absent despite being included in totals. |
| Recommended test | test_boq_rows_cover_all_priced_lines_and_section_1: run a known takeoff and assert Section I rows exist, concrete materials appear, and row amounts reconcile to every section total. |
| Proposed correction | Map canonical cost lines rather than traversing only the quantities dictionary. |
| Confidence level | High. The unused mats variable and absent line_items traversal are explicit. |

### DEF-016 - process_drawing converts parser/file failure into a successful sample-derived takeoff

| Field | Finding |
|---|---|
| Defect ID | DEF-016 |
| Title | process_drawing converts parser/file failure into a successful sample-derived takeoff |
| Assessment | CONFIRMED |
| Severity | Critical |
| Affected function | process_drawing |
| Affected outputs | HTTP status, input_source, project inputs, persisted BOQ/session, grand total |
| Evidence | If no file path resolves, backend/app.py:849-871 selects sample_structural_plan.pdf. If parsing raises, lines 873-881 replace the payload with {"schedules": {}}. Lines 883-897 label the source sample_defaults, call the sample-seeded adapter, run the solver, and continue. Lines 900-940 persist and return status success. This path is less strict than parser_ingest, which returns errors or marks sample fallback at lines 209-246. |
| Expected behavior | Production processing should fail or remain verification-blocked when the requested file cannot be parsed. Demo output must require an explicit demo action and must never be persisted as the requested project. |
| Current behavior | A parser exception or missing path can yield a positive, saved estimate built from demo defaults. |
| Possible business impact | Users can unknowingly approve and store an estimate unrelated to their drawing. |
| Recommended test | test_process_drawing_parse_failure_fails_closed: mock DrawingParserV2.parse to raise and assert non-success status, no solver call, and no local/cloud persistence. |
| Proposed correction | Remove implicit sample fallback from the production route and propagate a structured blocked/error state. |
| Confidence level | High. The complete silent-success path is visible in one function. |

### DEF-017 - Column clear-height authority conflicts across handbook, solved case, and adapter

| Field | Finding |
|---|---|
| Defect ID | DEF-017 |
| Title | Column clear-height authority conflicts across handbook, solved case, and adapter |
| Assessment | INCONCLUSIVE |
| Severity | Medium |
| Affected function | calculate_section_3_concrete_and_formworks; _schedules_to_project_inputs |
| Affected outputs | Column concrete volume, formwork, materials, and cost |
| Evidence | The handbook formula and Appendix B require Hstory - tfooting - tslab at formula_exhaustive_handbook.md:86-95 and 183-188. The solved case mentions a 0.40 m footing and 0.15 m slab but subtracts only 0.15 m at sample_solved_cases.md:35-44. The calculator trusts clear_height_m at backend/engine/fajardo.py:349-352, while the adapter defaults/sums 3.20 m story values without deductions at backend/app.py:734-740. |
| Expected behavior | Cannot be fixed safely until the authoritative measurement boundary is chosen for each story/location and the parser provides the required elevations or thicknesses. |
| Current behavior | Three sources encode different boundaries, and the adapter generally uses full story height. |
| Possible business impact | Columns may overlap footing/slab concrete or be under/overmeasured depending on which document a reviewer follows. |
| Recommended test | test_column_clear_height_authoritative_case: after approval, encode one case with explicit story, footing, and slab boundaries and assert both concrete and formwork. |
| Proposed correction | Resolve the source-of-truth conflict first, then make the adapter compute or validate clear_height_m explicitly. |
| Confidence level | High that the conflict exists; low on which formula is intended, therefore INCONCLUSIVE. |

### DEF-018 - Stirrup bend-shortening rule has conflicting approved-looking sources

| Field | Finding |
|---|---|
| Defect ID | DEF-018 |
| Title | Stirrup bend-shortening rule has conflicting approved-looking sources |
| Assessment | INCONCLUSIVE |
| Severity | Medium |
| Affected function | calculate_section_5_metals_and_rebar |
| Affected outputs | Beam stirrup cut length and rebar weight |
| Evidence | The handbook formula includes bend deduction at formula_exhaustive_handbook.md:128-132 and Appendix B quantifies 12db at lines 200-210. The solved stirrup case omits the deduction and reports 1.48 m at sample_solved_cases.md:77-86. The code documents the conflict and defaults apply_bend_deduction=False at backend/engine/fajardo.py:528-564. |
| Expected behavior | One fabrication authority must decide whether centerline dimensions already account for bend effects and whether the 12db deduction applies to this input convention. |
| Current behavior | Both modes exist, but the default follows the solved case rather than the handbook appendix. |
| Possible business impact | Stirrup weight can vary by 12db per stirrup, which compounds across high counts. |
| Recommended test | test_stirrup_cut_length_for_approved_dimension_convention: lock the approved 300 by 500 mm case and assert the selected result plus explicit mode metadata. |
| Proposed correction | Do not change the default until the dimension/bend convention is approved and documented consistently. |
| Confidence level | High on conflict and current behavior; insufficient evidence to select the correction. |

### DEF-019 - Masonry jamb-return area is multiplied by plaster face count

| Field | Finding |
|---|---|
| Defect ID | DEF-019 |
| Title | Masonry jamb-return area is multiplied by plaster face count |
| Assessment | CONFIRMED |
| Severity | Medium |
| Affected function | calculate_section_4_masonry_works |
| Affected outputs | plaster_area_m2, plaster cement/sand, plaster labor proxy, total cost |
| Evidence | backend/engine/fajardo.py:453-460 computes jamb_area, then uses (net_area + jamb_area) * plaster_faces. The handbook says calculate the return and add it to total plastering area at formula_exhaustive_handbook.md:223-228. For a two-face wall, current behavior adds two jamb returns. |
| Expected behavior | Under the handbook wording, plaster area is net wall area * faces + jamb return area once. |
| Current behavior | Both net wall area and jamb return are multiplied by faces. |
| Possible business impact | Openings overstate plaster materials and labor, with error increasing by number/perimeter of openings. |
| Recommended test | test_masonry_jamb_return_added_once: for a 10 m by 3 m, 150 mm wall with one 1 m by 2 m opening and two faces, assert 56.9 m2 rather than 57.8 m2. |
| Proposed correction | Move jamb_area outside the plaster_faces multiplication after confirming the handbook convention. |
| Confidence level | High relative to the current handbook wording. |

### DEF-020 - Plaster labor is priced using the painting labor rate

| Field | Finding |
|---|---|
| Defect ID | DEF-020 |
| Title | Plaster labor is priced using the painting labor rate |
| Assessment | CONFIRMED |
| Severity | Medium |
| Affected function | calculate_section_4_masonry_works |
| Affected outputs | Section IV labor cost and total cost |
| Evidence | backend/engine/fajardo.py:483-488 calls _cost_line(plaster_area_m2, "paint_labor_m2") and labels it a generic plaster labor proxy. DPWH_RATES contains no dedicated plaster labor key in lines 136-212. |
| Expected behavior | Use an approved masonry/plaster labor analysis with its own unit, source, and version, or explicitly disclose the proxy in result provenance. |
| Current behavior | Painting labor price is silently included in masonry cost. |
| Possible business impact | Section IV labor cost may be materially wrong and cannot be traced to an appropriate pay item. |
| Recommended test | test_masonry_plaster_uses_approved_rate_key: inspect emitted cost lines and assert a dedicated plaster rate/provenance rather than paint_labor_m2. |
| Proposed correction | Add a mapped plaster rate through the approved rate source; retain the proxy only as an explicit flagged fallback if authorized. |
| Confidence level | High. The proxy is directly named in source. |

### DEF-021 - DUPA-loaded rates are disconnected from solver pricing

| Field | Finding |
|---|---|
| Defect ID | DEF-021 |
| Title | DUPA-loaded rates are disconnected from solver pricing |
| Assessment | CONFIRMED |
| Severity | High |
| Affected function | DUPARateLoader.load_rates; get_dupa_qa; _rate; Sections II-XIII section calculators |
| Affected outputs | Sections II-XIII direct costs, downstream Section I/grand-total costs, and rate provenance |
| Evidence | DUPARateLoader reads workbook values at backend/engine/dupa_loader.py:16-89. backend/app.py:359-362 exposes only a QA summary. Sections II-XIII solver pricing calls the static DPWH_RATES dictionary through backend/engine/fajardo.py:136-222. Section I does not use DPWH_RATES; it applies percentage constants and a fixed permit amount directly to the Sections II-XIII subtotal. No inspected solver path maps loaded DUPA items to the Section II-XIII rate keys. The handbook says illustrative rates should be replaced in production at formula_exhaustive_handbook.md:6-8. |
| Expected behavior | The active calculation should use a selected, versioned project/DUPA rate set or explicitly identify that placeholder rates are in use. |
| Current behavior | DUPA may load successfully while Sections II-XIII calculations continue using hardcoded illustrative rate-table values; Section I continues using its percentage constants and fixed permit amount directly. |
| Possible business impact | A result can appear DPWH-backed but use unrelated placeholder rates, causing broad cost error and provenance failure. |
| Recommended test | test_solver_uses_selected_dupa_rate_set: inject a fixture rate with a unique sentinel value and assert the matching cost line uses it and records source/version. |
| Proposed correction | Create an explicit rate mapping/provider boundary in a later task and block production pricing when only placeholders are available unless acknowledged. |
| Confidence level | High for the inspected files and call graph. |

### DEF-022 - Undocumented surrogate quantities create plumbing and electrical cost lines

| Field | Finding |
|---|---|
| Defect ID | DEF-022 |
| Title | Undocumented surrogate quantities create plumbing and electrical cost lines |
| Assessment | CONFIRMED |
| Severity | Medium |
| Affected function | calculate_section_10_plumbing_works; calculate_section_11_electrical_works |
| Affected outputs | 2-inch UPVC pieces, catch-basin cost, LED panel cost, breaker cost, section totals |
| Evidence | backend/engine/fajardo.py:790-813 assumes 2-inch sanitary length is 50 percent of the 4-inch run and always prices one catch basin. Lines 830-847 infer LED panels as ceil(outlets/3) and always price one breaker. The handbook scopes these trades at formula_exhaustive_handbook.md:156-163 but does not define these surrogate ratios/counts, and the public functions accept no actual counts for them. |
| Expected behavior | Use parsed/manual schedules for each cost-bearing item, or mark missing quantities unresolved. Any estimation heuristic must be explicit, configurable, and provenance-tagged. |
| Current behavior | Four positive cost lines are synthesized from unrelated inputs or fixed quantity one. |
| Possible business impact | Projects can be charged for absent items or undercharged for actual circuits, fixtures, drainage, and distribution layouts. |
| Recommended test | test_sections_10_11_do_not_invent_unprovided_items: pass zero/independent inputs and assert catch basins, 2-inch lines, LED fixtures, and breakers require explicit quantities or flagged heuristics. |
| Proposed correction | Add explicit inputs and remove unconditional/surrogate costing after the input schema is approved. |
| Confidence level | High that the behavior is undocumented in the supplied formula sources. |

### DEF-023 - Installed, waste-adjusted, and procurement quantities use inconsistent field semantics

| Field | Finding |
|---|---|
| Defect ID | DEF-023 |
| Title | Installed, waste-adjusted, and procurement quantities use inconsistent field semantics |
| Assessment | CONFIRMED |
| Severity | Medium |
| Affected function | Multiple section calculators and _takeoff_to_boq_rows |
| Affected outputs | Quantity/material fields, pricing basis, procurement interpretation |
| Evidence | Concrete_volume_m3 already includes waste while cement_bags and marine_ply_sheets are procurement-ceiled at backend/engine/fajardo.py:364-397. Roof and ceiling area fields include lap/waste at lines 609-630. Tempered door count stays installed in quantities but a hidden ceiled waste count is priced at lines 663-675. Pipe materials are whole pieces at lines 790-810, while tile quantities remain fractional waste-adjusted m2 at lines 695-717. The handbook calls for distinct net/gross, waste, and discrete rounding rules at formula_exhaustive_handbook.md:176-177. |
| Expected behavior | Every result should identify measurement state and unit consistently, with procurement transformations represented as separate traceable fields. |
| Current behavior | The same dictionary layers mix installed, waste-adjusted, hidden, and rounded procurement meanings. |
| Possible business impact | BOQ and purchasing code cannot reliably choose the correct quantity, and reviewers may compare unlike states. |
| Recommended test | test_all_cost_lines_declare_quantity_state: inspect every emitted cost line and require raw/net, waste-adjusted, or procurement state plus unit and rounding rule. |
| Proposed correction | Define a canonical quantity-state model in a later architecture task, preserving current formulas during migration. |
| Confidence level | High. Cross-section field semantics are directly observable. |

### DEF-024 - Persistence schema cannot store formula, rate, or quantity-state trace

| Field | Finding |
|---|---|
| Defect ID | DEF-024 |
| Title | Persistence schema cannot store formula, rate, or quantity-state trace |
| Assessment | CONFIRMED |
| Severity | Medium |
| Affected function | boq_items_v2, backup_computations, boq_checklist, boq_sessions_v2 schemas |
| Affected outputs | Persisted BOQ audit trail and reproducibility |
| Evidence | schema/boq_v2_schema.sql:44-75 and 98-122 store flattened quantity, unit, component unit costs, amount, and status. There are no fields for formula ID/version, input snapshot/hash, source line, raw/net/waste/procurement states, waste rate, rounding rule, rate key/source/version, warnings, or unresolved optimizer demand. Rebar schedule storage at lines 77-86 likewise has no unresolved-cuts field. |
| Expected behavior | Persist enough immutable calculation and rate provenance to reproduce a result and explain every transformation. |
| Current behavior | Only final flattened values survive in the solver-result tables. |
| Possible business impact | Later audits cannot determine why a number changed, which placeholder/live rate was used, or whether a quantity included waste/procurement rounding. |
| Recommended test | test_persisted_result_round_trips_calculation_trace: save a known result and assert formula/version, input snapshot, rate source, quantity states, and warnings can be reconstructed. |
| Proposed correction | Extend result persistence in a later schema task after the canonical trace format is approved. |
| Confidence level | High. Required trace fields are absent from the supplied schema. |

### DEF-025 - Productivity outputs and labor/equipment pricing may represent unrelated models

| Field | Finding |
|---|---|
| Defect ID | DEF-025 |
| Title | Productivity outputs and labor/equipment pricing may represent unrelated models |
| Assessment | INCONCLUSIVE |
| Severity | Low |
| Affected function | All calculate_section_* functions returning labor_manday/equipment_hours |
| Affected outputs | labor_manday, equipment_hours versus cost.labor/equipment |
| Evidence | Calculators derive productivity indicators with hardcoded divisors, for example earthwork at backend/engine/fajardo.py:296-304 and concrete at lines 399-406, while cost labor/equipment comes independently from per-unit DPWH_RATES via _cost_line. No code reconciles hours/days with wage/equipment rates. |
| Expected behavior | If productivity fields are intended as the cost basis, they should reconcile. If they are informational planning metrics, the result should say so and carry separate provenance. |
| Current behavior | Both models coexist with no declared relationship. |
| Possible business impact | Users may assume mandays/hours explain the priced labor/equipment when they do not. |
| Recommended test | test_productivity_cost_relationship_matches_declared_policy: once policy is chosen, assert reconciliation or explicit informational-only metadata. |
| Proposed correction | Clarify the contract before changing formulas; this is not proven numerically wrong. |
| Confidence level | High on independence, insufficient evidence on intended relationship, therefore INCONCLUSIVE. |

### DEF-026 - Core calculators lack validation for invalid geometry and counts

| Field | Finding |
|---|---|
| Defect ID | DEF-026 |
| Title | Core calculators lack validation for invalid geometry and counts |
| Assessment | CONFIRMED |
| Severity | Medium |
| Affected function | Multiple calculate_section_* functions; run_full_takeoff |
| Affected outputs | Potential negative, infinite, nonsensical quantities/costs or runtime failures |
| Evidence | No shared validation occurs before run_full_takeoff dispatch at backend/engine/fajardo.py:1001-1007. Masonry permits net_area = gross - openings - stiffeners without a lower bound at lines 441-451. Roofing divides by cos(pitch) at lines 606-611 with no pitch range check. Counts/lengths are generally accepted directly, and unknown/missing keys fail inconsistently. |
| Expected behavior | Validate finite nonnegative dimensions, positive/whole counts, supported classes/thicknesses, valid pitch range, and physically consistent openings before calculating. |
| Current behavior | Invalid parser/manual values may become negative quantities, extreme quantities, misleading zeroes, or unstructured exceptions. |
| Possible business impact | Bad upstream extraction can contaminate totals or crash only partway through processing, with no uniform field-level error report. |
| Recommended test | test_solver_rejects_invalid_geometry_consistently: parameterize negative dimensions/counts, openings larger than wall, NaN/inf, and pitch near 90 degrees; assert structured validation errors. |
| Proposed correction | Add a validation boundary before section execution, not ad hoc clamps that hide source problems. |
| Confidence level | High. Absence of validation and concrete invalid paths are visible. |

### DEF-027 - Slab soffit formwork scope is unresolved

| Field | Finding |
|---|---|
| Defect ID | DEF-027 |
| Title | Slab soffit formwork scope is unresolved |
| Assessment | INCONCLUSIVE |
| Severity | Medium |
| Affected function | calculate_section_3_concrete_and_formworks |
| Affected outputs | formwork_contact_area_m2, plywood, lumber, formwork labor and cost for slabs |
| Evidence | The slab branch sets area = 0.0 and comments that slab soffit formwork is typically shored but not tallied at backend/engine/fajardo.py:357-360. The handbook scope includes slabs and gives formwork formulas for footings, columns, and beams at formula_exhaustive_handbook.md:73-96, but it does not provide a slab-soffit formula or explicitly exclude it. |
| Expected behavior | The project measurement standard must state whether suspended slab soffit/edge forms are included, excluded, or measured elsewhere, and distinguish slab-on-grade. |
| Current behavior | All slab types receive zero formwork. |
| Possible business impact | Suspended-slab formwork may be omitted, but the supplied references do not conclusively establish intended scope. |
| Recommended test | test_slab_formwork_for_approved_slab_types: after scope approval, assert zero for slab-on-grade and the defined soffit/edge rule for suspended slabs. |
| Proposed correction | Add an explicit slab subtype and approved formwork rule only after scope is resolved. |
| Confidence level | High on current zero behavior; insufficient authority on intended behavior, therefore INCONCLUSIVE. |

### DEF-028 - BOQ backup quantity is an undocumented fixed 97 percent of computed quantity

| Field | Finding |
|---|---|
| Defect ID | DEF-028 |
| Title | BOQ backup quantity is an undocumented fixed 97 percent of computed quantity |
| Assessment | CONFIRMED |
| Severity | Medium |
| Affected function | _takeoff_to_boq_rows |
| Affected outputs | backup_qty in every BOQ row |
| Evidence | backend/app.py:486-500 sets backup_qty = qty_val * 0.97 and comments that the engineer estimate is approximately 97 percent of computed. No supplied handbook, solved case, test, or input defines this factor or distinguishes it by trade. |
| Expected behavior | Backup/engineer quantity should come from an independent source or an explicit configurable comparison rule with provenance, not a universal derivative of the value it is supposed to check. |
| Current behavior | Every backup value is mechanically three percent lower than the computed quantity. |
| Possible business impact | The field creates a false appearance of independent verification and guarantees a predetermined variance. |
| Recommended test | test_backup_quantity_requires_independent_source: assert the adapter does not synthesize backup_qty when no engineer estimate is provided. |
| Proposed correction | Leave backup_qty null/unavailable until an independent estimate is supplied. |
| Confidence level | High. The fixed transformation and lack of source are explicit. |

### DEF-029 - Concrete solved case and baseline test disagree on waste inclusion

| Field | Finding |
|---|---|
| Defect ID | DEF-029 |
| Title | Concrete solved case and baseline test disagree on waste inclusion |
| Assessment | CONFIRMED |
| Severity | Medium |
| Affected function | sample_solved_cases.md Case 1.1; test_section_3_footing_concrete_worked_case; calculate_section_3_concrete_and_formworks |
| Affected outputs | Expected concrete volume and cement bags for the canonical footing case |
| Evidence | sample_solved_cases.md:23-31 derives 3.60 m3 and 33 bags with no waste. formula_exhaustive_handbook.md:86-90 prescribes 5 percent site-mixed or 3 percent ready-mix. test_fajardo_v2.py:28-36 calls the same geometry a handbook worked case but expects 3.78 m3 and 35 bags using default 5 percent. The implementation returns the test values. |
| Expected behavior | The canonical case should explicitly state net volume, mixing method, waste-adjusted quantity, and procurement bags, with all sources using the same labels. |
| Current behavior | The solved case labels the net result as total, while the test labels the waste-adjusted result as the worked-case volume. |
| Possible business impact | Developers can “fix” code toward either document and still believe they are following the baseline; quantity-state confusion is reinforced. |
| Recommended test | test_concrete_canonical_case_net_waste_procurement: assert all three named states in one test instead of choosing one unlabeled total. |
| Proposed correction | Reconcile the documents after adding explicit quantity states; do not silently overwrite either baseline in this task. |
| Confidence level | High. The numerical/document mismatch is direct. |

## Assumptions versus proven defects

The four INCONCLUSIVE findings are not authorized corrections. DEF-017 and DEF-018 have conflicting formula authorities. DEF-025 may be an intentional separation between planning productivity and direct-cost rates. DEF-027 depends on whether the slab is suspended or on grade and on the project measurement standard. They require a business/engineering decision before code changes.

Confirmed findings state observable current behavior and its mismatch with a supplied source, declared contract, unit rule, or fail-safe expectation. Proposed corrections are hypotheses for a later task, not implementation decisions made here.

## Suggested correction order

1. Block sample-derived production output and overlength optimizer success: DEF-002, DEF-007, DEF-016.
2. Protect major quantities and BOQ integrity: DEF-001, DEF-003, DEF-004, DEF-005, DEF-011, DEF-012, DEF-015.
3. Establish rate and trace provenance: DEF-010, DEF-021, DEF-024.
4. Resolve quantity-state, rounding, and procurement semantics: DEF-009, DEF-014, DEF-023, DEF-028, DEF-029.
5. Resolve conflicting authorities before touching formulas: DEF-017, DEF-018, DEF-025, DEF-027.
