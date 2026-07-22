# Plan2Takeoff V2 — Sample Solved Cases & Methodological Knowledge Base

> **Companion Reference to**: [`tech_spec_v2.md`](file:///e:/Users/Louis/Documents/boq_system_v2/tech_spec_v2.md)  
> **Status**: Verified Formula Extraction & V2 Baseline Knowledge Base

---

## 1. Concrete Works Module (Chapter 1)

### 1.1 Mathematical Principles & Proportions
Solid concrete volume is calculated as $V = L \times W \times H \times N$ ($m^3$).
Material breakdown relies on standard cement bag factors ($40\text{ kg}$ Portland Cement standard):

| Concrete Class | Mix Ratio (Cement:Sand:Gravel) | Cement (Bags / $m^3$) | Sand ($m^3 / m^3$) | Gravel ($m^3 / m^3$) | Standard Application |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Class AA** | 1 : 1.5 : 3 | 12.00 | 0.50 | 1.00 | Underwater, pre-stressed, heavy structural elements |
| **Class A** | 1 : 2 : 4 | 9.00 | 0.50 | 1.00 | Isolated Footings, Columns, Beams, Suspended Slabs |
| **Class B** | 1 : 2.5 : 5 | 7.50 | 0.50 | 1.00 | Slab-on-grade, non-structural floor topping |
| **Class C** | 1 : 3 : 6 | 6.00 | 0.50 | 1.00 | Mass concrete, planter boxes, non-bearing fill |

---

### 1.2 Solved Case Study 1.1 — Isolated Footing ($F-1$) Concrete Takeoff
* **Problem**: Compute concrete volume and material requirements for 4 isolated footings ($F-1$) with dimensions $L = 1.50\text{ m}$, $W = 1.50\text{ m}$, $T = 0.40\text{ m}$, Class A concrete mix.

* **Step-by-Step Derivation**:
  1. Volume per footing: $V_{\text{single}} = 1.50 \times 1.50 \times 0.40 = 0.90\text{ m}^3$
  2. Total volume ($N=4$): $V_{\text{total}} = 0.90 \times 4 = 3.60\text{ m}^3$
  3. Cement Bags (Class A): $3.60 \times 9.00 = 32.40\text{ bags} \xrightarrow{} \mathbf{33\text{ bags}}$
  4. Fine Aggregate (Sand): $3.60 \times 0.50 = \mathbf{1.80\text{ m}^3}$
  5. Coarse Aggregate (Gravel): $3.60 \times 1.00 = \mathbf{3.60\text{ m}^3}$

---

### 1.3 Solved Case Study 1.2 — Rectangular Column ($C-1$) Clear Height Volume
* **Problem**: Compute concrete volume for 4 ground-floor columns ($C-1$, $400\text{mm} \times 400\text{mm}$) supporting a $3.20\text{ m}$ story height with $0.40\text{ m}$ footing depth and $0.15\text{ m}$ slab thickness.

* **Step-by-Step Derivation**:
  1. Net Clear Height: $H_{\text{clear}} = 3.20 - 0.15 = 3.05\text{ m}$
  2. Single Column Volume: $V_{\text{single}} = 0.40 \times 0.40 \times 3.05 = 0.488\text{ m}^3$
  3. Total Column Volume ($N=4$): $V_{\text{total}} = 0.488 \times 4 = 1.952\text{ m}^3$
  4. Class A Cement: $1.952 \times 9.00 = 17.568 \xrightarrow{} \mathbf{18\text{ bags}}$
  5. Sand: $1.952 \times 0.50 = \mathbf{0.976\text{ m}^3}$
  6. Gravel: $1.952 \times 1.00 = \mathbf{1.952\text{ m}^3}$

---

## 2. Steel Reinforcement Module (Chapter 2)

### 2.1 Theoretical Unit Weights (PNS 49 / ASTM A615)
Unit Weight Formula: $W_{\text{kg/m}} = \frac{d^2}{162.2}$

| Diameter ($d_b$) | Unit Weight ($kg/m$) | 6.0m Commercial Bar ($kg$) | 9.0m Commercial Bar ($kg$) | 12.0m Commercial Bar ($kg$) |
| :---: | :---: | :---: | :---: | :---: |
| **10 mm** | 0.617 | 3.702 | 5.553 | 7.404 |
| **12 mm** | 0.888 | 5.328 | 7.992 | 10.656 |
| **16 mm** | 1.578 | 9.468 | 14.202 | 18.936 |
| **20 mm** | 2.466 | 14.796 | 22.194 | 29.592 |
| **25 mm** | 3.853 | 23.118 | 34.677 | 46.236 |

---

### 2.2 Solved Case Study 2.1 — Footing Mat Rebar Weight
* **Problem**: Isolated Footing $F-1$ ($1.50\text{ m} \times 1.50\text{ m}$) reinforced with $16\text{mm}$ bars both ways spaced at $150\text{mm}$ O.C. Concrete cover = $75\text{mm}$, hook length = $12 \cdot d_b$.

* **Step-by-Step Derivation**:
  1. Net bar length: $L_{\text{net}} = 1.50 - (2 \times 0.075) = 1.35\text{ m}$
  2. Hook length (2 ends): $2 \times (12 \times 0.016) = 0.384\text{ m}$
  3. Total cut length per bar: $L_{\text{cut}} = 1.35 + 0.384 = 1.734\text{ m}$
  4. Number of bars per direction: $N_{\text{dir}} = \frac{1.35}{0.150} + 1 = 10\text{ bars}$
  5. Total bars per footing (both ways): $10 \times 2 = 20\text{ bars}$
  6. Total linear meters ($N=4$ footings): $20 \times 1.734 \times 4 = 138.72\text{ m}$
  7. Rebar Weight ($16\text{mm}$): $138.72 \times 1.578 = \mathbf{218.90\text{ kg}}$

---

### 2.3 Solved Case Study 2.2 — Beam Seismic Stirrups (135° Hooks)
* **Problem**: Rectangular beam ($2B-1$, $300\text{mm} \times 500\text{mm}$, clear span $L_{\text{clear}} = 5.0\text{ m}$) reinforced with $10\text{mm}$ stirrups. Clear cover = $40\text{mm}$.

* **Step-by-Step Derivation**:
  1. Stirrup width: $w_{\text{stirrup}} = 0.30 - (2 \times 0.04) = 0.22\text{ m}$
  2. Stirrup depth: $d_{\text{stirrup}} = 0.50 - (2 \times 0.04) = 0.42\text{ m}$
  3. 135° Seismic Hook Allowance (2 hooks): $2 \times (10 \times 0.010) = 0.20\text{ m}$
  4. Total Cut Length per stirrup: $L_{\text{stirrup}} = 2(0.22 + 0.42) + 0.20 = 1.48\text{ m}$
  5. Stirrup Spacing Rule (DPWH standard): 1 at 50mm, 4 at 100mm, 8 at 150mm, rest at 200mm. Total stirrups per beam = 26 pcs.
  6. Total stirrup weight ($N=2$ beams): $26 \times 2 \times 1.48 \times 0.617 = \mathbf{47.50\text{ kg}}$

---

### 2.4 Tie Wire Formula (#16 G.I. Wire)
* **Formula**: $M_{\text{wire}} = M_{\text{rebar, total}} \times 0.015\text{ kg/kg}$ ($15\text{ kg}$ per metric ton of steel).

---

## 3. Masonry & Plastering Module (Chapter 3)

### 3.1 Masonry Factors per $1.0\text{ m}^2$ Net Surface Area

* **CHB Unit Count**: Constant **$12.50\text{ pcs/m}^2$** for both $100\text{mm}$ ($4"$) and $150\text{mm}$ ($6"$) CHB.
* **Class B Laying Mortar (1:3 Ratio)**:
  - **$100\text{mm}$ CHB Wall**: Cement = $0.522\text{ bags/m}^2$, Sand = $0.0435\text{ m}^3/\text{m}^2$.
  - **$150\text{mm}$ CHB Wall**: Cement = $1.010\text{ bags/m}^2$, Sand = $0.0840\text{ m}^3/\text{m}^2$.
* **Class B Plastering ($16\text{mm}$ Thickness per face)**:
  - Cement = $0.192\text{ bags/m}^2/\text{face}$, Sand = $0.016\text{ m}^3/\text{m}^2/\text{face}$.

---

### 3.2 Solved Case Study 3.1 — Exterior Wall CHB & Plastering
* **Problem**: $150\text{mm}$ CHB exterior wall ($L = 12.0\text{ m}$, $H = 3.20\text{ m}$) with 2 window openings ($1.50\text{m} \times 1.50\text{m}$ each). Plastered on both faces.

* **Step-by-Step Derivation**:
  1. Gross Wall Area: $A_{\text{gross}} = 12.0 \times 3.20 = 38.40\text{ m}^2$
  2. Opening Deductions: $A_{\text{openings}} = 2 \times (1.50 \times 1.50) = 4.50\text{ m}^2$
  3. Net Wall Area: $A_{\text{net}} = 38.40 - 4.50 = 33.90\text{ m}^2$
  4. CHB Count: $33.90 \times 12.50 = 423.75 \xrightarrow{} \mathbf{424\text{ pcs}}$
  5. Laying Mortar Cement: $33.90 \times 1.010 = \mathbf{34.24\text{ bags}}$
  6. Laying Mortar Sand: $33.90 \times 0.0840 = \mathbf{2.85\text{ m}^3}$
  7. Plaster Cement (2 faces): $33.90 \times (2 \times 0.192) = \mathbf{13.02\text{ bags}}$
  8. Plaster Sand (2 faces): $33.90 \times (2 \times 0.016) = \mathbf{1.08\text{ m}^3}$

---

## 4. Formworks Module (Chapter 4)

### 4.1 Surface Contact Area Ratios
* **Footing Forms**: Surface area of perimeter faces = $2(L + W) \times H \times N$.
* **Column Forms**: Contact area = $2(W + D) \times H_{\text{clear}} \times N$.
* **Beam Forms (Bottom & 2 Sides)**: Area = $(W + 2D) \times L_{\text{clear}} \times N$.
* **Plywood Ratios**: Marine Plywood $1/2" = 0.28\text{ sheets/m}^2$ contact area.
* **Lumber Ratios**: Form Lumber ($2\times2 / 2\times3$) = $7.0\text{ bdft/m}^2$ contact area.

---

*Sample Solved Cases Reference Document — Verified V1 Baseline for V2 Implementation.*
