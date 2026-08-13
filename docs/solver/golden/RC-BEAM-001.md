# RC-BEAM-001: Golden reinforced-concrete beam reference case

**Acceptance status:** PASS

**Classification:** RC-BEAM-001 is a proposed normative target for the replacement solver architecture and is not a regression expectation for the frozen legacy solver.

This document is the independently calculated acceptance reference for one rectangular, monolithic reinforced-concrete beam. It is a quantity, procurement, and direct-cost case only. No structural analysis, bar sizing, spacing design, or code compliance inference is performed.

Calculation payload SHA-256: `aa5bbcf33d6ffcce0c74a729a5ea0e0c780ba99978f502cb2d552c0546c736ae`

## 1. Source facts and explicit assumptions

All values in this section are inputs or declared policies, not calculated answers.

### 1.1 Geometry and ownership of intersections

```text
outer face                                                     outer face
|<-- left support 0.400 m -->|<------ clear span 5.400 m ------>|<-- right support 0.500 m -->|
|============================|==================================|==============================|
                    x = 0.000 m                         x = 5.400 m
                    clear-span coordinates for stirrups

Beam section: width 0.300 m, overall depth 0.600 m
Monolithic slab: thickness 0.150 m
Explicit beam-below-slab depth: 0.450 m
```

Concrete ownership is explicit: support concrete owns both beam-support intersections, and slab concrete owns the 0.150 m slab layer across the clear-span beam strip. The beam quantity therefore retains only the 0.450 m drop below the slab over the 5.400 m clear span.

### 1.2 Concrete, formwork, reinforcement, and procurement policies

- Concrete waste is a project-specific 3.000000% of net measured beam concrete.
- Ready-mix procurement is rounded upward to 0.100000 m^3 increments.
- Formwork includes the soffit and two beam-drop sides over the clear span. The top face, both support intersections, and both monolithic end faces are excluded.
- Longitudinal reinforcement is supplied as source facts: 3 bottom 20 mm bars and 2 top 16 mm bars. The top bars each have one explicit 0.800000 m lap and are fabricated as two equal pieces.
- Stirrups are 10 mm bars with 0.040000 m cover, two 10db hook extensions, and a project-specific aggregate 12db bend deduction. No additional centerline or bend-radius adjustment is inferred.
- Commercial stock lengths are 6.000000 m, 9.000000 m, and 12.000000 m for all three diameters.
- Cutting kerf is explicitly 0.000000 m/cut and is applied once per produced cut piece. Offcuts at least 1.000000 m long are reusable; shorter positive remnants are scrap.
- Reusable offcuts receive no credit against this case's material cost.
- Rates and productivity values are illustrative project test assumptions. Overhead, tax, and profit are excluded.

## 2. Geometry checks

| Formula ID | Calculation | Symbolic formula | Numerical substitution | Unrounded result | Reported result |
|---|---|---|---|---:|---:|
| RCB-GEO-001 | Compute the beam drop below the monolithic slab and compare it with the explicitly supplied net depth. | `D_net,calc = D_overall - t_slab` | `0.6 - 0.15` | 0.45 m | 0.450000 m |
| RCB-GEO-002 | Overall beam prism length before support deductions. | `L_outer = L_clear + w_support,left + w_support,right` | `5.4 + 0.4 + 0.5` | 6.3 m | 6.300000 m |
| RCB-GEO-003 | Centerline-to-centerline span derived transparently from the supplied clear span and support widths. | `L_c/c = L_clear + w_left/2 + w_right/2` | `5.4 + 0.4/2 + 0.5/2` | 5.85 m | 5.850000 m |
| RCB-GEO-004 | Difference between computed and explicitly supplied net depth. | `Delta_D = D_net,calc - D_net,input` | `0.45 - 0.45` | 0.00 m | 0.000000 m |

The supplied net depth is 0.450000 m. The calculated difference is 0.000000 m, so the redundant geometry facts reconcile.

## 3. Concrete takeoff

| Formula ID | Calculation | Symbolic formula | Numerical substitution | Unrounded result | Reported result |
|---|---|---|---|---:|---:|
| RCB-CON-001 | Gross full-prism beam volume before any intersection deductions. | `V_gross = b * D_overall * L_outer` | `0.3 * 0.6 * 6.3` | 1.134 m^3 | 1.134000 m^3 |
| RCB-CON-002 | Beam prism volume inside the left support. | `V_left = b * D_overall * w_left` | `0.3 * 0.6 * 0.4` | 0.072 m^3 | 0.072000 m^3 |
| RCB-CON-003 | Beam prism volume inside the right support. | `V_right = b * D_overall * w_right` | `0.3 * 0.6 * 0.5` | 0.090 m^3 | 0.090000 m^3 |
| RCB-CON-004 | Combined support-intersection deduction. | `V_support = V_left + V_right` | `0.072 + 0.090` | 0.162 m^3 | 0.162000 m^3 |
| RCB-CON-005 | Clear-span beam prism at overall depth after support deductions. | `V_clear,overall = V_gross - V_support` | `1.134 - 0.162` | 0.972 m^3 | 0.972000 m^3 |
| RCB-CON-006 | Slab-owned volume across the clear-span beam strip. | `V_slab = b * t_slab * L_clear` | `0.3 * 0.15 * 5.4` | 0.2430 m^3 | 0.243000 m^3 |
| RCB-CON-007 | Net measured beam concrete after support and slab deductions. | `V_net = V_gross - V_support - V_slab` | `1.134 - 0.162 - 0.2430` | 0.7290 m^3 | 0.729000 m^3 |
| RCB-CON-008 | Independent direct calculation using clear span and the explicit beam-below-slab depth. | `V_net,check = b * D_net * L_clear` | `0.3 * 0.45 * 5.4` | 0.7290 m^3 | 0.729000 m^3 |
| RCB-CON-009 | Concrete waste allowance kept separate from net measured volume. | `V_waste = V_net * r_waste` | `0.7290 * 0.03` | 0.021870 m^3 | 0.021870 m^3 |
| RCB-CON-010 | Concrete required before commercial procurement rounding. | `V_required = V_net + V_waste` | `0.7290 + 0.021870` | 0.750870 m^3 | 0.750870 m^3 |
| RCB-CON-011 | Concrete ordered after ceiling to the declared batch increment. | `V_proc = ceil(V_required / increment) * increment` | `ceil(0.750870 / 0.1) * 0.1` | 0.8 m^3 | 0.800000 m^3 |
| RCB-CON-012 | Quantity caused only by commercial batch rounding. | `V_rounding = V_proc - V_required` | `0.8 - 0.750870` | 0.049130 m^3 | 0.049130 m^3 |

Concrete quantity stages remain separate:

- Gross full-prism volume: 1.134000 m^3
- Net measured beam volume: 0.729000 m^3
- Waste quantity: 0.021870 m^3
- Required quantity before procurement rounding: 0.750870 m^3
- Procured quantity: 0.800000 m^3
- Commercial rounding excess: 0.049130 m^3

Independent check: gross-minus-deductions and direct net-prism methods differ by 0.000000 m^3. Status: PASS.

## 4. Formwork takeoff

| Formula ID | Calculation | Symbolic formula | Numerical substitution | Unrounded result | Reported result |
|---|---|---|---|---:|---:|
| RCB-FRM-001 | Soffit contact area over the clear span. | `A_soffit = b * L_clear` | `0.3 * 5.4` | 1.62 m^2 | 1.620000 m^2 |
| RCB-FRM-002 | Left beam-side contact area using only the beam drop below the slab. | `A_left = D_net * L_clear` | `0.45 * 5.4` | 2.430 m^2 | 2.430000 m^2 |
| RCB-FRM-003 | Right beam-side contact area using only the beam drop below the slab. | `A_right = D_net * L_clear` | `0.45 * 5.4` | 2.430 m^2 | 2.430000 m^2 |
| RCB-FRM-004 | End form area. Both ends are excluded because they are monolithic support interfaces. | `A_ends = 0` | `0` | 0 m^2 | 0.000000 m^2 |
| RCB-FRM-005 | Total form-contact area. This remains an area and is never merged into concrete volume. | `A_form = A_soffit + A_left + A_right + A_ends` | `1.62 + 2.430 + 2.430 + 0` | 6.480 m^2 | 6.480000 m^2 |
| RCB-FRM-006 | Independent beam-form perimeter method. | `A_form,check = (b + 2*D_net) * L_clear` | `(0.3 + 2*0.45) * 5.4` | 6.480 m^2 | 6.480000 m^2 |

Excluded surfaces:

- Top face at the monolithic slab interface
- Left support intersection
- Right support intersection
- Both beam end faces at monolithic supports

Formwork contact area is reported only in m^2. It is not added to, converted into, or otherwise merged with concrete volume.

### 4.1 Formwork material resources

| Formula ID | Calculation | Symbolic formula | Numerical substitution | Unrounded result | Reported result |
|---|---|---|---|---:|---:|
| RCB-FRM-007 | Theoretical plywood sheet-equivalent consumption. | `Q_ply,theory = A_form * f_ply` | `6.480 * 0.25` | 1.62000 sheet | 1.620000 sheet |
| RCB-FRM-008 | Whole-sheet plywood procurement. | `Q_ply,proc = ceil(Q_ply,theory / 1 sheet) * 1 sheet` | `ceil(1.62000 / 1) * 1` | 2 sheet | 2 sheet |
| RCB-FRM-009 | Theoretical form-lumber consumption. | `Q_lumber,theory = A_form * f_lumber` | `6.480 * 5.0` | 32.4000 board_foot | 32.400000 board_foot |
| RCB-FRM-010 | Form-lumber procurement rounded upward to a whole board foot. | `Q_lumber,proc = ceil(Q_lumber,theory / 1 bdft) * 1 bdft` | `ceil(32.4000 / 1) * 1` | 33 board_foot | 33 board_foot |
| RCB-FRM-011 | Theoretical form release oil. | `Q_oil,theory = A_form * f_oil` | `6.480 * 0.1` | 0.6480 L | 0.648000 L |
| RCB-FRM-012 | Release oil procurement rounded upward to a whole litre. | `Q_oil,proc = ceil(Q_oil,theory / 1 L) * 1 L` | `ceil(0.6480 / 1) * 1` | 1 L | 1 L |

Independent formwork check differs by 0.000000 m^2. Status: PASS.

## 5. Longitudinal reinforcement

### 5.1 L1_BOTTOM_20

Diameter: 20 mm; assembled bar count: 3 bar; lap case: `none`.

| Formula ID | Calculation | Symbolic formula | Numerical substitution | Unrounded result | Reported result |
|---|---|---|---|---:|---:|
| RCB-LON-001-01 | Effective assembled bar length before lap overlap is added as physical steel. | `L_effective = L_base + L_anchor,left + L_anchor,right + L_hook` | `5.4 + 0.25 + 0.35 + 0` | 6.00 m/bar | 6.000000 m/bar |
| RCB-LON-001-02 | Physical steel added for the explicitly specified lap. | `L_lap,add = n_lap * L_lap,each` | `0 * 0` | 0 m/bar | 0.000000 m/bar |
| RCB-LON-001-03 | Physical steel length required for one assembled longitudinal bar. | `L_steel,bar = L_effective + L_lap,add` | `6.00 + 0` | 6.00 m/bar | 6.000000 m/bar |
| RCB-LON-001-04 | Equal fabrication piece length under the declared group policy. | `L_piece = L_steel,bar / n_piece,bar` | `6.00 / 1` | 6.00 m/piece | 6.000000 m/piece |
| RCB-LON-001-05 | Total fabrication-piece demand for the group. | `N_piece = N_bar * n_piece,bar` | `3 * 1` | 3 piece | 3 piece |
| RCB-LON-001-06 | Independent assembly check. Sum of pieces less lap overlap must recover the effective bar length. | `L_effective,check = n_piece,bar * L_piece - L_lap,add` | `1 * 6.00 - 0` | 6.00 m/bar | 6.000000 m/bar |
| RCB-LON-001-07 | Theoretical physical steel length for the complete group. | `L_group = N_bar * L_steel,bar` | `3 * 6.00` | 18.00 m | 18.000000 m |
| RCB-LON-001-08 | Theoretical unit weight under the declared project test rule. | `w_d = d_mm^2 / 162.2` | `20^2 / 162.2` | 2.46609124537607891491985203452527744 kg/m | 2.466091 kg/m |
| RCB-LON-001-09 | Theoretical physical steel weight for the group. | `W_group = L_group * w_d` | `18.00 * 2.46609124537607891491985203452527744` | 44.3896424167694204685573366214549939 kg | 44.389642 kg |

### 5.2 L2_TOP_16_LAPPED

Diameter: 16 mm; assembled bar count: 2 bar; lap case: `single_lap`.

| Formula ID | Calculation | Symbolic formula | Numerical substitution | Unrounded result | Reported result |
|---|---|---|---|---:|---:|
| RCB-LON-002-01 | Effective assembled bar length before lap overlap is added as physical steel. | `L_effective = L_base + L_anchor,left + L_anchor,right + L_hook` | `5.4 + 0.35 + 0.45 + 0` | 6.20 m/bar | 6.200000 m/bar |
| RCB-LON-002-02 | Physical steel added for the explicitly specified lap. | `L_lap,add = n_lap * L_lap,each` | `1 * 0.8` | 0.8 m/bar | 0.800000 m/bar |
| RCB-LON-002-03 | Physical steel length required for one assembled longitudinal bar. | `L_steel,bar = L_effective + L_lap,add` | `6.20 + 0.8` | 7.00 m/bar | 7.000000 m/bar |
| RCB-LON-002-04 | Equal fabrication piece length under the declared group policy. | `L_piece = L_steel,bar / n_piece,bar` | `7.00 / 2` | 3.50 m/piece | 3.500000 m/piece |
| RCB-LON-002-05 | Total fabrication-piece demand for the group. | `N_piece = N_bar * n_piece,bar` | `2 * 2` | 4 piece | 4 piece |
| RCB-LON-002-06 | Independent assembly check. Sum of pieces less lap overlap must recover the effective bar length. | `L_effective,check = n_piece,bar * L_piece - L_lap,add` | `2 * 3.50 - 0.8` | 6.20 m/bar | 6.200000 m/bar |
| RCB-LON-002-07 | Theoretical physical steel length for the complete group. | `L_group = N_bar * L_steel,bar` | `2 * 7.00` | 14.00 m | 14.000000 m |
| RCB-LON-002-08 | Theoretical unit weight under the declared project test rule. | `w_d = d_mm^2 / 162.2` | `16^2 / 162.2` | 1.57829839704069050554870530209617756 kg/m | 1.578298 kg/m |
| RCB-LON-002-09 | Theoretical physical steel weight for the group. | `W_group = L_group * w_d` | `14.00 * 1.57829839704069050554870530209617756` | 22.0961775585696670776818742293464858 kg | 22.096178 kg |

The 16 mm top group is the explicit lap case. Each assembled bar has an effective length of 6.200000 m/bar, uses two 3.500000 m/piece pieces, and subtracts the 0.800000 m/bar overlap when checking assembled length.

## 6. Stirrups

| Formula ID | Calculation | Symbolic formula | Numerical substitution | Unrounded result | Reported result |
|---|---|---|---|---:|---:|
| RCB-STI-001 | Stirrup width inside the specified cover lines. | `b_st = b_beam - 2*c` | `0.3 - 2*0.04` | 0.22 m | 0.220000 m |
| RCB-STI-002 | Stirrup depth inside the specified cover lines, using overall beam depth. | `D_st = D_overall - 2*c` | `0.6 - 2*0.04` | 0.52 m | 0.520000 m |
| RCB-STI-003 | Project-specific hook extension per hook. | `L_hook,each = m_hook * d_b` | `10 * 0.01` | 0.10 m/hook | 0.100000 m/hook |
| RCB-STI-004 | Total hook extension for one stirrup. | `L_hook,total = n_hook * L_hook,each` | `2 * 0.10` | 0.20 m/stirrup | 0.200000 m/stirrup |
| RCB-STI-005 | Project-specific aggregate bend deduction for one stirrup. | `Delta_bend = m_bend * d_b` | `12 * 0.01` | 0.12 m/stirrup | 0.120000 m/stirrup |
| RCB-STI-006 | Cutting length for one rectangular stirrup under the declared hook and bend rule. | `L_st = 2*(b_st + D_st) + L_hook,total - Delta_bend` | `2*(0.22 + 0.52) + 0.20 - 0.12` | 1.56 m/stirrup | 1.560000 m/stirrup |

### 6.1 Spacing zones and transition ownership

Zone coordinates use `x = x_start + k*s` with each zone's explicit start/end ownership. The table shows the numerical substitution and the generated unrounded coordinate set.

| Formula ID | Zone | Boundary rule | Spacing | Numerical substitution | Count | Generated x-coordinates (m) |
|---|---|---|---:|---|---:|---|
| RCB-STI-Z01 | Z1_LEFT_END | `[0.000, 1.200]` | 0.100 m | `start=0.0, end=1.2, s=0.1, include_start=True, include_end=True` | 13 stirrup | 0.000, 0.100, 0.200, 0.300, 0.400, 0.500, 0.600, 0.700, 0.800, 0.900, 1.000, 1.100, 1.200 |
| RCB-STI-Z02 | Z2_MIDDLE | `(1.200, 4.200)` | 0.200 m | `start=1.2, end=4.2, s=0.2, include_start=False, include_end=False` | 14 stirrup | 1.400, 1.600, 1.800, 2.000, 2.200, 2.400, 2.600, 2.800, 3.000, 3.200, 3.400, 3.600, 3.800, 4.000 |
| RCB-STI-Z03 | Z3_RIGHT_END | `[4.200, 5.400]` | 0.100 m | `start=4.2, end=5.4, s=0.1, include_start=True, include_end=True` | 13 stirrup | 4.200, 4.300, 4.400, 4.500, 4.600, 4.700, 4.800, 4.900, 5.000, 5.100, 5.200, 5.300, 5.400 |

| Formula ID | Calculation | Symbolic formula | Numerical substitution | Unrounded result | Reported result |
|---|---|---|---|---:|---:|
| RCB-STI-007 | Sum of all zone-generated stirrup positions before deduplication. | `N_zone,sum = sum(N_zone,i)` | `13 + 14 + 13` | 40 stirrup | 40 stirrup |
| RCB-STI-008 | Duplicate transition coordinates removed by the boundary policy. | `N_duplicate = N_zone,sum - size(unique(position_union))` | `40 - 40` | 0 stirrup | 0 stirrup |
| RCB-STI-009 | Unique stirrup count after applying explicit transition-boundary ownership. | `N_st = size(unique(position_union))` | `size(unique(40 generated coordinates))` | 40 stirrup | 40 stirrup |
| RCB-STI-010 | Total theoretical stirrup steel length. | `L_st,total = N_st * L_st` | `40 * 1.56` | 62.40 m | 62.400000 m |
| RCB-STI-011 | Theoretical 10 mm unit weight under the declared project test rule. | `w_10 = 10^2 / 162.2` | `10^2 / 162.2` | 0.616522811344019728729963008631319359 kg/m | 0.616523 kg/m |
| RCB-STI-012 | Total theoretical stirrup weight. | `W_st = L_st,total * w_10` | `62.40 * 0.616522811344019728729963008631319359` | 38.4710234278668310727496917385943280 kg | 38.471023 kg |

Boundary result: 0 duplicate coordinates and 40 unique stirrups. Status: PASS.

## 7. Reinforcement totals before procurement

| Formula ID | Calculation | Symbolic formula | Numerical substitution | Unrounded result | Reported result |
|---|---|---|---|---:|---:|
| RCB-REB-001 | Total physical reinforcing-steel length, including the explicit lap overlap and all stirrups. | `L_rebar,total = sum(L_longitudinal groups) + L_stirrups` | `62.40 + 14.00 + 18.00` | 94.40 m | 94.400000 m |
| RCB-REB-002 | Total theoretical installed reinforcing-steel weight. | `W_rebar,total = sum(W_by_diameter)` | `38.4710234278668310727496917385943280 + 22.0961775585696670776818742293464858 + 44.3896424167694204685573366214549939` | 104.956843403205918618988902589395808 kg | 104.956843 kg |
| RCB-REB-003 | Theoretical tie-wire quantity based on installed rebar weight. | `W_tie,theory = W_rebar,total * f_tie` | `104.956843403205918618988902589395808 * 0.015` | 1.57435265104808877928483353884093712 kg | 1.574353 kg |
| RCB-REB-004 | Tie wire rounded upward to the declared procurement increment. | `W_tie,proc = ceil(W_tie,theory / increment) * increment` | `ceil(1.57435265104808877928483353884093712 / 1) * 1` | 2 kg | 2 kg |

## 8. Rebar procurement and cutting schedule

The optimizer must satisfy every cut piece exactly. It first minimizes purchased stock length, then stock-bar count, non-reusable scrap, the largest individual offcut, and finally a deterministic pattern signature.

### 8.1 Diameter 20 mm

Available stock lengths: 6.000, 9.000, 12.000 m. Required demand: 3 piece at 6.000000 m/piece.

Plan-selection formula ID: `RCB-PRC-001-04`. Symbolic rule: `arg min_plan (L_purchased, N_stock, L_scrap, max(L_offcut), signature) subject to exact piece demand`. Numerical substitution: `piece_length=6.00 m, piece_count=3, stock_lengths=[6, 9, 12] m, kerf=0 m/cut, reusable_threshold=1 m`.

Each selected stock bar applies `L_stock = sum(L_cut) + L_kerf + L_reusable + L_scrap`.

| Formula ID | Stock bar | Stock length | Cuts | Used cut length | Kerf | Reusable offcut | Scrap | Length-balance substitution | Difference |
|---|---|---:|---|---:|---:|---:|---:|---|---:|
| RCB-PRC-001-04-01 | D20-S01 | 12.000000 m | 6.000 + 6.000 m | 12.000000 m | 0.000000 m | 0.000000 m | 0.000000 m | `12 = (2 * 6.00) + (2 * 0) + 0 + 0` | 0.000000 m |
| RCB-PRC-001-04-02 | D20-S02 | 6.000000 m | 6.000 m | 6.000000 m | 0.000000 m | 0.000000 m | 0.000000 m | `6 = (1 * 6.00) + (1 * 0) + 0 + 0` | 0.000000 m |

| Formula ID | Calculation | Symbolic formula | Numerical substitution | Unrounded result | Reported result |
|---|---|---|---|---:|---:|
| RCB-PRC-001-01 | Uniform cut length used by the diameter-specific cutting plan. | `L_piece = source demand cut length` | `6.00` | 6.00 m/piece | 6.000000 m/piece |
| RCB-PRC-001-02 | Required cut-piece count for this diameter. | `N_required = sum(source piece counts)` | `3` | 3 piece | 3 piece |
| RCB-PRC-001-03 | Total physical cut length required for this diameter. | `L_required = N_required * L_piece` | `3 * 6.00` | 18.00 m | 18.000000 m |
| RCB-PRC-001-05 | Count of purchased commercial stock bars in the selected plan. | `N_stock = count(selected stock bars)` | `2` | 2 stock_bar | 2 stock_bar |
| RCB-PRC-001-06 | Total purchased commercial stock length for this diameter. | `L_purchased = sum(L_stock bars)` | `12 + 6` | 18 m | 18.000000 m |
| RCB-PRC-001-07 | Purchased weight for this diameter. | `W_purchased = L_purchased * w_d` | `18 * 2.46609124537607891491985203452527744` | 44.3896424167694204685573366214549939 kg | 44.389642 kg |
| RCB-PRC-001-08 | Offcut length at or above the declared reusable threshold. | `L_reusable = sum(offcut where offcut >= threshold)` | `0 + 0` | 0 m | 0.000000 m |
| RCB-PRC-001-09 | Reusable offcut weight for this diameter. | `W_reusable = L_reusable * w_d` | `0 * 2.46609124537607891491985203452527744` | 0.00000000000000000000000000000000000 kg | 0.000000 kg |
| RCB-PRC-001-10 | Non-reusable offcut length below the declared threshold. | `L_scrap = sum(offcut where 0 < offcut < threshold)` | `0 + 0` | 0 m | 0.000000 m |
| RCB-PRC-001-11 | Non-reusable scrap weight for this diameter. | `W_scrap = L_scrap * w_d` | `0 * 2.46609124537607891491985203452527744` | 0.00000000000000000000000000000000000 kg | 0.000000 kg |
| RCB-PRC-001-12 | Cut pieces not satisfied by the selected plan. | `N_unresolved = N_required - N_produced` | `3 - 3` | 0 piece | 0 piece |
| RCB-PRC-001-13 | Purchased length less required cut length, reusable offcut, and scrap. | `Delta_L = L_purchased - L_required - L_reusable - L_scrap` | `18 - 18.00 - 0 - 0` | 0.00 m | 0.000000 m |
| RCB-PRC-001-14 | Purchased weight less installed, reusable offcut, and scrap weight. | `Delta_W = W_purchased - W_installed - W_reusable - W_scrap` | `44.3896424167694204685573366214549939 - 44.3896424167694204685573366214549939 - 0.00000000000000000000000000000000000 - 0.00000000000000000000000000000000000` | 0.00000000000000000000000000000000000 kg | 0.000000 kg |

### 8.2 Diameter 16 mm

Available stock lengths: 6.000, 9.000, 12.000 m. Required demand: 4 piece at 3.500000 m/piece.

Plan-selection formula ID: `RCB-PRC-002-04`. Symbolic rule: `arg min_plan (L_purchased, N_stock, L_scrap, max(L_offcut), signature) subject to exact piece demand`. Numerical substitution: `piece_length=3.50 m, piece_count=4, stock_lengths=[6, 9, 12] m, kerf=0 m/cut, reusable_threshold=1 m`.

Each selected stock bar applies `L_stock = sum(L_cut) + L_kerf + L_reusable + L_scrap`.

| Formula ID | Stock bar | Stock length | Cuts | Used cut length | Kerf | Reusable offcut | Scrap | Length-balance substitution | Difference |
|---|---|---:|---|---:|---:|---:|---:|---|---:|
| RCB-PRC-002-04-01 | D16-S01 | 9.000000 m | 3.500 + 3.500 m | 7.000000 m | 0.000000 m | 2.000000 m | 0.000000 m | `9 = (2 * 3.50) + (2 * 0) + 2.00 + 0` | 0.000000 m |
| RCB-PRC-002-04-02 | D16-S02 | 9.000000 m | 3.500 + 3.500 m | 7.000000 m | 0.000000 m | 2.000000 m | 0.000000 m | `9 = (2 * 3.50) + (2 * 0) + 2.00 + 0` | 0.000000 m |

| Formula ID | Calculation | Symbolic formula | Numerical substitution | Unrounded result | Reported result |
|---|---|---|---|---:|---:|
| RCB-PRC-002-01 | Uniform cut length used by the diameter-specific cutting plan. | `L_piece = source demand cut length` | `3.50` | 3.50 m/piece | 3.500000 m/piece |
| RCB-PRC-002-02 | Required cut-piece count for this diameter. | `N_required = sum(source piece counts)` | `4` | 4 piece | 4 piece |
| RCB-PRC-002-03 | Total physical cut length required for this diameter. | `L_required = N_required * L_piece` | `4 * 3.50` | 14.00 m | 14.000000 m |
| RCB-PRC-002-05 | Count of purchased commercial stock bars in the selected plan. | `N_stock = count(selected stock bars)` | `2` | 2 stock_bar | 2 stock_bar |
| RCB-PRC-002-06 | Total purchased commercial stock length for this diameter. | `L_purchased = sum(L_stock bars)` | `9 + 9` | 18 m | 18.000000 m |
| RCB-PRC-002-07 | Purchased weight for this diameter. | `W_purchased = L_purchased * w_d` | `18 * 1.57829839704069050554870530209617756` | 28.4093711467324290998766954377311961 kg | 28.409371 kg |
| RCB-PRC-002-08 | Offcut length at or above the declared reusable threshold. | `L_reusable = sum(offcut where offcut >= threshold)` | `2.00 + 2.00` | 4.00 m | 4.000000 m |
| RCB-PRC-002-09 | Reusable offcut weight for this diameter. | `W_reusable = L_reusable * w_d` | `4.00 * 1.57829839704069050554870530209617756` | 6.31319358816276202219482120838471024 kg | 6.313194 kg |
| RCB-PRC-002-10 | Non-reusable offcut length below the declared threshold. | `L_scrap = sum(offcut where 0 < offcut < threshold)` | `0 + 0` | 0 m | 0.000000 m |
| RCB-PRC-002-11 | Non-reusable scrap weight for this diameter. | `W_scrap = L_scrap * w_d` | `0 * 1.57829839704069050554870530209617756` | 0.00000000000000000000000000000000000 kg | 0.000000 kg |
| RCB-PRC-002-12 | Cut pieces not satisfied by the selected plan. | `N_unresolved = N_required - N_produced` | `4 - 4` | 0 piece | 0 piece |
| RCB-PRC-002-13 | Purchased length less required cut length, reusable offcut, and scrap. | `Delta_L = L_purchased - L_required - L_reusable - L_scrap` | `18 - 14.00 - 4.00 - 0` | 0.00 m | 0.000000 m |
| RCB-PRC-002-14 | Purchased weight less installed, reusable offcut, and scrap weight. | `Delta_W = W_purchased - W_installed - W_reusable - W_scrap` | `28.4093711467324290998766954377311961 - 22.0961775585696670776818742293464858 - 6.31319358816276202219482120838471024 - 0.00000000000000000000000000000000000` | 0.00000000000000000000000000000000006 kg | 0.000000 kg |

### 8.3 Diameter 10 mm

Available stock lengths: 6.000, 9.000, 12.000 m. Required demand: 40 piece at 1.560000 m/piece.

Plan-selection formula ID: `RCB-PRC-003-04`. Symbolic rule: `arg min_plan (L_purchased, N_stock, L_scrap, max(L_offcut), signature) subject to exact piece demand`. Numerical substitution: `piece_length=1.56 m, piece_count=40, stock_lengths=[6, 9, 12] m, kerf=0 m/cut, reusable_threshold=1 m`.

Each selected stock bar applies `L_stock = sum(L_cut) + L_kerf + L_reusable + L_scrap`.

| Formula ID | Stock bar | Stock length | Cuts | Used cut length | Kerf | Reusable offcut | Scrap | Length-balance substitution | Difference |
|---|---|---:|---|---:|---:|---:|---:|---|---:|
| RCB-PRC-003-04-01 | D10-S01 | 12.000000 m | 1.560 + 1.560 + 1.560 + 1.560 + 1.560 + 1.560 + 1.560 m | 10.920000 m | 0.000000 m | 1.080000 m | 0.000000 m | `12 = (7 * 1.56) + (7 * 0) + 1.08 + 0` | 0.000000 m |
| RCB-PRC-003-04-02 | D10-S02 | 12.000000 m | 1.560 + 1.560 + 1.560 + 1.560 + 1.560 + 1.560 + 1.560 m | 10.920000 m | 0.000000 m | 1.080000 m | 0.000000 m | `12 = (7 * 1.56) + (7 * 0) + 1.08 + 0` | 0.000000 m |
| RCB-PRC-003-04-03 | D10-S03 | 12.000000 m | 1.560 + 1.560 + 1.560 + 1.560 + 1.560 + 1.560 + 1.560 m | 10.920000 m | 0.000000 m | 1.080000 m | 0.000000 m | `12 = (7 * 1.56) + (7 * 0) + 1.08 + 0` | 0.000000 m |
| RCB-PRC-003-04-04 | D10-S04 | 12.000000 m | 1.560 + 1.560 + 1.560 + 1.560 + 1.560 + 1.560 + 1.560 m | 10.920000 m | 0.000000 m | 1.080000 m | 0.000000 m | `12 = (7 * 1.56) + (7 * 0) + 1.08 + 0` | 0.000000 m |
| RCB-PRC-003-04-05 | D10-S05 | 12.000000 m | 1.560 + 1.560 + 1.560 + 1.560 + 1.560 + 1.560 + 1.560 m | 10.920000 m | 0.000000 m | 1.080000 m | 0.000000 m | `12 = (7 * 1.56) + (7 * 0) + 1.08 + 0` | 0.000000 m |
| RCB-PRC-003-04-06 | D10-S06 | 9.000000 m | 1.560 + 1.560 + 1.560 + 1.560 + 1.560 m | 7.800000 m | 0.000000 m | 1.200000 m | 0.000000 m | `9 = (5 * 1.56) + (5 * 0) + 1.20 + 0` | 0.000000 m |

| Formula ID | Calculation | Symbolic formula | Numerical substitution | Unrounded result | Reported result |
|---|---|---|---|---:|---:|
| RCB-PRC-003-01 | Uniform cut length used by the diameter-specific cutting plan. | `L_piece = source demand cut length` | `1.56` | 1.56 m/piece | 1.560000 m/piece |
| RCB-PRC-003-02 | Required cut-piece count for this diameter. | `N_required = sum(source piece counts)` | `40` | 40 piece | 40 piece |
| RCB-PRC-003-03 | Total physical cut length required for this diameter. | `L_required = N_required * L_piece` | `40 * 1.56` | 62.40 m | 62.400000 m |
| RCB-PRC-003-05 | Count of purchased commercial stock bars in the selected plan. | `N_stock = count(selected stock bars)` | `6` | 6 stock_bar | 6 stock_bar |
| RCB-PRC-003-06 | Total purchased commercial stock length for this diameter. | `L_purchased = sum(L_stock bars)` | `12 + 12 + 12 + 12 + 12 + 9` | 69 m | 69.000000 m |
| RCB-PRC-003-07 | Purchased weight for this diameter. | `W_purchased = L_purchased * w_d` | `69 * 0.616522811344019728729963008631319359` | 42.5400739827373612823674475955610358 kg | 42.540074 kg |
| RCB-PRC-003-08 | Offcut length at or above the declared reusable threshold. | `L_reusable = sum(offcut where offcut >= threshold)` | `1.08 + 1.08 + 1.08 + 1.08 + 1.08 + 1.20` | 6.60 m | 6.600000 m |
| RCB-PRC-003-09 | Reusable offcut weight for this diameter. | `W_reusable = L_reusable * w_d` | `6.60 * 0.616522811344019728729963008631319359` | 4.06905055487053020961775585696670777 kg | 4.069051 kg |
| RCB-PRC-003-10 | Non-reusable offcut length below the declared threshold. | `L_scrap = sum(offcut where 0 < offcut < threshold)` | `0 + 0 + 0 + 0 + 0 + 0` | 0 m | 0.000000 m |
| RCB-PRC-003-11 | Non-reusable scrap weight for this diameter. | `W_scrap = L_scrap * w_d` | `0 * 0.616522811344019728729963008631319359` | 0.000000000000000000000000000000000000 kg | 0.000000 kg |
| RCB-PRC-003-12 | Cut pieces not satisfied by the selected plan. | `N_unresolved = N_required - N_produced` | `40 - 40` | 0 piece | 0 piece |
| RCB-PRC-003-13 | Purchased length less required cut length, reusable offcut, and scrap. | `Delta_L = L_purchased - L_required - L_reusable - L_scrap` | `69 - 62.40 - 6.60 - 0` | 0.00 m | 0.000000 m |
| RCB-PRC-003-14 | Purchased weight less installed, reusable offcut, and scrap weight. | `Delta_W = W_purchased - W_installed - W_reusable - W_scrap` | `42.5400739827373612823674475955610358 - 38.4710234278668310727496917385943280 - 4.06905055487053020961775585696670777 - 0.000000000000000000000000000000000000` | 0.000000000000000000000000000000000030 kg | 0.000000 kg |

### 8.4 Overall procurement reconciliation

| Formula ID | Calculation | Symbolic formula | Numerical substitution | Unrounded result | Reported result |
|---|---|---|---|---:|---:|
| RCB-PRC-TOT-001 | Total theoretical cut length across all diameters. | `L_required,total = sum(L_required,d)` | `18.00 + 14.00 + 62.40` | 94.40 m | 94.400000 m |
| RCB-PRC-TOT-002 | Total purchased stock length across all diameters. | `L_purchased,total = sum(L_purchased,d)` | `18 + 18 + 69` | 105 m | 105.000000 m |
| RCB-PRC-TOT-003 | Total purchased reinforcing-steel weight across all diameters. | `W_purchased,total = sum(W_purchased,d)` | `44.3896424167694204685573366214549939 + 28.4093711467324290998766954377311961 + 42.5400739827373612823674475955610358` | 115.339087546239210850801479654747226 kg | 115.339088 kg |
| RCB-PRC-TOT-004 | Total reusable offcut length across all diameters. | `L_reusable,total = sum(L_reusable,d)` | `10.60` | 10.60 m | 10.600000 m |
| RCB-PRC-TOT-005 | Total reusable offcut weight across all diameters. | `W_reusable,total = sum(W_reusable,d)` | `10.3822441430332922318125770653514180` | 10.3822441430332922318125770653514180 kg | 10.382244 kg |
| RCB-PRC-TOT-006 | Total non-reusable scrap length across all diameters. | `L_scrap,total = sum(L_scrap,d)` | `0` | 0 m | 0.000000 m |
| RCB-PRC-TOT-007 | Total non-reusable scrap weight across all diameters. | `W_scrap,total = sum(W_scrap,d)` | `0.000000000000000000000000000000000000` | 0.000000000000000000000000000000000000 kg | 0.000000 kg |
| RCB-PRC-TOT-008 | Total unresolved cut-piece demand. | `N_unresolved,total = sum(N_unresolved,d)` | `0` | 0 piece | 0 piece |
| RCB-PRC-TOT-009 | Overall purchased-length reconciliation. | `Delta_L,total = L_purchased,total - L_required,total - L_reusable,total - L_scrap,total` | `105 - 94.40 - 10.60 - 0` | 0.00 m | 0.000000 m |
| RCB-PRC-TOT-010 | Overall purchased-weight reconciliation. | `Delta_W,total = W_purchased,total - W_installed,total - W_reusable,total - W_scrap,total` | `115.339087546239210850801479654747226 - 104.956843403205918618988902589395808 - 10.3822441430332922318125770653514180 - 0.000000000000000000000000000000000000` | 0.000000000000000000000000000000000000 kg | 0.000000 kg |

Length reconciliation: 105.000000 m purchased = 94.400000 m installed demand + 10.600000 m reusable offcut + 0.000000 m scrap.

Weight reconciliation: 115.339088 kg purchased = 104.956843 kg theoretical installed + 10.382244 kg reusable offcut + 0.000000 kg scrap.

Unresolved demand is 0 piece. Length status: PASS; weight status: PASS; unresolved-demand status: PASS.

## 9. Resource and direct-cost ledger

### 9.1 Materials

| Resource | Quantity | Rate | Unrounded amount | Reported amount | Formula ID |
|---|---:|---:|---:|---:|---|
| MAT-CON-RM - Ready-mix concrete | 0.800000 m^3 | 5500.00 PHP/m^3 | 4400.0 PHP | 4400.00 PHP | RCB-CST-MAT-001 |
| MAT-FRM-PLY - 12 mm plywood sheet equivalent | 2.000000 sheet | 850.00 PHP/sheet | 1700 PHP | 1700.00 PHP | RCB-CST-MAT-002 |
| MAT-FRM-LBR - Form lumber | 33.000000 board_foot | 55.00 PHP/board_foot | 1815 PHP | 1815.00 PHP | RCB-CST-MAT-003 |
| MAT-FRM-OIL - Form release oil | 1.000000 L | 180.00 PHP/L | 180 PHP | 180.00 PHP | RCB-CST-MAT-004 |
| MAT-RB-20 - 20 mm reinforcing steel | 44.389642 kg | 62.00 PHP/kg | 2752.15782983970406905055487053020962 PHP | 2752.16 PHP | RCB-CST-MAT-005 |
| MAT-RB-16 - 16 mm reinforcing steel | 28.409371 kg | 60.00 PHP/kg | 1704.56226880394574599260172626387177 PHP | 1704.56 PHP | RCB-CST-MAT-006 |
| MAT-RB-10 - 10 mm reinforcing steel | 42.540074 kg | 64.00 PHP/kg | 2722.56473489519112207151664611590629 PHP | 2722.56 PHP | RCB-CST-MAT-007 |
| MAT-TIE-WIRE - Tie wire | 2.000000 kg | 90.00 PHP/kg | 180 PHP | 180.00 PHP | RCB-CST-MAT-008 |

Material cost calculation trace:

| Formula ID | Calculation | Symbolic formula | Numerical substitution | Unrounded result | Reported result |
|---|---|---|---|---:|---:|
| RCB-CST-MAT-001 | Direct material cost for Ready-mix concrete. | `C_material,line = Q_procurement * rate` | `0.8 * 5500` | 4400.0 PHP | 4400.00 PHP |
| RCB-CST-MAT-002 | Direct material cost for 12 mm plywood sheet equivalent. | `C_material,line = Q_procurement * rate` | `2 * 850` | 1700 PHP | 1700.00 PHP |
| RCB-CST-MAT-003 | Direct material cost for Form lumber. | `C_material,line = Q_procurement * rate` | `33 * 55` | 1815 PHP | 1815.00 PHP |
| RCB-CST-MAT-004 | Direct material cost for Form release oil. | `C_material,line = Q_procurement * rate` | `1 * 180` | 180 PHP | 180.00 PHP |
| RCB-CST-MAT-005 | Direct material cost for 20 mm reinforcing steel. | `C_material,line = Q_procurement * rate` | `44.3896424167694204685573366214549939 * 62` | 2752.15782983970406905055487053020962 PHP | 2752.16 PHP |
| RCB-CST-MAT-006 | Direct material cost for 16 mm reinforcing steel. | `C_material,line = Q_procurement * rate` | `28.4093711467324290998766954377311961 * 60` | 1704.56226880394574599260172626387177 PHP | 1704.56 PHP |
| RCB-CST-MAT-007 | Direct material cost for 10 mm reinforcing steel. | `C_material,line = Q_procurement * rate` | `42.5400739827373612823674475955610358 * 64` | 2722.56473489519112207151664611590629 PHP | 2722.56 PHP |
| RCB-CST-MAT-008 | Direct material cost for Tie wire. | `C_material,line = Q_procurement * rate` | `2 * 90` | 180 PHP | 180.00 PHP |

Direct material subtotal: **15454.28 PHP**

### 9.2 Labor

| Resource | Basis quantity | Productivity | Crew-days | Rate | Reported amount |
|---|---:|---:|---:|---:|---:|
| LAB-CON-PLACE - Concrete placing crew | 0.750870 m^3 | 4.000000 m^3/crew-day | 0.187718 crew-day | 4800.00 PHP/crew-day | 901.04 PHP |
| LAB-FRM - Formwork carpentry crew | 6.480000 m^2 | 10.000000 m^2/crew-day | 0.648000 crew-day | 3600.00 PHP/crew-day | 2332.80 PHP |
| LAB-RB - Rebar fabrication and installation crew | 104.956843 kg | 250.000000 kg/crew-day | 0.419827 crew-day | 4200.00 PHP/crew-day | 1763.27 PHP |

Labor usage and cost calculation trace:

| Formula ID | Calculation | Symbolic formula | Numerical substitution | Unrounded result | Reported result |
|---|---|---|---|---:|---:|
| RCB-CST-LAB-001-A | Crew usage for Concrete placing crew. | `T_crew = Q_basis / productivity` | `0.750870 / 4` | 0.1877175 crew-day | 0.187718 crew-day |
| RCB-CST-LAB-001-B | Direct labor cost for Concrete placing crew. | `C_labor,line = T_crew * rate` | `0.1877175 * 4800` | 901.0440000 PHP | 901.04 PHP |
| RCB-CST-LAB-002-A | Crew usage for Formwork carpentry crew. | `T_crew = Q_basis / productivity` | `6.480 / 10` | 0.648 crew-day | 0.648000 crew-day |
| RCB-CST-LAB-002-B | Direct labor cost for Formwork carpentry crew. | `C_labor,line = T_crew * rate` | `0.648 * 3600` | 2332.800 PHP | 2332.80 PHP |
| RCB-CST-LAB-003-A | Crew usage for Rebar fabrication and installation crew. | `T_crew = Q_basis / productivity` | `104.956843403205918618988902589395808 / 250` | 0.419827373612823674475955610357583232 crew-day | 0.419827 crew-day |
| RCB-CST-LAB-003-B | Direct labor cost for Rebar fabrication and installation crew. | `C_labor,line = T_crew * rate` | `0.419827373612823674475955610357583232 * 4200` | 1763.27496917385943279901356350184957 PHP | 1763.27 PHP |

Direct labor subtotal: **4997.11 PHP**

### 9.3 Equipment

| Resource | Basis quantity | Calculated use | Minimum | Charged use | Rate | Reported amount |
|---|---:|---:|---:|---:|---:|---:|
| EQ-CON-VIB - Concrete vibrator | 0.750870 m^3 | 0.150174 unit-day | 0.250000 unit-day | 0.250000 unit-day | 1200.00 PHP/unit-day | 300.00 PHP |
| EQ-RB-CUT - Rebar cutter and bender | 104.956843 kg | 0.209914 unit-day | 0.250000 unit-day | 0.250000 unit-day | 900.00 PHP/unit-day | 225.00 PHP |

Equipment usage, minimum-charge, and cost calculation trace:

| Formula ID | Calculation | Symbolic formula | Numerical substitution | Unrounded result | Reported result |
|---|---|---|---|---:|---:|
| RCB-CST-EQ-001-A | Calculated equipment usage before minimum charge for Concrete vibrator. | `T_calc = Q_basis / productivity` | `0.750870 / 5` | 0.150174 unit-day | 0.150174 unit-day |
| RCB-CST-EQ-001-B | Charged equipment usage for Concrete vibrator. | `T_charge = max(T_calc, T_min)` | `max(0.150174, 0.25)` | 0.25 unit-day | 0.250000 unit-day |
| RCB-CST-EQ-001-C | Direct equipment cost for Concrete vibrator. | `C_equipment,line = T_charge * rate` | `0.25 * 1200` | 300.00 PHP | 300.00 PHP |
| RCB-CST-EQ-002-A | Calculated equipment usage before minimum charge for Rebar cutter and bender. | `T_calc = Q_basis / productivity` | `104.956843403205918618988902589395808 / 500` | 0.209913686806411837237977805178791616 unit-day | 0.209914 unit-day |
| RCB-CST-EQ-002-B | Charged equipment usage for Rebar cutter and bender. | `T_charge = max(T_calc, T_min)` | `max(0.209913686806411837237977805178791616, 0.25)` | 0.25 unit-day | 0.250000 unit-day |
| RCB-CST-EQ-002-C | Direct equipment cost for Rebar cutter and bender. | `C_equipment,line = T_charge * rate` | `0.25 * 900` | 225.00 PHP | 225.00 PHP |

Direct equipment subtotal: **525.00 PHP**

### 9.4 Cost reconciliation

| Formula ID | Calculation | Symbolic formula | Numerical substitution | Unrounded result | Reported result |
|---|---|---|---|---:|---:|
| RCB-CST-SUB-001 | Direct material subtotal as the sum of reported material line amounts. | `C_material = sum(reported material line amounts)` | `4400.00 + 1700.00 + 1815.00 + 180.00 + 2752.16 + 1704.56 + 2722.56 + 180.00` | 15454.28 PHP | 15454.28 PHP |
| RCB-CST-SUB-002 | Direct labor subtotal as the sum of reported labor line amounts. | `C_labor = sum(reported labor line amounts)` | `901.04 + 2332.80 + 1763.27` | 4997.11 PHP | 4997.11 PHP |
| RCB-CST-SUB-003 | Direct equipment subtotal as the sum of reported equipment line amounts. | `C_equipment = sum(reported equipment line amounts)` | `300.00 + 225.00` | 525.00 PHP | 525.00 PHP |
| RCB-CST-TOT-001 | Total direct cost with no overhead, tax, or profit. | `C_direct = C_material + C_labor + C_equipment` | `15454.28 + 4997.11 + 525.00` | 20976.39 PHP | 20976.39 PHP |

Total direct cost is **20976.39 PHP**. Overhead, tax, and profit are each 0.00 PHP. Cost reconciliation difference: 0.00 PHP. Status: PASS.

## 10. Independent checks and acceptance summary

| Formula ID | Check | Symbolic formula | Numerical substitution | Difference or unresolved quantity | Status |
|---|---|---|---|---:|---|
| RCB-REC-001 | Check the explicit net beam depth against overall depth less slab thickness. | `Delta_D = (D_overall - t_slab) - D_net,input` | `(0.6 - 0.15) - 0.45` | 0.000000 m | PASS |
| RCB-REC-002 | Compare net concrete from deductions with the direct beam-drop prism method. | `Delta_V = V_net,deduction - V_net,direct` | `0.7290 - 0.7290` | 0.000000 m^3 | PASS |
| RCB-REC-003 | Compare component-sum formwork with the independent perimeter method. | `Delta_A = A_form,components - A_form,perimeter` | `6.480 - 6.480` | 0.000000 m^2 | PASS |
| RCB-REC-004 | Confirm that spacing-zone transition coordinates are not double-counted. | `N_duplicate = N_generated - N_unique` | `40 - 40` | 0 stirrup | PASS |
| RCB-REC-005 | Reconcile purchased stock length with cuts, reusable offcuts, and scrap. | `Delta_L = L_purchased - L_installed - L_reusable - L_scrap` | `105 - 94.40 - 10.60 - 0` | 0.000000 m | PASS |
| RCB-REC-006 | Reconcile purchased stock weight with installed steel, reusable offcuts, and scrap. | `Delta_W = W_purchased - W_installed - W_reusable - W_scrap` | `115.339087546239210850801479654747226 - 104.956843403205918618988902589395808 - 10.3822441430332922318125770653514180 - 0.000000000000000000000000000000000000` | 0.000000 kg | PASS |
| RCB-REC-007 | Confirm that every required reinforcing-steel cut piece is assigned to stock. | `N_unresolved,total = sum(N_required,d - N_produced,d)` | `0` | 0 piece | PASS |
| RCB-REC-008 | Reconcile total direct cost with reported material, labor, and equipment subtotals. | `Delta_C = C_direct - C_material - C_labor - C_equipment` | `20976.39 - 15454.28 - 4997.11 - 525.00` | 0.00 PHP | PASS |

## 11. Assumptions requiring domain review

1. Confirm that support concrete, rather than beam concrete, should own the complete beam cross-section within both support widths for the project's measurement rules.
2. Confirm that the slab is measured at full 0.150000 m thickness across the clear-span beam strip, leaving only the 0.450000 m beam drop in the beam quantity.
3. Confirm the 3.000000% concrete waste allowance and 0.100000 m^3 ready-mix ordering increment.
4. Confirm the formwork consumption factors and whole-unit procurement rounding. They are costing assumptions, not geometric necessities.
5. Confirm every reinforcement detail supplied in the input, especially the anchorage additions, the 0.800000 m lap, the equal-piece fabrication policy, 0.040000 m stirrup cover, 10db hooks, and 12db aggregate bend deduction.
6. Confirm that 6.000000 m, 9.000000 m, and 12.000000 m bars are actually available for all diameters, and whether cutting kerf should remain zero.
7. Confirm the 1.000000 m reusable-offcut threshold and whether offcut inventory should receive a cost credit or be reserved for later elements.
8. Confirm illustrative rates, labor productivity, equipment productivity, and minimum equipment charges before using this case for real estimating.

No assumption above is asserted to be required by a Philippine code.

## 12. Proposed boundary and invalid-input tests

1. Reject zero or negative beam width, overall depth, clear span, support width, slab thickness, or procurement increment.
2. Reject a slab thickness greater than or equal to overall beam depth, and reject an explicit net depth that does not equal overall depth less slab thickness within tolerance.
3. Reject a support marked as a full cross-section overlap when its along-beam dimension is missing.
4. Verify a zero-width support produces zero support-intersection deduction only when the input explicitly allows a face support with no overlap length.
5. Verify zero concrete waste keeps net and required quantities equal while procurement rounding remains separate.
6. Verify an exact 0.100000 m^3 concrete multiple produces zero procurement-rounding excess.
7. Reject negative cover or cover large enough to make stirrup clear width or clear depth non-positive.
8. Reject zero or negative stirrup spacing and zones whose end coordinate is less than their start coordinate.
9. Verify adjacent zones that both include the same transition coordinate are either rejected or explicitly deduplicated with a nonzero duplicate diagnostic.
10. Verify a middle zone shorter than one spacing interval can validly generate zero interior stirrups without division errors.
11. Reject non-integer bar counts, lap counts, pieces per bar, and stock-bar demand counts.
12. Reject a lap length that is negative or an equal-piece policy that cannot recover the declared effective assembled length.
13. Report unresolved demand when every available stock length is shorter than a required cut piece.
14. Verify a leftover exactly equal to the 1.000000 m threshold is reusable, while a 0.999999 m leftover is scrap.
15. Verify nonzero cutting kerf is included in each stock pattern and can change the optimum or create unresolved demand.
16. Verify the optimizer's tie-break order with equal purchased length but different stock-bar counts, scrap, and maximum offcut.
17. Reject missing resource rates, zero productivity, negative rates, and negative minimum equipment charges.
18. Verify line-level half-up rounding before subtotals using a rate that creates a half-cent boundary.
19. Verify JSON input contains no expected-output keys and that expected JSON contains no undeclared source assumptions.
20. Run the support checker and fail on any byte-level difference between the regenerated Markdown/expected JSON and the committed files.

## 13. Reproduction

From the repository root:

```bash
python tests/solver/golden/support/verify_rc_beam_001.py
```

To regenerate the expected JSON and this Markdown file from the input facts:

```bash
python tests/solver/golden/support/verify_rc_beam_001.py --write
```

The checker compares the entire calculated JSON object and the entire rendered Markdown text. A mismatch returns a nonzero exit code.
