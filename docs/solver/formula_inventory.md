# Current Solver Formula Inventory

**Task IDs:** S0-002, S0-003
**Repository branch:** `main`
**Source commit:** `97f16aa3fd7b6d8e7cd364b6edc2ac303a5f54e6`
**Inventory scope:** current behavior only. No formula correction or new architecture is implemented here.

## Inventory accounting

This document treats a public calculator or solver-boundary rule as one inventory entry, then enumerates every atomic mathematical rule inside that entry. The inventory contains **20 formula/rule groups**, including **all 13 public `calculate_section_*` functions**. It also covers the shared rate/cost rule, unit-weight helper, full-takeoff orchestrator, parser adapter, BOQ adapter, rebar optimizer, and DUPA rate loader because those boundaries materially change quantities, units, procurement, or price.

Confidence labels separate confidence in observed implementation from confidence in the intended estimating rule. A high implementation confidence does not mean the business rule is correct.

## Public calculator coverage

| Section | Public function | Source |
|---:|---|---|
| I | `calculate_section_1_general_requirements` | `backend/engine/fajardo.py:934-956` |
| II | `calculate_section_2_earthworks` | `backend/engine/fajardo.py:241-306` |
| III | `calculate_section_3_concrete_and_formworks` | `backend/engine/fajardo.py:313-408` |
| IV | `calculate_section_4_masonry_works` | `backend/engine/fajardo.py:415-499` |
| V | `calculate_section_5_metals_and_rebar` | `backend/engine/fajardo.py:506-599` |
| VI | `calculate_section_6_roofing_and_ceiling` | `backend/engine/fajardo.py:606-642` |
| VII | `calculate_section_7_doors_and_windows` | `backend/engine/fajardo.py:649-688` |
| VIII | `calculate_section_8_tile_and_flooring` | `backend/engine/fajardo.py:695-728` |
| IX | `calculate_section_9_painting_works` | `backend/engine/fajardo.py:735-783` |
| X | `calculate_section_10_plumbing_works` | `backend/engine/fajardo.py:790-823` |
| XI | `calculate_section_11_electrical_works` | `backend/engine/fajardo.py:830-857` |
| XII | `calculate_section_12_sanitary_mechanical` | `backend/engine/fajardo.py:864-891` |
| XIII | `calculate_section_13_special_works` | `backend/engine/fajardo.py:898-927` |

## Detailed inventory

### TMP-S01 - `calculate_section_1_general_requirements`

| Field | Current behavior |
|---|---|
| Temporary formula ID | TMP-S01 |
| Current function | calculate_section_1_general_requirements |
| File and line range | backend/engine/fajardo.py:934-956 |
| Trade and element type | Section I - General requirements; project-level indirect items |
| Purpose | Price mobilization, temporary facilities, safety/PPE, and permits from the Sections II-XIII direct-cost base. |
| Required inputs | sections_2_to_13_direct_cost |
| Optional inputs and defaults | None. Percentages and permit lot are module constants. |
| Input units | PHP direct-cost subtotal. |
| Output fields and units | quantities.basis_direct_cost [PHP]; line_items.* [PHP]; cost.material/labor/equipment/total [PHP]; labor_manday [day]; equipment_hours [hour]. |
| Mathematical rule | base = input; mobilization = 0.010 x base; temporary facilities = 0.015 x base; safety = 0.0075 x base; permits = PHP 18,500; total = sum of rounded line items. |
| Rounding stage | Each line item is rounded to 2 decimals before the total is summed and rounded. |
| Waste allowance | None. |
| Procurement rule | Permits are a fixed lot. Other items are percentage allowances, not measured procurement quantities. |
| Rate dependency | Uses GENREQ_* constants in fajardo.py:123-127. It does not query DUPA or a project rate source. |
| Handbook reference | formula_exhaustive_handbook.md:12-32. Values match the worked example percentages and permit lot. |
| Solved-case reference | No separate case in sample_solved_cases.md. |
| Test coverage | No direct test. test_fajardo_v2.py:51-73 only verifies Section I exists and grand total exceeds the II-XIII subtotal. |
| Current confidence | High for current implementation behavior; medium for project applicability because all percentages are global constants. |
| Unresolved assumptions | No location, project size, remote-site factor, statutory headcount, or actual LGU fee schedule is accepted. BOQ conversion currently skips basis_direct_cost and line_items, so this section produces no normal BOQ row (DEF-015). |

### TMP-S02 - `calculate_section_2_earthworks`

| Field | Current behavior |
|---|---|
| Temporary formula ID | TMP-S02 |
| Current function | calculate_section_2_earthworks |
| File and line range | backend/engine/fajardo.py:241-306 |
| Trade and element type | Section II - Earthworks; isolated footing excavation, backfill, bedding, soil treatment |
| Purpose | Calculate earthwork quantities, materials, productivity indicators, and direct cost. |
| Required inputs | footing_specs; slab_area; slab_t. Each footing needs length_m, width_m, depth_m, count. |
| Optional inputs and defaults | clearance_m defaults to 0.25 m per footing. slab_t is accepted but deliberately unused. |
| Input units | Lengths/depths/clearance [m]; areas [m2]; count [integer]. |
| Output fields and units | excavation_m3, backfill_m3, gravel_bedding_m3 [m3]; soil_poisoning_l [L]; gravel_m3 [m3]; soil_poison_l [L]; labor_manday [day]; equipment_hours [hour]; cost [PHP]. |
| Mathematical rule | For each footing: exc_L = L + clearance; exc_W = W + clearance; Vexc = exc_L x exc_W x H x N; Vfoot = L x W x H x N; footprint = L x W x N. Totals: Vbackfill = (sum Vexc - sum Vfoot) x 1.18; bedding = footing footprint x 0.10 + slab_area x 0.05; poison area = footing footprint + slab_area; poison = area x 5 L/m2; labor = excavation/3.5 + backfill/4; equipment = excavation/6. |
| Rounding stage | Quantities are rounded first (3 decimals for volumes, 2 for liters), then those rounded quantities are priced. Labor and equipment outputs round to 2 decimals. |
| Waste allowance | Backfill uses 18% shrinkage/loose-fill allowance. No excavation bulking factor. |
| Procurement rule | Bedding and chemical are continuous quantities; no truckload/container rounding. |
| Rate dependency | excavation_m3, backfill_m3, gravel_bedding_m3, soil_poison_l from DPWH_RATES at fajardo.py:148-151. |
| Handbook reference | formula_exhaustive_handbook.md:36-69. The handbook defines clearance per side and its case uses L + 2c and W + 2c. |
| Solved-case reference | No Section II case in sample_solved_cases.md. |
| Test coverage | Only exercised inside test_fajardo_v2.py:51-73; no earthwork quantity assertion. |
| Current confidence | High that the implementation is inventoried; high that clearance behavior conflicts with the handbook. |
| Unresolved assumptions | The treatment footprint, 100 mm footing bedding, 50 mm slab bedding, and productivity rates are global. slab_t has no effect. Clearance is applied once rather than twice (DEF-001). |

### TMP-S03 - `calculate_section_3_concrete_and_formworks`

| Field | Current behavior |
|---|---|
| Temporary formula ID | TMP-S03 |
| Current function | calculate_section_3_concrete_and_formworks |
| File and line range | backend/engine/fajardo.py:313-408 |
| Trade and element type | Section III - Concrete and formwork; footings, columns, beams, slabs |
| Purpose | Calculate waste-adjusted concrete, class-based mix materials, formwork materials, productivity indicators, and cost. |
| Required inputs | elements list. Per element: type plus geometry required by that type. |
| Optional inputs and defaults | class defaults A; count defaults 1; wastage defaults 0.05; footing depth falls through depth_m, height_m, then 0.40 m. |
| Input units | Geometry [m, m2]; count [integer]; wastage [fraction]. |
| Output fields and units | concrete_volume_m3 and volume_by_class_m3 [m3]; formwork_contact_area_m2 [m2]; cement_bags [bag]; sand_m3/gravel_m3 [m3]; marine_ply_sheets [sheet]; form_lumber_bdft [board foot]; labor/equipment; cost [PHP]. |
| Mathematical rule | Footing V=LWHN and form=2(L+W)HN; column V=wdHcN and form=2(w+d)HcN; beam V=wdLcN and form=(w+2d)LcN; slab V=A x t and form=0. For every type, Vwaste=V(1+wastage). Mix materials = Vwaste x class factors. Plywood=form area x 0.28; lumber=form area x 7.0. Labor=concrete/4 + form/8; equipment=concrete/5. |
| Rounding stage | Only waste-adjusted volume is retained. Output volume and aggregates round to 3 decimals; cement and plywood ceil to integer; lumber to 2 decimals. Rounded outputs are priced. |
| Waste allowance | Per-element, default 5%. Handbook also mentions 3% ready-mix, but the app adapter never sets it. |
| Procurement rule | Cement bags and plywood sheets round up. Sand, gravel, and lumber remain continuous. No ready-mix truck increment. |
| Rate dependency | cement_bag, sand_m3, gravel_m3, concrete_labor_m3, marine_ply_sheet, form_lumber_bdft from static DPWH_RATES. |
| Handbook reference | formula_exhaustive_handbook.md:73-96 and 183-196. |
| Solved-case reference | sample_solved_cases.md:23-44 and 123-130. The sample footing case reports net 3.60 m3 and 33 bags, while current code/test apply 5% and return 3.78 m3 and 35 bags. |
| Test coverage | Direct exact assertions only for one footing case at test_fajardo_v2.py:28-36. Slab count, other element types, formwork, class mix, and quantity-state separation are untested. |
| Current confidence | High for behavior; low-to-medium for business correctness where net, gross, waste-adjusted, and procurement quantities are not separated. |
| Unresolved assumptions | Slab count is ignored (DEF-004). Slab soffit formwork is zero. Column and beam inputs are assumed already net. Concrete quantity states are collapsed (DEF-005). |

### TMP-S04 - `calculate_section_4_masonry_works`

| Field | Current behavior |
|---|---|
| Temporary formula ID | TMP-S04 |
| Current function | calculate_section_4_masonry_works |
| File and line range | backend/engine/fajardo.py:415-499 |
| Trade and element type | Section IV - CHB masonry and plaster |
| Purpose | Calculate net wall area effects, CHB, mortar, plaster, jamb returns, productivity, and cost. |
| Required inputs | wall_elements with length_m, height_m, thickness_mm. |
| Optional inputs and defaults | openings=[]; stiffener_area_m2=0; plaster_faces=2. |
| Input units | Length [m], area [m2], thickness [mm], faces/count [integer]. |
| Output fields and units | chb_count and chb_by_thickness [pc]; plaster_area_m2 [m2]; mortar/plaster cement [bag] and sand [m3]; labor_manday; cost [PHP]. |
| Mathematical rule | gross=L x H; openings=sum(width x height); net=gross-openings-stiffeners; CHB=net x 12.5; mortar=net x thickness factor; jamb=sum(2(w+h)twall); plaster=(net+jamb) x faces; plaster materials=plaster area x factors; labor=CHB/150 + plaster/10. |
| Rounding stage | Total and per-thickness CHB ceil independently. Plaster area rounds 3 decimals; material outputs round before pricing; combined cement is ceiled for cost but that procurement total is not returned. |
| Waste allowance | No CHB breakage, mortar waste, or plaster waste factor. |
| Procurement rule | CHB and total cement used for pricing are rounded up. Returned cement components remain fractional. Sand remains continuous. |
| Rate dependency | CHB rate selected by thickness; cement_bag and sand_m3; plaster labor is priced with paint_labor_m2 as a proxy. |
| Handbook reference | formula_exhaustive_handbook.md:100-116 and 223-232. |
| Solved-case reference | sample_solved_cases.md:95-130. |
| Test coverage | Only full-pipeline smoke coverage at test_fajardo_v2.py:51-73; no exact masonry assertions. |
| Current confidence | High for current code; medium for jamb-return interpretation and low for the painting-rate labor proxy. |
| Unresolved assumptions | No validation prevents negative net area. Jamb return is multiplied by plaster_faces although the handbook says add the return once to total plaster area (DEF-019). |

### TMP-S05 - `calculate_section_5_metals_and_rebar`

| Field | Current behavior |
|---|---|
| Temporary formula ID | TMP-S05 |
| Current function | calculate_section_5_metals_and_rebar |
| File and line range | backend/engine/fajardo.py:506-599 |
| Trade and element type | Section V - Reinforcing bars and structural steel |
| Purpose | Calculate installed rebar weight from cut lengths, tie wire, structural steel, productivity, and cost. |
| Required inputs | rebar_elements. Every item needs diameter_mm and count; geometry depends on member type. |
| Optional inputs and defaults | structural_steel_kg=0; member=generic; footing cover=0.075; column dowel=0; stirrup cover=0.040; bend deduction=False; multiple geometry fallbacks exist. |
| Input units | Diameter [mm], lengths [m], count [integer], steel [kg]. |
| Output fields and units | rebar_weight_kg and by diameter [kg]; structural_steel_kg [kg]; tie_wire_kg [kg]; labor_manday; cost [PHP]. |
| Mathematical rule | Unit weight=d^2/162.2. Footing cut=max(0.5, L-2cover+2(12db)); column cut=H+40db+dowel; stirrup cut=2(w-2c)+2(d-2c)+2(10db)-optional 12db; generic cut=input length. Weight=cut x count x unit weight; tie wire=1.5% of rebar; labor=rebar/250. |
| Rounding stage | Rebar/steel/tie wire round to 2 decimals and then are priced. No procurement stock rounding occurs here. |
| Waste allowance | No cutting, lap-stock, splice, or fabrication waste in section cost. Tie wire is 1.5%. |
| Procurement rule | Returns installed weight only. The stock optimizer is separate and not called by run_full_takeoff. |
| Rate dependency | rebar_kg, tie_wire_kg, structural_steel_kg from static DPWH_RATES. |
| Handbook reference | formula_exhaustive_handbook.md:120-132 and 200-219. |
| Solved-case reference | sample_solved_cases.md:48-91. Footing case expects 80 cuts across four footings and about 218.90 kg. Stirrup case omits bend deduction. |
| Test coverage | test_fajardo_v2.py:38-49 names 218.90 kg but passes only 40 cuts and asserts >0; current result is about 109.47 kg. |
| Current confidence | High for implementation; medium for stirrup authority because handbook and solved case disagree. |
| Unresolved assumptions | A 0.5 m minimum footing cut is undocumented. The parser adapter can omit one footing direction and all beam/slab reinforcement (DEF-011, DEF-012). |

### TMP-S06 - `calculate_section_6_roofing_and_ceiling`

| Field | Current behavior |
|---|---|
| Temporary formula ID | TMP-S06 |
| Current function | calculate_section_6_roofing_and_ceiling |
| File and line range | backend/engine/fajardo.py:606-642 |
| Trade and element type | Section VI - Roofing and ceiling |
| Purpose | Calculate roof slope/lap area, rivets, ceiling waste area, furring, productivity, and cost. |
| Required inputs | roof_plan_area, pitch_deg, ceiling_area. |
| Optional inputs and defaults | None; constants provide 12% roof lap, 5% ceiling waste, 26 rivets/m2, 2.5 m furring/m2. |
| Input units | Areas [m2], pitch [degrees]. |
| Output fields and units | roof_slope_area_m2, ceiling_area_m2 [m2]; metal_furring_m [m]; roofing_rivets_pcs [pc]; labor_manday; cost [PHP]. |
| Mathematical rule | theta=radians(pitch); raw slope=plan/cos(theta); roofing=raw x 1.12; rivets=roofing x 26; ceiling procurement area=ceiling x 1.05; furring=ceiling x 2.5; labor=roofing/15+ceiling/12. |
| Rounding stage | Areas round to 3 decimals, furring to 2, rivets ceil; rounded values are priced. |
| Waste allowance | 12% roof lap and 5% Hardiflex waste. |
| Procurement rule | Rivets round up. Roofing and ceiling remain fractional m2; no sheet dimension/layout rounding. |
| Rate dependency | longspan_roofing_m2, rivet_pc, hardiflex_m2, metal_furring_m. Purlin and GI strap rates exist but are not used. |
| Handbook reference | formula_exhaustive_handbook.md:136-137 and 251-255. |
| Solved-case reference | None. |
| Test coverage | Only full-pipeline smoke coverage; no exact section assertion. |
| Current confidence | High for current math; medium for completeness because purlins, trusses, straps, trims, and sheet layout are omitted. |
| Unresolved assumptions | Pitch is valid and cos(theta) is nonzero. Rivets are based on lap-adjusted area. No input validation or commercial sheet procurement rule. |

### TMP-S07 - `calculate_section_7_doors_and_windows`

| Field | Current behavior |
|---|---|
| Temporary formula ID | TMP-S07 |
| Current function | calculate_section_7_doors_and_windows |
| File and line range | backend/engine/fajardo.py:649-688 |
| Trade and element type | Section VII - Doors and windows |
| Purpose | Price windows, door sets, jamb lumber, and installation productivity. |
| Required inputs | windows_sqm, doors list with type and count. |
| Optional inputs and defaults | jamb_lumber_bdft_each defaults to 8.0. |
| Input units | Window area [m2], door count [integer], lumber [board foot/set]. |
| Output fields and units | windows_m2 [m2], door_counts [set], jamb_lumber_bdft [bd.ft], labor_manday, cost [PHP]. |
| Mathematical rule | Aggregate door counts; jamb lumber=sum(count x bdft_each); tempered procurement=ceil(tempered count x 1.02); labor=all door sets/4 + windows/8. |
| Rounding stage | Window area and lumber round to 2 decimals before pricing. Tempered door waste is ceiled to a whole set. |
| Waste allowance | 2% only on tempered-glass door set count. |
| Procurement rule | Door sets are integer; windows are fractional m2; jamb lumber is continuous. Applying 2% then ceil adds at least one whole door for every nonzero count. |
| Rate dependency | aluminum_window_m2, tempered_glass_door_set, panel_door_set, flush_door_set, jamb_lumber_bdft. |
| Handbook reference | formula_exhaustive_handbook.md:141-142. |
| Solved-case reference | None. |
| Test coverage | Only full-pipeline smoke coverage. The test uses panel doors only. |
| Current confidence | High that the current tempered-door rule is materially distortive for small counts. |
| Unresolved assumptions | Unknown door types are accumulated for labor but are not priced. The meaning of 2% waste for a prefabricated door set is unresolved (DEF-014). |

### TMP-S08 - `calculate_section_8_tile_and_flooring`

| Field | Current behavior |
|---|---|
| Temporary formula ID | TMP-S08 |
| Current function | calculate_section_8_tile_and_flooring |
| File and line range | backend/engine/fajardo.py:695-728 |
| Trade and element type | Section VIII - Tile and flooring |
| Purpose | Calculate tile order area, mortar bed, grout, productivity, and cost. |
| Required inputs | floor_area, wall_area. |
| Optional inputs and defaults | is_diagonal=False. |
| Input units | Areas [m2]. |
| Output fields and units | floor_tile_area_m2 and wall_tile_area_m2 [m2]; mortar_bed_bags [bag]; tile_grout_kg [kg]; labor_manday; cost [PHP]. |
| Mathematical rule | Floor waste=15% diagonal else 8%; floor procurement=floor x (1+waste); wall procurement=wall x 1.08; mortar=floor x 0.24 bag/m2; grout=(floor+wall) x 0.40 kg/m2; labor=(floor+wall)/8. |
| Rounding stage | Tile areas round 3 decimals; mortar and grout round 2 before pricing. |
| Waste allowance | 8% standard, 15% diagonal floor; wall fixed at 8%. |
| Procurement rule | Tile is billed as fractional m2; mortar bags are fractional, not ceiled; no tile-size/carton layout rule. |
| Rate dependency | floor_tile_m2, wall_tile_m2, tile_mortar_bed_bag, tile_grout_kg. |
| Handbook reference | formula_exhaustive_handbook.md:146-147 and 241-242. |
| Solved-case reference | None. |
| Test coverage | Only full-pipeline smoke coverage. |
| Current confidence | High for implementation; medium for wall-tile bedding and procurement completeness. |
| Unresolved assumptions | Mortar bed is calculated only for floor area. No adhesive/bedding rule for wall tile. Discrete bag procurement is not represented. |

### TMP-S09 - `calculate_section_9_painting_works`

| Field | Current behavior |
|---|---|
| Temporary formula ID | TMP-S09 |
| Current function | calculate_section_9_painting_works |
| File and line range | backend/engine/fajardo.py:735-783 |
| Trade and element type | Section IX - Painting |
| Purpose | Calculate coating liquids, labor area, and cost for masonry, ceilings, and metal. |
| Required inputs | masonry_area, ceiling_area, metal_area. |
| Optional inputs and defaults | is_rough_chb=False. |
| Input units | Areas [m2]. |
| Output fields and units | surface quantities [m2]; neutralizer, primer, topcoat, ceiling latex, metal primer/enamel [L]; labor_manday; cost [PHP]. |
| Mathematical rule | Neutralizer=masonry/10; primer=masonry/(6.25 rough or 10 smooth); topcoat=2 x masonry/8; ceiling latex=ceiling/8; metal primer=metal/8; metal enamel=metal/9; labor area=masonry+ceiling+metal; labor=area/20. |
| Rounding stage | Every liquid rounds to 2 decimals before pricing; labor cost uses unrounded total area. |
| Waste allowance | No application loss or container waste. Rough CHB changes primer coverage only. |
| Procurement rule | Liters remain fractional. No gallon/can packaging or round-up. |
| Rate dependency | neutralizer_l, primer_l, topcoat_l, ceiling_latex_l, metal_primer_l, metal_enamel_l, paint_labor_m2. |
| Handbook reference | formula_exhaustive_handbook.md:151-152 and 244-245. |
| Solved-case reference | None. |
| Test coverage | Only full-pipeline smoke coverage. |
| Current confidence | High for current coverage arithmetic; low-to-medium for coat/packaging completeness. |
| Unresolved assumptions | Neutralizer always uses smooth coverage even for rough CHB. Ceiling and metal coat counts are implicit. No procurement packaging. |

### TMP-S10 - `calculate_section_10_plumbing_works`

| Field | Current behavior |
|---|---|
| Temporary formula ID | TMP-S10 |
| Current function | calculate_section_10_plumbing_works |
| File and line range | backend/engine/fajardo.py:790-823 |
| Trade and element type | Section X - Plumbing |
| Purpose | Convert sanitary/water runs to commercial pipe pieces, add fixtures/catch basin, productivity, and cost. |
| Required inputs | sanitary_run_m, water_run_m, fixtures_count. |
| Optional inputs and defaults | None. Constants: 3 m pipe, 10% allowance. |
| Input units | Run lengths [m], fixtures [set]. |
| Output fields and units | runs [m], fixture count; UPVC 4-inch, UPVC 2-inch, and PPR [pc]; labor_manday; cost [PHP]. |
| Mathematical rule | 4in pcs=ceil((sanitary/3) x 1.10); 2in pcs=ceil((sanitary x 0.5/3) x 1.10); PPR=ceil((water/3) x 1.10); catch basin=1 lot; labor=(sanitary+water)/20 + fixtures/2. |
| Rounding stage | Runs round 2 decimals for output only; pieces ceil. Cost uses integer pieces, raw fixture count, and one lot. |
| Waste allowance | 10% fittings allowance is converted into extra pipe pieces. |
| Procurement rule | 3 m commercial pipe pieces are rounded up. Fixtures are sets. Exactly one catch basin is always procured. |
| Rate dependency | upvc_4in_pc, upvc_2in_pc, ppr_pipe_pc, fixture_set, catch_basin_lot. |
| Handbook reference | formula_exhaustive_handbook.md:156-157. |
| Solved-case reference | None. |
| Test coverage | Only full-pipeline smoke coverage. |
| Current confidence | High for current code; low for undocumented 50% 2-inch split and fixed catch basin. |
| Unresolved assumptions | No pipe diameter schedule, fitting count, septic vault quantity, or catch-basin input exists (DEF-022). |

### TMP-S11 - `calculate_section_11_electrical_works`

| Field | Current behavior |
|---|---|
| Temporary formula ID | TMP-S11 |
| Current function | calculate_section_11_electrical_works |
| File and line range | backend/engine/fajardo.py:830-857 |
| Trade and element type | Section XI - Electrical |
| Purpose | Estimate wire, conduit, outlets, derived lighting, one breaker, productivity, and cost. |
| Required inputs | outlets_count, homerun_m. |
| Optional inputs and defaults | None. Constants: 12% wire slack, 3 m conduit. |
| Input units | Count [unit], run [m]. |
| Output fields and units | wire_m [m], conduit_pcs [pc], outlets_count [unit], labor_manday, cost [PHP]. LED and breaker counts are cost-only and not returned. |
| Mathematical rule | wire=homerun x 1.12; conduit=ceil(homerun/3); LED panels=ceil(outlets/3); breaker=1; labor=wire/60 + outlets/8. |
| Rounding stage | Wire rounds 2 decimals before pricing; conduit and LED ceil. |
| Waste allowance | 12% wire slack. No conduit allowance. |
| Procurement rule | Conduit/LED/breaker are discrete. Wire is fractional meters. |
| Rate dependency | thhn_wire_m, pvc_conduit_pc, outlet_pc, led_panel_pc, breaker_pc. |
| Handbook reference | formula_exhaustive_handbook.md:161-162. |
| Solved-case reference | None. |
| Test coverage | Only full-pipeline smoke coverage. |
| Current confidence | High for current implementation; low for business validity of LEDs-per-outlet and one-breaker surrogate. |
| Unresolved assumptions | No conductor count, wire size, circuit grouping, lighting input, or breaker load sizing. Cost-only derived quantities are absent from output (DEF-022). |

### TMP-S12 - `calculate_section_12_sanitary_mechanical`

| Field | Current behavior |
|---|---|
| Temporary formula ID | TMP-S12 |
| Current function | calculate_section_12_sanitary_mechanical |
| File and line range | backend/engine/fajardo.py:864-891 |
| Trade and element type | Section XII - Sanitary/mechanical; split AC |
| Purpose | Estimate cooling load, continuous tonnage, refrigerant piping, commissioning, productivity, and cost. |
| Required inputs | room_area_m2, pipe_run_m. |
| Optional inputs and defaults | None. Constants: 700 BTU/h/m2 and 10% copper allowance. |
| Input units | Area [m2], pipe run [m]. |
| Output fields and units | cooling_load_btu [BTU/h], acu_tons [ton], copper_piping_m [m], labor_manday, cost [PHP]. |
| Mathematical rule | BTU=area x 700; tons=BTU/12,000; copper=run x 1.10; commissioning=1 lot; labor=copper/15 + 1. |
| Rounding stage | BTU, tons, and copper round to 2 decimals; rounded tons/copper are priced. |
| Waste allowance | 10% copper piping allowance. |
| Procurement rule | AC tonnage remains fractional and is not mapped to available unit capacities; commissioning is always one lot. |
| Rate dependency | acu_unit_per_ton, copper_piping_m, commissioning_lot. |
| Handbook reference | formula_exhaustive_handbook.md:166-167. |
| Solved-case reference | None. |
| Test coverage | Only full-pipeline smoke coverage. |
| Current confidence | High for arithmetic; low for equipment procurement realism. |
| Unresolved assumptions | No climate, occupancy, solar gain, room count, standard AC sizes, or zero-work suppression for commissioning. |

### TMP-S13 - `calculate_section_13_special_works`

| Field | Current behavior |
|---|---|
| Temporary formula ID | TMP-S13 |
| Current function | calculate_section_13_special_works |
| File and line range | backend/engine/fajardo.py:898-927 |
| Trade and element type | Section XIII - Handrails, ACP, waterproofing |
| Purpose | Apply ACP waste and waterproofing consumption, then price special works. |
| Required inputs | handrail_m, acp_m2, waterproofing_m2. |
| Optional inputs and defaults | None. |
| Input units | Length [m], areas [m2]. |
| Output fields and units | handrail_m [m], acp_cladding_m2 [m2], waterproofing_m2 [m2], waterproofing_kg [kg], labor_manday, cost [PHP]. |
| Mathematical rule | ACP procurement=area x 1.08; waterproofing material=area x 1.2 kg/m2; labor=handrail/10 + raw ACP/8 + waterproofing/25. |
| Rounding stage | All returned quantities round 2 decimals and those rounded quantities are priced. |
| Waste allowance | 8% ACP cutting waste. Waterproofing consumption is fixed at 1.2 kg/m2. |
| Procurement rule | No ACP panel layout or waterproofing pail rounding. |
| Rate dependency | handrail_m, acp_cladding_m2, waterproofing_kg, waterproofing_labor_m2. |
| Handbook reference | formula_exhaustive_handbook.md:171-172. |
| Solved-case reference | None. |
| Test coverage | Only full-pipeline smoke coverage. |
| Current confidence | High for current implementation; medium for product-specific consumption/packaging. |
| Unresolved assumptions | No number of coats, panel dimensions, joint waste, or pail size input. |

### TMP-U01 - `rebar_unit_weight_kg_per_m`

| Field | Current behavior |
|---|---|
| Temporary formula ID | TMP-U01 |
| Current function | rebar_unit_weight_kg_per_m |
| File and line range | backend/engine/fajardo.py:63-65 |
| Trade and element type | Cross-cutting reinforcement helper |
| Purpose | Compute theoretical mass per meter from nominal diameter. |
| Required inputs | diameter_mm. |
| Optional inputs and defaults | None. |
| Input units | Diameter [mm]. |
| Output fields and units | Unit weight [kg/m]. |
| Mathematical rule | W=d^2/162.2. |
| Rounding stage | None inside helper. Callers round final weights. |
| Waste allowance | None. |
| Procurement rule | None. |
| Rate dependency | No rate. Used by Section V only, not by the optimizer table lookup. |
| Handbook reference | formula_exhaustive_handbook.md:125-126. |
| Solved-case reference | sample_solved_cases.md:50-59. Table values are rounded to 3 decimals. |
| Test coverage | Indirectly exercised; no direct diameter/value test. |
| Current confidence | High. |
| Unresolved assumptions | Nominal diameter is positive and in millimeters. Section V accepts any diameter, while the optimizer has a finite table and a silent fallback. |

### TMP-COST01 - `_rate, _cost_line, _sum_costs`

| Field | Current behavior |
|---|---|
| Temporary formula ID | TMP-COST01 |
| Current function | _rate, _cost_line, _sum_costs |
| File and line range | backend/engine/fajardo.py:136-230 |
| Trade and element type | Cross-cutting pricing |
| Purpose | Resolve static component rates, multiply quantity by material/labor/equipment rates, and total section cost. |
| Required inputs | rate key and quantity. |
| Optional inputs and defaults | None. Missing key raises KeyError. |
| Input units | Quantity unit must match the rate key; rate [PHP per unit]. |
| Output fields and units | material, labor, equipment, total [PHP]. |
| Mathematical rule | component cost=(q x material rate, q x labor rate, q x equipment rate); section components=sum each axis; total=sum axes. |
| Rounding stage | _sum_costs rounds each axis and total to 2 decimals. Most callers pass quantities already rounded. |
| Waste allowance | Inherited from caller quantity. |
| Procurement rule | Inherited from caller. |
| Rate dependency | DPWH_RATES static dictionary in the same module. Values are labeled illustrative placeholders. Sections II-XIII use this rate table through the current pricing helpers; Section I instead uses its percentage constants and fixed permit amount directly. |
| Handbook reference | formula_exhaustive_handbook.md:6-8. |
| Solved-case reference | Section II handbook case has illustrative rates; other sample cases focus on quantities. |
| Test coverage | Only indirect through section tests. No rate-source, unit compatibility, or precision test. |
| Current confidence | High that formulas, rates, and pricing are coupled in one module (DEF-010). |
| Unresolved assumptions | Every key has correct unit semantics. DUPA loader output is not injected. Rounding policy is not centrally declared. |

### TMP-ORCH01 - `run_full_takeoff`

| Field | Current behavior |
|---|---|
| Temporary formula ID | TMP-ORCH01 |
| Current function | run_full_takeoff |
| File and line range | backend/engine/fajardo.py:963-1017 |
| Trade and element type | All 13 sections; orchestration |
| Purpose | Execute Sections II-XIII, compute Section I from their subtotal, and return grand total. |
| Required inputs | project_inputs with keyword dictionaries for every section 2-13. |
| Optional inputs and defaults | Dictionary lookup defaults missing section to {}, but most calculators then raise TypeError because required arguments are absent. |
| Input units | Section-specific. |
| Output fields and units | sections map; sections_2_to_13_subtotal [PHP]; grand_total_direct_cost [PHP]. |
| Mathematical rule | For n=2..13, result_n=fn(**project_inputs[n]); subtotal=sum(result_n.cost.total); section1=general_requirements(subtotal); grand=subtotal+section1.total. |
| Rounding stage | Each section cost is already rounded; subtotal and grand total round to 2 decimals. |
| Waste allowance | Section-specific. |
| Procurement rule | Section-specific; optimizer is not invoked. |
| Rate dependency | Sections II-XIII pricing uses static DPWH_RATES through the current pricing helpers. Section I uses the GENREQ_* percentage constants and fixed permit amount directly; it does not price through DPWH_RATES. |
| Handbook reference | formula_exhaustive_handbook.md:6-8 and Section I:12-32. |
| Solved-case reference | No complete 13-trade solved case. |
| Test coverage | test_fajardo_v2.py:51-73 checks keys and positive relationships, not exact section totals. |
| Current confidence | High for orchestration. |
| Unresolved assumptions | All sections are mandatory. It does not carry formula IDs, rate versions, warnings, unresolved optimizer cuts, or calculation trace. |

### TMP-ADAPT01 - `_schedules_to_project_inputs`

| Field | Current behavior |
|---|---|
| Temporary formula ID | TMP-ADAPT01 |
| Current function | _schedules_to_project_inputs |
| File and line range | backend/app.py:605-805 |
| Trade and element type | Parser-to-solver adapter |
| Purpose | Normalize extracted footing/column/beam/slab/wall schedules into Section II-V solver input dictionaries while preserving a full 13-section template. |
| Required inputs | schedules dictionary. |
| Optional inputs and defaults | Numerous parser fields; missing values fall back to hardcoded dimensions/counts/classes. Non-dict input returns a deep copy of the sample project. |
| Input units | Mixed parser shapes; millimeters are heuristically converted when values exceed 20. |
| Output fields and units | project_inputs keyed 2-13. |
| Mathematical rule | Starts with deepcopy(SAMPLE_PROJECT_INPUTS); clears only Section II footing list and Sections III-V element lists; maps parsed items; retains Section II slab_area/slab_t and all Section VI-XIII sample values. Columns group by mark and sum per-row clear heights; defaults include 1.5 m footings, 0.4 m depth/columns, 3.2 m story, 250x400 mm beams, 4.5 m span, 120 m2 slabs, and sample trade values. |
| Rounding stage | Some mm-to-m conversions round to 3 decimals. |
| Waste allowance | No waste field is mapped, so concrete defaults to 5%. |
| Procurement rule | No procurement mapping. |
| Rate dependency | No rate. |
| Handbook reference | No adapter rule in formula handbook. It claims a zero-hardcoding policy in its docstring, but current fallbacks are hardcoded. |
| Solved-case reference | No adapter solved case. |
| Test coverage | No tests. |
| Current confidence | High that parsed inputs can inherit sample values and hardcoded defaults (DEF-002, DEF-013). |
| Unresolved assumptions | Missing parser data is treated as quantity data rather than uncertainty. Footing BAR X/BAR Y handling, beam rebar, slab rebar, openings, and nonstructural trades are incomplete. |

### TMP-BOQ01 - `_takeoff_to_boq_rows`

| Field | Current behavior |
|---|---|
| Temporary formula ID | TMP-BOQ01 |
| Current function | _takeoff_to_boq_rows |
| File and line range | backend/app.py:446-504 |
| Trade and element type | Section result to BOQ presentation/persistence adapter |
| Purpose | Flatten section quantity dictionaries into frontend/database BOQ rows and proportionally allocate section cost. |
| Required inputs | run_full_takeoff result. |
| Optional inputs and defaults | Unknown sections get generic prefix/name. |
| Input units | Mixed section quantities plus PHP cost. |
| Output fields and units | Rows with quantity/unit, material/labor/equipment/total unit cost, total amount, backup_qty, status. |
| Mathematical rule | For each scalar quantity, total_qty_sum=sum(all positive scalar quantities regardless unit); each component unit rate=section component cost/total_qty_sum; row total=quantity x total unit rate; backup_qty=quantity x 0.97. Nested quantity maps and basis_direct_cost are skipped. Materials are not iterated. |
| Rounding stage | Quantity/unit rates round to 4 decimals; row amount to 2; backup to 4. |
| Waste allowance | Whatever is embedded in quantity; state is not labeled. |
| Procurement rule | Material dictionary is ignored, so procurement items do not become rows. |
| Rate dependency | Uses section aggregate cost, not the original rate key or item-level rate. |
| Handbook reference | Conflicts with the handbook principle of unit-specific costing and direct-cost line items at formula_exhaustive_handbook.md:6-8 and 176-177. |
| Solved-case reference | No BOQ-row solved case. |
| Test coverage | No tests. |
| Current confidence | High that incompatible units are summed and cost is smeared across them (DEF-003). |
| Unresolved assumptions | Scalar quantities are treated as a common allocation base. Section I line items, cement, sand, gravel, tie wire, paint, pipe, and cost-only derived items can disappear or be misrepresented. |

### TMP-OPT01 - `RebarStockOptimizer.optimize_diameter`

| Field | Current behavior |
|---|---|
| Temporary formula ID | TMP-OPT01 |
| Current function | RebarStockOptimizer.optimize_diameter |
| File and line range | backend/engine/rebar_optimizer.py:46-129 |
| Trade and element type | Rebar procurement/cutting stock |
| Purpose | Pack cut demands into 6/9/12 m bars using a First Fit Decreasing-like best-stock pass and report weight/scrap. |
| Required inputs | diameter_mm and demands list of required_length_m, quantity, element_ref. |
| Optional inputs and defaults | stock_lengths defaults [12,9,6]. Unsupported diameter silently defaults to 0.617 kg/m. |
| Input units | Diameter [mm], cut/stock lengths [m], quantity [integer]. |
| Output fields and units | required/purchased/scrap weight [kg], scrap percentage, purchased bars by length, cut patterns. |
| Mathematical rule | Expand cuts, sort descending. For each new pattern, greedily fit remaining cuts into every stock length, choose candidate with least scrap, remove its cuts, repeat. Metrics=sum cut/stock/scrap lengths x unit weight; scrap%=scrap/purchased. |
| Rounding stage | Pattern utilization rounds 2 decimals; final weights and scrap percent round 2. |
| Waste allowance | Scrap is computed. No kerf. No lap-splice rule is actually implemented. |
| Procurement rule | Whole bars by stock length. |
| Rate dependency | No pricing. Uses a separate hardcoded unit-weight table. |
| Handbook reference | formula_exhaustive_handbook.md:125-132 and 200-210. |
| Solved-case reference | sample_solved_cases.md provides bar unit weights but no cutting-stock solution. |
| Test coverage | test_fajardo_v2.py:76-86 checks one feasible 20 mm case has <5% scrap and purchased weight > required. |
| Current confidence | High for current behavior; high that unsupported diameters and overlength cuts fail silently (DEF-006, DEF-007). |
| Unresolved assumptions | All demand lengths are positive, no cut exceeds max stock, demand diameter matches method diameter, kerf is zero, and bar price is independent of stock length. |

### TMP-RATE01 - `DUPARateLoader.load_rates`

| Field | Current behavior |
|---|---|
| Temporary formula ID | TMP-RATE01 |
| Current function | DUPARateLoader.load_rates |
| File and line range | backend/engine/dupa_loader.py:16-89 |
| Trade and element type | Rate ingestion/QA boundary |
| Purpose | Scan a residential DUPA workbook and extract material/labor/equipment/total unit costs by sheet. |
| Required inputs | Workbook at configured residential path. |
| Optional inputs and defaults | Cache after first load. Roads workbook path exists but is not read. |
| Input units | Workbook-defined PHP/unit. |
| Output fields and units | Dictionary per sheet with component and total unit costs plus source label. |
| Mathematical rule | For each non-excluded sheet, scan rows. If a label contains total/unit cost terms, take the last positive numeric cell; similarly for material/labor/equipment. Total=explicit total or sum of components. |
| Rounding stage | Extracted component and total rates round to 2 decimals. |
| Waste allowance | None. |
| Procurement rule | None. |
| Rate dependency | This is a rate source, but its result is exposed only through the QA endpoint and is not used by DPWH_RATES or section pricing. |
| Handbook reference | Handbook says illustrative rates should be replaced by live CMPD/project rates at formula_exhaustive_handbook.md:6-8. |
| Solved-case reference | None. |
| Test coverage | No tests. |
| Current confidence | High that the loader is disconnected from solver pricing (DEF-021); medium that generic row scanning always selects the intended cell. |
| Unresolved assumptions | Workbook labels/layout are stable. Unit metadata is not captured, and there is no mapping from DUPA pay item to solver rate key. |


## Cross-reference summary

| Concern | Inventory entries | Defect register |
|---|---|---|
| Net, gross, waste-adjusted, procurement separation | TMP-S03, TMP-S05, TMP-S08, TMP-S09, TMP-S12, TMP-S13 | DEF-005, DEF-023 |
| Parser defaults and sample contamination | TMP-ADAPT01 | DEF-002, DEF-013, DEF-016 |
| Unit-safe BOQ costing | TMP-COST01, TMP-BOQ01 | DEF-003, DEF-015, DEF-028 |
| Rebar correctness and procurement | TMP-S05, TMP-U01, TMP-OPT01 | DEF-006, DEF-007, DEF-008, DEF-011, DEF-012, DEF-018 |
| Rate source and versioning | TMP-COST01, TMP-RATE01 | DEF-010, DEF-021, DEF-024 |
| Rounding and pricing precision | TMP-COST01 and all section entries | DEF-009 |

## Inventory limitations

The inventory records what the checked source does. It does not certify the engineering validity of constants that have no worked case or test. Sections VI-XIII are especially thin in the handbook and have only end-to-end positivity coverage. Any correction should first establish a normative formula/rate source and add a regression test, rather than silently replacing one undocumented assumption with another.
