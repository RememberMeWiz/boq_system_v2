# Construction Quantity Takeoff & Direct Costing Reference
## An Original Estimating Handbook for Plan2Takeoff V2 (13 Trade Divisions)

**Purpose**: This is an original reference document, written for the Plan2Takeoff V2 engine. It presents standard Philippine construction-estimating methodology — the kind taught in quantity surveying courses and used in DPWH-style estimating practice (the same conventions underlying Fajardo-style "Simplified Construction Estimate" approaches) — restated in original form, with original worked examples. It is not a reproduction, excerpt, or summary of any specific textbook; formulas below reflect general industry practice (PNS steel standards, DPWH CMPD costing structure, standard CHB/mortar ratios) that appear across multiple estimating references.

**Costing convention used throughout**:
$$C_{total} = C_{material} + C_{labor} + C_{equipment}$$
All worked examples use illustrative unit rates only — swap in live DPWH CMPD rates or project-specific supplier quotes in production.

---

## Section I — General Requirements & Site Preparation

### Scope
Mobilization/demobilization, permits and clearances, temporary facilities (site office, workers' bunkhouse, perimeter fence), and safety/health provisioning. These items are typically priced as **lump sum (lot)** percentages of estimated direct cost rather than measured quantities, since they don't scale linearly with a single trade quantity.

### Standard Ratios
- **Mobilization/Demobilization**: 0.5%–1.5% of total direct cost (small residential) up to 2%–3% (remote/large sites).
- **Temporary Facilities & Enclosure**: 1%–2% of total direct cost.
- **Safety & Health (PPE, signage, first-aid, safety officer)**: 0.5%–1% of total direct cost, plus mandatory statutory safety officer manday cost where a project exceeds a threshold headcount.
- **Permits & Clearances**: Fixed lot sum based on LGU/BFP/DOLE schedule of fees for the project's location and scale — not a percentage; look up actual fee schedule.

### Worked Example
A 2-storey residential build has an estimated Sections II–XIII direct cost subtotal of ₱3,200,000.

| Item | Basis | Amount (₱) |
|---|---|---|
| Mobilization/Demobilization | 1.0% × 3,200,000 | 32,000 |
| Temporary Facilities & Enclosure | 1.5% × 3,200,000 | 48,000 |
| Safety & Health / PPE | 0.75% × 3,200,000 | 24,000 |
| Permits & Clearances | Lot (per LGU fee schedule) | 18,500 |
| **Section I Subtotal** | | **122,500** |

---

## Section II — Earthworks

### Scope
Structural excavation, backfill and compaction, granular bedding under footings/slabs, and soil poisoning (termite pre-treatment).

### Formulas
**Excavation volume** (rectangular pit, footing-by-footing):
$$V_{exc} = L \times W \times H \times N$$
where $L, W$ include a working clearance beyond the footing footprint (commonly +0.20 m to +0.30 m per side for formwork access), $H$ is excavation depth, $N$ is the count of identical footings.

**Backfill volume** — backfill is excavated volume minus the volume displaced by the footing/foundation itself, then increased for compaction shrinkage (loose-to-compacted soil requires more loose material than the void it fills):
$$V_{backfill} = (V_{exc} - V_{footing}) \times (1 + f_{shrinkage})$$
Typical shrinkage allowance: **15%–20%** for ordinary compacted fill (use 15% for sandy soil, 20% for clayey soil, higher for select fill imported to site).

**Gravel bedding**: bedding thickness (commonly 50 mm under slabs-on-grade, 100 mm under footings) applied over plan area:
$$V_{gravel} = A_{plan} \times t_{bedding}$$

**Soil poisoning**: measured per m² of the treated footprint (under slab and along foundation perimeter trench), priced per liter of chemical solution at a fixed application rate (commonly 5 L/m² for horizontal, 7.5 L/lin.m for vertical trench treatment — verify against product data sheet in use).

### Worked Example
Footing F-1: 1.2 m × 1.2 m × 0.40 m deep, qty 8, with 0.25 m working clearance per side.

- Excavation footprint: (1.2 + 0.5) × (1.2 + 0.5) = 1.70 m × 1.70 m
- $V_{exc}$ = 1.70 × 1.70 × 0.40 × 8 = **9.248 m³**
- Footing concrete volume (net): 1.2 × 1.2 × 0.40 × 8 = 4.608 m³
- $V_{backfill}$ = (9.248 − 4.608) × 1.18 = **5.475 m³** (18% shrinkage, mixed soil)
- Gravel bedding, 100 mm under footings: (1.2×1.2×8) × 0.10 = **1.152 m³**

| Item | Qty | Unit | Rate (₱) | Amount (₱) |
|---|---|---|---|---|
| Structural excavation | 9.248 | m³ | 350.00 | 3,236.80 |
| Structure backfill & compaction | 5.475 | m³ | 280.00 | 1,533.00 |
| Gravel bedding (100mm) | 1.152 | m³ | 1,650.00 | 1,900.80 |
| **Section II Subtotal** | | | | **6,670.60** |

---

## Section III — Concrete Works & Formworks

### Scope
Cast-in-place concrete for footings, columns, beams, slabs, and slab-on-grade; formwork/falsework contact-area takeoff.

### Mix Design Table (per 1.0 m³ finished concrete, 40 kg cement bags)
| Class | Ratio (cement:sand:gravel) | Cement (bags) | Sand (m³) | Gravel (m³) | Typical Use |
|---|---|---|---|---|---|
| AA | 1 : 1.5 : 3 | 12.0 | 0.50 | 1.00 | Watertight / pre-stressed elements |
| A | 1 : 2 : 4 | 9.0 | 0.50 | 1.00 | Footings, columns, beams, slabs |
| B | 1 : 2.5 : 5 | 7.5 | 0.50 | 1.00 | Slab-on-grade, pathways |
| C | 1 : 3 : 6 | 6.0 | 0.50 | 1.00 | Non-structural mass concrete |

### Geometry Formulas
- **Isolated footing**: $V_F = L \times W \times H \times N$
- **Column, net clear height**: $H_{clear} = H_{story} - t_{footing} - t_{slab}$
- **Beam, net clear span**: $L_{clear} = L_{grid} - \tfrac{w_{c1}}{2} - \tfrac{w_{c2}}{2}$
- **Wastage allowance**: +5% site-mixed batching, +3% ready-mix.

### Formwork Contact Area
- Footing: $A = 2(L+W) \times H \times N$
- Column: $A = 2(w+d) \times H_{clear} \times N$
- Beam (soffit + 2 sides): $A = (w + 2d) \times L_{clear} \times N$
- Material factors: Marine plywood ½" — **0.28 sheets/m²**; form lumber (2×2/2×3) — **7.0 bd.ft/m²**.

---

## Section IV — Masonry Works

### Scope
CHB wall units (100/150/200 mm), laying mortar, cell/core fill, and plastering.

### CHB Unit Count
$$N_{CHB} = A_{net} \times 12.5 \text{ pcs/m}^2$$

### Mortar & Cell Fill (Class B, 1:3, per m² of wall)
| CHB Thickness | Cement (bags/m²) | Sand (m³/m²) |
|---|---|---|
| 100 mm (4") | 0.522 | 0.0435 |
| 150 mm (6") | 1.010 | 0.0840 |
| 200 mm (8") | ≈1.35 | ≈0.112 |

### Plastering (per m² per face, 16 mm thick, Class B mortar)
Cement = 0.192 bags/m²/face, Sand = 0.016 m³/m²/face. For 20 mm thickness, multiply by 1.25.

---

## Section V — Metals & Steel Reinforcement

### Scope
Deformed rebar (footings, columns, beams, slabs), tie wire, structural steel shapes, and stainless handrails.

### PNS Theoretical Unit Weight
$$W_{kg/m} = \frac{d^2}{162.2}$$

### Cut Length Formulas
- **Footing mat bars**: $L_{cut} = L_{footing} - 2C_{cover} + 2H_{hook}$, with $C_{cover}$ = 75 mm, $H_{hook}$ = $12 d_b$.
- **Column main bars**: $L_{cut} = H_{story} + L_{splice} + L_{dowel}$, with $L_{splice} = 40 d_b$.
- **Beam stirrups (135° seismic hook)**: $L_{stirrup} = 2(w_{beam}-2C_{cover}) + 2(d_{beam}-2C_{cover}) + 2(10 d_b) - \Delta_{bend}$.
- **Tie wire**: 0.015 kg per kg of installed rebar (≈15 kg tie wire per metric ton).

---

## Section VI — Roofing & Ceiling Works
Pre-painted long-span roofing sheets ($A_{sheet} = A_{plan}/\cos\theta + 10\text{--}15\%$ lap), C-purlins, roof trusses, Hardiflex ceiling boards ($A_{\text{ceiling}} + 5\%$), and metal furring ($A_{\text{ceiling}} \times 2.5$).

---

## Section VII — Doors & Windows
Aluminum/glass window sets, tempered glass doors (+2% waste allowance), solid wooden panel doors, flush hollow-core doors, jamb lumber calculations.

---

## Section VIII — Tile & Flooring Works
Ceramic floor tiles ($600\times600$, $300\times300$, $+8\text{--}10\%$ waste), mortar bedding (20–25 mm 1:4 mix), tile grout ($0.35\text{--}0.45\text{ kg/m}^2$), plain cement finish.

---

## Section IX — Painting Works
Masonry 3-coat system (neutralizer $\rightarrow$ primer $\rightarrow$ 2 topcoats), ceiling flat latex, metal red oxide primer & enamel.

---

## Section X — Plumbing Works
UPVC sewer/sanitary pipe (+10% fittings allowance), PPR cold water distribution, fixture sets, septic vault & catch basins.

---

## Section XI — Electrical Works
Wire lengths per circuit (home-run distance + 10–15% drop/slack allowance), PVC conduits, duplex convenience outlets, LED panel fixtures, breaker sizing limits (80% continuous load).

---

## Section XII — Sanitary / Mechanical Works
Split-type inverter ACU sizing (~600–800 BTU/h per m²), refrigerant copper piping (+10% for bends/rises), testing & commissioning.

---

## Section XIII — Special Works
Stainless steel handrails (linear meter development), ACP canopy cladding (+8–10% cutting waste), elastomeric waterproofing (2–3 coats at 1.0–1.5 kg/m²).

---

## Appendix A — Cross-Cutting Estimating Principles
Net vs. gross measurement, trade-specific waste factors, discrete unit rounding up, direct vs. indirect cost separation, DPWH CMPD regional rate currency.

---

## Appendix B — Fajardo Deep Corner Cases, Void Deductions & Special Methodologies Manual

### B.1 Concrete Volume Deductions & Non-Standard Geometries

1. **Volume Intersections & Boundary Deduplications**:
   - **Column vs Footing**: Columns are measured starting from the top face of the footing ($H_{\text{column}} = H_{\text{floor}} - T_{\text{footing}} - T_{\text{slab}}$). The concrete volume inside the footing depth belongs strictly to the footing.
   - **Beam vs Column**: Beams are measured using net clear span between column faces ($L_{\text{clear}} = L_{\text{grid}} - \frac{W_{C1}}{2} - \frac{W_{C2}}{2}$). Column volume is continuous through the beam depth.
   - **Slab vs Beam**: Monolithic slab-and-beam construction measures slab area over clear beam pockets, or measures full slab thickness across the plan and deducts the slab thickness from the beam depth ($D_{\text{beam, net}} = D_{\text{beam, total}} - T_{\text{slab}}$).

2. **Trapezoidal & Battered Frustum Footings**:
   - For sloped/battered isolated footings (stepped or pyramidal frustum):
     $$V_{\text{frustum}} = \frac{h}{3} \cdot \left( A_1 + A_2 + \sqrt{A_1 \cdot A_2} \right)$$
     where $A_1 = L_1 \times W_1$ (bottom base area), $A_2 = L_2 \times W_2$ (top pedestal area), and $h$ is the sloped depth.

3. **Void Deduction Threshold Rule**:
   - In standard Philippine quantity surveying practice (Fajardo Chapter 1), pipe penetrations, small box sleeves, and embedded rebar voids under $0.10\text{ m}^3$ volume are **NOT deducted** from gross structural concrete volume due to displacement negligible impact and extra honeycombing batching waste.

---

### B.2 Rebar Fabrication, Lap Splices & Seismic Hooks

1. **Staggered Lap Splices**:
   - Class B tension lap splices ($40 \cdot d_b$) must be staggered by $50\%$ at alternate story levels. For a $20\text{mm}$ bar ($40 \times 20 = 800\text{mm}$ splice), 50% of the main bars splice at $500\text{mm}$ above floor slab, and 50% splice at $1,300\text{mm}$ above floor slab.

2. **Seismic 135° Stirrups vs Bend Shortening Deductions**:
   - 135° seismic hooks require $10 \cdot d_b$ extension per leg ($200\text{mm}$ total for $10\text{mm}$ rebar).
   - **Bend Shortening Deduction ($\Delta_{\text{bend}}$)**: Bending steel stretches the bar. Subtractions are made per bend:
     - 90° bend = subtract $2 \cdot d_b$ per bend.
     - 135° bend = subtract $3 \cdot d_b$ per bend.
     - For a 4-bend rectangular stirrup with 135° hooks: $\Delta_{\text{bend, total}} = 4 \times (3 \cdot d_b) = 12 \cdot d_b$ ($120\text{mm}$ subtraction for $10\text{mm}$ bar).

3. **Helical Spiral Column Reinforcement**:
   - For circular spiral columns:
     $$L_{\text{spiral}} = \pi \cdot D_{\text{core}} \cdot \sqrt{N_{\text{turns}}^2 + \left( \frac{H}{s} \right)^2}$$
     where $D_{\text{core}} = D_{\text{col}} - 2 C_{\text{cover}}$, $s$ is spiral pitch ($50\text{mm}\text{--}75\text{mm}$), and $H$ is clear height. Add $1.5 \text{ extra turns}$ top and bottom for anchorage.

4. **Temperature Bars & Torsion Mesh**:
   - Slabs-on-grade & suspended slabs require temperature bars perpendicular to main reinforcement:
     $$A_s = 0.0018 \cdot b \cdot d \quad (\text{Grade 60 steel}), \quad A_s = 0.0020 \cdot b \cdot d \quad (\text{Grade 40 steel})$$

---

### B.3 Masonry Opening Returns & Stiffener Columns

1. **Jamb Plaster Returns**:
   - When deducting window/door openings ($A_{\text{net}} = A_{\text{gross}} - \sum A_{\text{openings}}$), the exposed jamb perimeter requires additional plaster area:
     $$A_{\text{jamb return}} = 2 \cdot (W_{\text{opening}} + H_{\text{opening}}) \times t_{\text{wall}}$$
     Add $A_{\text{jamb return}}$ to total plastering area takeoff.

2. **RC Stiffener Columns in CHB Walls**:
   - Where RC stiffener columns ($150\text{mm} \times 150\text{mm}$) or lintel bond beams are embedded in CHB walls, deduct the stiffener column footprint from CHB count:
     $$N_{\text{CHB, net}} = \left( A_{\text{wall, gross}} - A_{\text{openings}} - A_{\text{stiffeners}} \right) \times 12.5\text{ pcs/m}^2$$

---

### B.4 Roofing, Tilework & Painting Multipliers

1. **Roofing Trims & Flashing Overlaps**:
   - Ridge rolls, valley rolls, hip caps, and eaves flashings are measured per linear meter + **15% lap allowance** ($150\text{mm}$ overlap per 2.4m commercial sheet length).

2. **45° Diagonal Tile Laying Waste**:
   - Diagonal 45° tile installation increases cutting waste from standard **8%** to **12%–15%** due to triangular corner cuts along all room perimeters.

3. **Rough Masonry Paint Primer Absorption**:
   - Unplastered CHB walls absorb **40%–50% more primer** than smooth troweled plaster. Adjust primer coverage rate from $10\text{ m}^2/\text{liter}$ down to $6.0\text{--}6.5\text{ m}^2/\text{liter}$.

---

## Appendix C — Hardware, Fasteners & Niche Specialty Trade Constants Manual

### C.1 Roofing Fasteners & Hardware
1. **Roofing Rivets & Lead Washers**:
   - Corrugated G.I. & long-span roofing sheets require **26 pcs of rivets & lead washers per m²** of roof slope area (spacing at every corrugated crown along purlin lines).
2. **G.I. Strap Fasteners**:
   - **1 pc G.I. strap per purlin-truss intersection** (typically $2\text{"} \times 3/16\text{"}$ flat bar strap).

---

### C.2 Scaffolding & Steel Framing Systems
1. **H-Frame Steel Scaffolding Sets**:
   - Standard $1.2\text{m} \times 1.7\text{m}$ H-Frame set (2 frames, 2 cross braces, 4 joint pins) covers **2.89 m² of vertical wall surface** per lift.
   - For story height $H = 3.2\text{m}$, allow **2 vertical lifts** per 1.8m horizontal run.

---

### C.3 Timber Stud Grids & Wood Finishes
1. **Wood Wall Studs & Ceiling Framing ($2\times2$ Lumber)**:
   - For $400\text{mm} \times 400\text{mm}$ grid spacing: **$1.875\text{ bd.ft / m}^2$**.
   - For $600\text{mm} \times 600\text{mm}$ grid spacing: **$1.250\text{ bd.ft / m}^2$**.
   - Add **10% framing waste** for corner studs and blocking.
2. **Wood Varnish & Clear Lacquer Finishes**:
   - 1 coat Sanding Sealer + 2 coats Clear Gloss Lacquer = **$1.0\text{ liter per } 8.0\text{ m}^2$** total 3-pass finish.

---

### C.4 Vinyl Tile Adhesives & Catch Basin Brickwork
1. **Vinyl Tile Contact Cement / Adhesive**:
   - Water-based vinyl adhesive = **$4.0\text{ m}^2 \text{ per liter}$** ($16.0\text{ m}^2 / \text{gallon}$).
2. **Drainage Catch Basin CHB / Brick Count**:
   - Standard $500\text{mm} \times 500\text{mm} \times 600\text{mm}$ deep catch basin: Requires **16 pcs $100\text{mm}$ CHB**, $0.25\text{ bags}$ cement, and 1 set Cast Iron / Galvanized Steel grating cover ($500\text{mm} \times 500\text{mm}$).
