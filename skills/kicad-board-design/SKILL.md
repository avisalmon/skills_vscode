---
name: kicad-board-design
description: >
  Design PCBs from idea to production using KiCad 9.x. Covers S-expression file generation,
  CLI-driven ERC/DRC verification, schematic capture, footprint assignment, and board layout.
  TRIGGER: user says "kicad", "pcb design", "schematic", "board layout", "erc", "drc",
  "footprint", "gerber", "pcb", or "kicad-cli".
---

# KiCad PCB Design  Complete Skill Reference

> **Purpose**: Standalone guide for an AI agent to design PCBs from idea to production using KiCad 9.x, text-based S-expression file generation, and CLI-driven verification. Every section contains copy-paste-ready code, conventions, and hard-won lessons.

---

## Table of Contents

1. [Master Workflow Checklist](#master-workflow-checklist)
2. [Environment & Installation](#environment--installation)
3. [KiCad File Formats](#kicad-file-formats)
4. [Project Structure](#project-structure)
5. [Schematic Design Workflow](#schematic-design-workflow)
6. [Components Reference (THT)](#components-reference-tht)
7. [ERC  Electrical Rules Check](#erc--electrical-rules-check)
8. [PCB Layout Workflow](#pcb-layout-workflow)
9. [Design Rules (JLCPCB)](#design-rules-jlcpcb)
10. [Copper Trace Routing](#copper-trace-routing)
11. [DRC  Design Rule Check](#drc--design-rule-check)
12. [3D Models](#3d-models)
13. [Production Output (Gerber/Drill)](#production-output-gerberdrill)
14. [Manufacturer Ordering (JLCPCB)](#manufacturer-ordering-jlcpcb)
15. [KiCad GUI Tips](#kicad-gui-tips)
16. [Common Circuit References](#common-circuit-references)
17. [Troubleshooting](#troubleshooting)
18. [Lessons Learned](#lessons-learned)

---

## Master Workflow Checklist

Follow these phases **in order** for every board. Each phase has a gate () that must pass before proceeding.

> **GUI-First Principle**: For spatial tasks (component placement, trace routing, footprint swaps, courtyard fixes), **always ask the user to do it in KiCad's GUI first**. The interactive router (push-and-shove mode) and drag-to-place are dramatically faster than editing S-expressions programmatically. The agent should:
> 1. Describe what needs to change (which components, which nets, target positions)
> 2. Ask the user to make the change in KiCad
> 3. Wait for the user to confirm completion
> 4. Re-read the file and run DRC to verify
>
> Only fall back to programmatic S-expression editing when: the user explicitly asks for it, the change is purely additive (3D models, new footprints), or the change is a bulk find-replace (e.g. net renaming).

### Phase 1  Project Setup
- [ ] Create project directory: `<project-name>/`
- [ ] Generate `<name>.kicad_pro` with design rules
- [ ] Generate `sym-lib-table` and `fp-lib-table`
- [ ] **Gate**: Files parse without error in KiCad

### Phase 2  Schematic
- [ ] Generate `<name>.kicad_sch` with all components, wires, power symbols
- [ ] Add PWR_FLAG on every power net driven by passive-pin connectors
- [ ] Add `no_connect` flags on unused pins
- [ ] **Gate**: `kicad-cli sch erc`  0 errors

### Phase 2.5  Wiring Report
- [ ] Generate `WIRING-REPORT.md` in project directory
- [ ] Include: GPIO assignment table, signal chain diagrams, pin defines for firmware
- [ ] User reviews and confirms circuit correctness before proceeding to PCB
- [ ] **Gate**: User confirms all connections match design intent

### Phase 3  PCB Layout
- [ ] Generate `<name>.kicad_pcb` with board outline, all footprints roughly placed
- [ ] **Ask user to arrange components in KiCad GUI** (drag, rotate, align  much faster than scripting)
- [ ] User confirms placement is done  agent re-reads file to sync positions
- [ ] Verify no courtyard overlaps
- [ ] **Gate**: `kicad-cli pcb drc`  0 errors (unconnected items expected at this stage)

### Phase 4  Trace Routing
- [ ] **Preferred: Ask user to route in KiCad GUI** (Interactive Router with push-and-shove mode)
  - Provide a net-by-net routing guide (which pads to connect, suggested layers)
  - User routes interactively  agent re-reads file and runs DRC to verify
  - For simple boards, user can also use Freerouting (export DSN  import SES)
- [ ] Fallback (programmatic): Extract pad positions, generate segment/via entries
  - Only if user explicitly requests scripted routing
  - Expect 35 DRC iterations per board
- [ ] **Gate**: `kicad-cli pcb drc`  0 errors, 0 unconnected items

### Phase 5  3D Models
- [ ] Insert `(model ...)` blocks for every component footprint
- [ ] User verifies in 3D Viewer (Alt+3)
- [ ] **Gate**: DRC still clean after model insertion

### Phase 6  Production Output
- [ ] Generate Gerber files (9 layers + job file)
- [ ] Generate Excellon drill file
- [ ] Create ZIP archive for manufacturer upload
- [ ] **Gate**: ZIP contains all required files, sizes are reasonable

### Phase 7  Order
- [ ] Upload ZIP to manufacturer (JLCPCB, PCBWay, etc.)
- [ ] Review quoted specs match design intent
- [ ] Place order

---

## Environment & Installation

### KiCad 9.x on Windows
```
Executable : %USERPROFILE%\AppData\Local\Programs\KiCad\9.0\bin\kicad-cli.exe
3D Models  : %USERPROFILE%\AppData\Local\Programs\KiCad\9.0\share\kicad\3dmodels\
Symbols    : %USERPROFILE%\AppData\Local\Programs\KiCad\9.0\share\kicad\symbols\
Footprints : %USERPROFILE%\AppData\Local\Programs\KiCad\9.0\share\kicad\footprints\
```

**KiCad is NOT on PATH.** Always use the full path or set it:
```powershell
$kicadBin = "%USERPROFILE%\AppData\Local\Programs\KiCad\9.0\bin"
$env:PATH += ";$kicadBin"
```

### Detecting KiCad Installation
```powershell
# Search common locations
$locations = @(
    "$env:LOCALAPPDATA\Programs\KiCad\*\bin\kicad-cli.exe",
    "$env:ProgramFiles\KiCad\*\bin\kicad-cli.exe"
)
$cli = Get-ChildItem $locations -ErrorAction SilentlyContinue | Sort-Object FullName -Descending | Select-Object -First 1
if ($cli) { Write-Host "Found: $($cli.FullName)" }
```

### CRITICAL: File Encoding
**ALL KiCad files MUST be UTF-8 without BOM.** KiCad's parser rejects files that start with a byte-order mark.

```powershell
# CORRECT  UTF-8 no BOM
[System.IO.File]::WriteAllText($filePath, $content, (New-Object System.Text.UTF8Encoding $false))

# WRONG  these add BOM or use wrong encoding
Set-Content -Path $filePath -Value $content  # Adds BOM in PowerShell 5.1
Out-File -FilePath $filePath -Encoding utf8   # Also adds BOM
```

**Use this pattern for every file write in the entire workflow.**

---

## KiCad File Formats

All KiCad 9.x files are **S-expression** text files.

| File | Format Version | Purpose |
|------|---------------|---------|
| `.kicad_pro` | `(kicad_sch (version 20231120))` | Project settings, design rules |
| `.kicad_sch` | `(kicad_sch (version 20250114))` | Schematic: symbols, wires, power |
| `.kicad_pcb` | `(kicad_pcb (version 20241229))` | PCB: footprints, traces, zones |
| `sym-lib-table` | `(sym_lib_table ...)` | Symbol library paths |
| `fp-lib-table` | `(fp_lib_table ...)` | Footprint library paths |

### UUID Generation
Every element needs a unique UUID. Use:
```powershell
(New-Guid).ToString()
```

### S-expression Tips
- KiCad reformats files on save (compact  multi-line). Parsers must handle both.
- Coordinates are in **millimeters**.
- Angles are in **degrees**, clockwise positive (screen Y-axis down).
- Net numbers are assigned sequentially starting from 0 (unconnected).

---

## Project Structure

```
<project-name>/
 <name>.kicad_pro          # Project file with design rules
 <name>.kicad_sch          # Schematic
 <name>.kicad_pcb          # PCB layout + routing
 sym-lib-table             # Symbol library references
 fp-lib-table              # Footprint library references
 output/
    gerbers/
        <name>-F_Cu.gtl        # Front copper
        <name>-B_Cu.gbl        # Back copper
        <name>-F_Mask.gts      # Front solder mask
        <name>-B_Mask.gbs      # Back solder mask
        <name>-F_SilkS.gto     # Front silkscreen
        <name>-B_SilkS.gbo     # Back silkscreen
        <name>-F_Paste.gtp     # Front paste
        <name>-B_Paste.gbp     # Back paste
        <name>-Edge_Cuts.gm1   # Board outline
        <name>.drl             # Drill file (Excellon)
        <name>-job.gbrjob      # Gerber job file
    <name>-gerbers.zip        # Production ZIP
```

---

## Schematic Design Workflow

### Step 1: Define the Circuit
List all components with reference designators, values, and connections (netlist).

### Step 2: Generate .kicad_sch

**Skeleton**:
```
(kicad_sch
    (version 20250114)
    (generator "copilot_gen")
    (generator_version "1.0")
    (uuid "<project-uuid>")
    (paper "A4")

    (lib_symbols
        ... all symbol definitions embedded here ...
    )

    ... symbol instances (components placed on sheet) ...
    ... wires connecting pins ...
    ... power symbols (VCC, GND) ...
    ... PWR_FLAG symbols ...
    ... no_connect flags ...
    ... labels ...

    (sheet_instances
        (path "/" (page "1"))
    )
)
```

### Step 3: Place Components
Each component is a `(symbol ...)` block:
```
(symbol
    (lib_id "Device:R")
    (at X Y rotation)
    (unit 1)
    (exclude_from_sim no)
    (in_bom yes)
    (on_board yes)
    (dnp no)
    (uuid "<uuid>")
    (property "Reference" "R1" (at rx ry rot) (effects (font (size 1.27 1.27))))
    (property "Value" "1k" (at vx vy rot) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal"
        (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
    (pin "1" (uuid "<uuid>"))
    (pin "2" (uuid "<uuid>"))
    (instances (project "<name>" (path "/<project-uuid>" (reference "R1") (unit 1))))
)
```

### Step 4: Draw Wires
```
(wire (pts (xy x1 y1) (xy x2 y2))
    (stroke (width 0) (type default))
    (uuid "<uuid>")
)
```

**Pin-to-wire alignment is CRITICAL**: Power symbol pins must touch wire endpoints exactly  no gaps, even 0.01mm.

### Step 5: Add Power Symbols
Use `power:VCC` and `power:GND` from the built-in power library. These symbols provide global net connections.

### Step 6: Add PWR_FLAG (Required)
**Every power net driven only by passive-pin connectors needs a PWR_FLAG.** Battery connectors and pin headers have passive pins that don't satisfy ERC's "power pin must be driven" requirement.

PWR_FLAG symbol definition (embed in `lib_symbols`):
```
(symbol "power:PWR_FLAG"
    (power)
    (pin_names (offset 0))
    (exclude_from_sim no)
    (in_bom yes)
    (on_board yes)
    (property "Reference" "#FLG" ...)
    (property "Value" "PWR_FLAG" ...)
    (symbol "PWR_FLAG_0_1"
        (pin power_out line (at 0 0 90) (length 0)
            (name "pwr" ...) (number "1" ...))
    )
)
```

Place instances: `#FLG01` on VCC net, `#FLG02` on GND net.

---

## Components Reference (THT)

Default to **through-hole (THT)** components for hobby projects.

### Common Components

| Component | Symbol Library | Footprint | Pin Count |
|-----------|---------------|-----------|-----------|
| Resistor | `Device:R` | `Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal` | 2 |
| Capacitor (ceramic) | `Device:C` | `Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P2.50mm` | 2 |
| Capacitor (electrolytic) | `Device:CP` | `Capacitor_THT:CP_Radial_D5.0mm_P2.50mm` | 2 (polarized: + is pin 1) |
| LED 5mm | `Device:LED` | `LED_THT:LED_D5.0mm` | 2 (A=pin 1, K=pin 2) |
| Potentiometer | `Device:R_Potentiometer` | `Potentiometer_THT:Potentiometer_Bourns_3296W_Vertical` | 3 (1=CCW, 2=wiper, 3=CW) |
| NE555 Timer | `Timer:NE555` | `Package_DIP:DIP-8_W7.62mm` | 8 |
| Pin Header 102 | `Connector_Generic:Conn_01x02` | `Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical` | 2 |
| Mounting Hole 3.2mm | `Mechanical:MountingHole` | `MountingHole:MountingHole_3.2mm_M3` | 0 (NPTH) |

### NE555 Pinout
| Pin | Name | Function |
|-----|------|----------|
| 1 | GND | Ground |
| 2 | TRIG | Trigger (< 1/3 VCC starts timing) |
| 3 | OUT | Output |
| 4 | RESET | Reset (active low, tie to VCC if unused) |
| 5 | CTRL | Control voltage (bypass to GND with 10nF) |
| 6 | THR | Threshold (> 2/3 VCC stops timing) |
| 7 | DISCH | Discharge (open collector) |
| 8 | VCC | Supply (4.516V) |

### Footprint Pad Coordinates (Local, Before Rotation)

| Footprint | Pad 1 | Pad 2 | Others |
|-----------|-------|-------|--------|
| DIP-8_W7.62mm | (0,0) | (0,2.54) | +2.54 each; right column at x=7.62 |
| R_Axial_P10.16mm | (0,0) | (10.16,0) | |
| CP_Radial_D5.0mm_P2.50mm | (0,0)+ | (2.5,0) | |
| C_Disc_D5.0mm_P2.50mm | (0,0) | (2.5,0) | |
| LED_D5.0mm | (0,0)A | (2.54,0)K | |
| PinHeader_1x02_P2.54mm | (0,0) | (0,2.54) | |
| Bourns_3296W_Vertical | (0,0) | (2.54,0) | (5.08,0) |

---

## ERC  Electrical Rules Check

### Running ERC
```powershell
& "$kicadBin\kicad-cli.exe" sch erc --output output/erc-report.rpt "$projectDir\$name.kicad_sch"
Get-Content output/erc-report.rpt | Select-String "violations|Error|errors"
```

### Common ERC Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| Power pin not connected | Pin not touching wire endpoint (even 0.01mm gap) | Add bridge wire segment |
| Power pin not driven | No `power_out` pin on net | Add PWR_FLAG symbol to that net |
| Symbol doesn't match library | Embedded symbol differs from installed lib | Cosmetic warning  safe to ignore |
| Library not configured | `lib_name` empty in embedded symbols | Create sym-lib-table or ignore |

### ERC Severity
- **Error**: Must fix before PCB layout
- **Warning**: Review, generally safe to proceed
- **Excluded**: Manually suppressed

### ERC Best Practices
1. Power symbol pins must touch wires **exactly**
2. Every power net needs PWR_FLAG when driven by passive connectors
3. Unused pins need `no_connect` flags
4. Create empty `sym-lib-table` to suppress "library not configured" warnings
5. Always re-run ERC after fixes  verify 0 errors before proceeding

---

## PCB Layout Workflow

### Step 1: Generate .kicad_pcb

**Skeleton**:
```
(kicad_pcb
    (version 20241229)
    (generator "copilot_gen")
    (generator_version "1.0")
    (general (thickness 1.6) (legacy_teardrops no))
    (paper "A4")
    (layers
        (0 "F.Cu" signal)
        (31 "B.Cu" signal)
        (32 "B.Adhes" user "B.Adhesive")
        (33 "F.Adhes" user "F.Adhesive")
        (34 "B.Paste" user)
        (35 "F.Paste" user)
        (36 "B.SilkS" user "B.Silkscreen")
        (37 "F.SilkS" user "F.Silkscreen")
        (38 "B.Mask" user "B.Mask")
        (39 "F.Mask" user "F.Mask")
        (40 "Dwgs.User" user "User.Drawings")
        (41 "Cmts.User" user "User.Comments")
        (42 "Eco1.User" user "User.Eco1")
        (43 "Eco2.User" user "User.Eco2")
        (44 "Edge.Cuts" user)
        (45 "Margin" user)
        (46 "B.CrtYd" user "B.Courtyard")
        (47 "F.CrtYd" user "F.Courtyard")
        (48 "B.Fab" user "B.Fabrication")
        (49 "F.Fab" user "F.Fabrication")
        (50 "User.1" user)
        (51 "User.2" user)
    )
    (setup
        (pad_to_mask_clearance 0)
        (allow_soldermask_bridges_in_footprints no)
        (pcbplotparams ...)
    )
    (net 0 "")
    (net 1 "VCC")
    (net 2 "GND")
    ... more nets ...

    ... footprints ...
    ... segments (traces) ...
    ... vias ...
)
```

### Step 2: Board Outline
```
(gr_rect
    (start X1 Y1)
    (end X2 Y2)
    (stroke (width 0.05) (type default))
    (fill none)
    (layer "Edge.Cuts")
    (uuid "<uuid>")
)
```

### Step 3: Place Footprints
Each component is a `(footprint ...)` block containing pads, silkscreen, courtyard, fab layer graphics, and a `(model ...)` block for 3D visualization.

**Key rules:**
- Spread components to avoid courtyard overlaps
- Allow 35mm spacing between components
- Keep power components near power connector
- Check actual library courtyard dimensions  they may be larger than expected
- DIP IC courtyards are wide: DIP-8 is ~10.3mm  10.5mm

### Step 4: Net Assignment
Every pad must be assigned to the correct net number matching the schematic. This is how the PCB knows which pads to connect with traces.

### Step 5: Verify Placement
```powershell
& "$kicadBin\kicad-cli.exe" pcb drc --output output/drc-report.rpt "$projectDir\$name.kicad_pcb"
```

Expect at this stage:
- 0 errors (courtyard overlaps = errors if present)
- N unconnected items (expected  routing not done yet)
- Cosmetic warnings (safe to ignore)

### Step 6: User Adjustment
User may open the board in KiCad and move components. After they save:
- File will be reformatted (multi-line S-expressions)
- Re-read the file before making further edits
- Use `File  Revert` in KiCad after external edits

---

## Design Rules (JLCPCB)

Use these rules by default for all hobby boards:

```
Minimum trace width:     0.2mm (0.127mm capability, 0.2mm recommended)
Minimum clearance:       0.2mm
Minimum via diameter:    0.45mm (0.6mm recommended)
Minimum via drill:       0.3mm
Minimum hole size:       0.3mm
Board thickness:         1.6mm
Copper layers:           2 (F.Cu + B.Cu)
Min annular ring:        0.13mm
Trace width (signal):    0.25mm
Trace width (power):     0.5mm
Via size used:           0.6mm outer / 0.3mm drill
Hole clearance:          0.25mm from NPTH edges
```

### Netclass Configuration (in .kicad_pro)
```json
"net_settings": {
    "classes": [{
        "name": "Default",
        "clearance": 0.2,
        "track_width": 0.2,
        "via_diameter": 0.6,
        "via_drill": 0.3
    }]
}
```

---

## Copper Trace Routing

### Process Overview
1. **Extract** pad absolute positions (apply footprint rotation with CW convention)
2. **Plan** routes net-by-net, checking same-layer crossings exhaustively **before** generating
3. **Generate** segment/via entries
4. **Insert** before closing `)` of .kicad_pcb
5. **Run DRC**, fix errors, repeat until 0 errors / 0 unconnected

### KiCad Rotation Convention (CRITICAL)
KiCad uses **clockwise** rotation (screen Y-axis points down):
```
x' = xcos(θ) + ysin(θ)
y' = xsin(θ) + ycos(θ)
```
Where θ is the footprint's rotation angle in degrees.

**Example**: D1 at (147,95) rot=90, pad 2 local offset (2.54,0)
 absolute = (147 + 0, 95  2.54) = (147, 92.46)  NOT (147, 97.54)

### Segment Format
```
(segment (start X1 Y1) (end X2 Y2) (width W) (layer "F.Cu") (net N) (uuid "<uuid>"))
```

### Via Format
```
(via (at X Y) (size 0.6) (drill 0.3) (layers "F.Cu" "B.Cu") (net N) (uuid "<uuid>"))
```

### Routing Rules
| Net Type | Width | Layer |
|----------|-------|-------|
| Power (VCC/GND) | 0.5mm | Prefer F.Cu, use B.Cu for crossings |
| Signal | 0.25mm | Any, avoid crossings |

### Key Techniques

**THT Pad Multi-Layer Connections:**
Through-hole pads connect on ALL copper layers. You can route B.Cu directly to THT pads without vias. This is fundamental for 2-layer routing.

**Inside-DIP Routing:**
Route B.Cu traces between DIP pin rows. DIP-8 rows are 7.62mm apart  plenty of room. Keep trace centerline 1.0mm from pad centers on both rows.

**Layer Jumping:**
When two nets must cross on the same layer, use a via pair to jump one trace to B.Cu:
```
via  B.Cu segment  via (back to F.Cu)
```

**Power Bus Patterns:**
- GND bus below components: Route at Y offset below lowest component pads to avoid shorts
- VCC spine above components: Route at Y offset above highest component pads
- Branch from bus to individual pads at specific X positions

**Pad Avoidance:**
THT pad annular rings extend ~0.8mm from center. B.Cu traces within this radius short to the pad's net. Always route B.Cu traces 1.0mm from any THT pad center (unless intentionally connecting).

### Common Routing Pitfalls

| Pitfall | Description | Prevention |
|---------|-------------|------------|
| Pad rotation errors | Forgot CW convention when calculating absolute coords | Always use rotation formula |
| THT pad shorts on B.Cu | B.Cu trace passes through THT annular ring | Keep B.Cu traces 1.0mm+ from pad centers |
| Via floating | Via not touching any trace | Place via exactly on trace endpoint |
| NPTH keepout | Trace too close to mounting hole | Route well clear (check drill radius + 0.25mm) |
| DIP inside clearance | Trace between DIP pins too close to pad | Keep 1.0mm from pad centers |
| Same-layer crossing | Two different-net traces intersect | Move one to other layer with via pair |

### Scripted Routing Workflow

**Strip and Regenerate**: Easier to remove ALL segments/vias and regenerate than to edit individual traces.
```powershell
# Remove old routing
$pcb = Get-Content $pcbFile -Raw
$pcb = $pcb -replace '(?m)^\s*\(segment\s.*?\)\s*$', ''
$pcb = $pcb -replace '(?m)^\s*\(via\s.*?\)\s*$', ''
# Remove blank lines left behind
$pcb = $pcb -replace '(\r?\n){3,}', "`n`n"
```

**UUID Scheme**: Use sequential fake UUIDs (e.g., `e0000000-0000-0000-0000-000000000001`). KiCad reassigns real UUIDs on save.

**Insert Location**: Append all segments/vias before the final `)` in the .kicad_pcb file.

**Expect 35 DRC iterations** per board. This is normal. Each iteration fixes a category of errors.

### Iterative DRC Fix Patterns

| DRC Error | Root Cause | Fix |
|-----------|-----------|-----|
| `shorting_items` (B.Cu + THT pad) | B.Cu trace within 0.8mm of THT pad center | Reroute B.Cu to avoid annular ring |
| `clearance` (trace + pad) | Trace within 0.2mm of pad edge | Move trace farther (usually 1mm+ extra) |
| `hole_clearance` (trace + NPTH) | Trace within 0.25mm of mounting hole | Route around with margin |
| `tracks_crossing` (same layer) | Two different-net traces intersect | Move one to B.Cu via layer jump |
| `solder_mask_bridge` | Secondary effect of a short | Fix the underlying short first |

---

## DRC  Design Rule Check

### Running DRC
```powershell
& "$kicadBin\kicad-cli.exe" pcb drc --output output/drc-report.rpt "$projectDir\$name.kicad_pcb"
Get-Content output/drc-report.rpt
```

### Interpreting Results
- **Errors**: Must fix (shorts, clearance violations, unconnected items)
- **Warnings**: Generally cosmetic, review each
- **Unconnected items**: All nets must show 0 unconnected after routing

### Permanent Warning Baseline (Normal)
These warnings appear on every board and are safe to ignore:
- `lib_footprint_mismatch`  embedded footprints differ from library (1 per footprint)
- `silk_over_copper`  silkscreen overlaps solder pads (manufacturer handles)
- `silk_overlap`  silkscreen text overlaps other silkscreen (visual only)
- `silk_edge_clearance`  silkscreen near board edge

**Typical baseline**: ~23 cosmetic warnings for a 10-component board.

---

## 3D Models

### Why Needed
KiCad's 3D Viewer (Alt+3) only shows component shapes if each footprint has a `(model ...)` block. Generated footprints often omit this  board renders as bare PCB.

### Model Block Format
Insert inside each `(footprint ...)` block, before `(embedded_fonts no)`:
```
(model "${KICAD9_3DMODEL_DIR}/Library.3dshapes/ModelName.wrl"
    (offset (xyz 0 0 0))
    (scale (xyz 1 1 1))
    (rotate (xyz 0 0 0))
)
```

### Common THT Component Model Paths

| Component | Model Path |
|-----------|-----------|
| DIP-8 IC | `Package_DIP.3dshapes/DIP-8_W7.62mm.wrl` |
| Resistor (axial, P10.16) | `Resistor_THT.3dshapes/R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal.wrl` |
| Disc capacitor (D5.0, P2.5) | `Capacitor_THT.3dshapes/C_Disc_D5.0mm_W2.5mm_P2.50mm.wrl` |
| Electrolytic cap (D5.0, P2.5) | `Capacitor_THT.3dshapes/CP_Radial_D5.0mm_P2.50mm.wrl` |
| LED 5mm | `LED_THT.3dshapes/LED_D5.0mm.wrl` |
| Bourns 3296W pot | `Potentiometer_THT.3dshapes/Potentiometer_Bourns_3296W_Vertical.wrl` |
| Pin header 102 | `Connector_PinHeader_2.54mm.3dshapes/PinHeader_1x02_P2.54mm_Vertical.wrl` |
| Mounting hole 3.2mm | No 3D model needed |

### 3D Model Library Location
- **Windows**: `%USERPROFILE%\AppData\Local\Programs\KiCad\9.0\share\kicad\3dmodels\`
- **Variable** (use in PCB files): `${KICAD9_3DMODEL_DIR}`
- **Format**: Use `.wrl` (VRML)  universally supported. `.step` also available for MCAD export.

### Bulk Model Insertion Script Pattern
```powershell
# Define ref  model path mapping
$models = @{
    "U1"  = '${KICAD9_3DMODEL_DIR}/Package_DIP.3dshapes/DIP-8_W7.62mm.wrl'
    "R1"  = '${KICAD9_3DMODEL_DIR}/Resistor_THT.3dshapes/R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal.wrl'
    # ... etc
}

# For each footprint, find (property "Reference" "XX") and insert model block before (embedded_fonts no)
foreach ($ref in $models.Keys) {
    $modelBlock = @"
        (model "$($models[$ref])"
            (offset (xyz 0 0 0))
            (scale (xyz 1 1 1))
            (rotate (xyz 0 0 0))
        )
"@
    # Insert into footprint via regex or string matching
}
```

---

## Wiring Report Format

After the schematic passes ERC, generate a `WIRING-REPORT.md` in the project directory. This serves as:
1. **Verification**  human reviews every connection before committing to PCB
2. **Programming guide**  firmware developers use it as pin reference
3. **Documentation**  permanent record of the design intent

### Required Sections

`markdown
# <Project Name>  Wiring Report

## Board Overview
Table: MCU, peripherals, power source, mounting

## GPIO Assignment Table
| GPIO | Direction | Component | Function | Arduino Pin |

## Detailed Signal Chains
For each subsystem (buttons, display, LEDs, etc.):
- ASCII art wiring diagram showing full path
- Firmware notes (pull mode, I2C address, PWM channel, etc.)

## MCU Socket/Connector Pinout
Pin-by-pin table for every MCU connector showing:
| Pin # | MCU Pin Name | Net | Used By |

## Power Distribution
ASCII diagram showing power flow from source to all loads

## Quick-Start Firmware Defines
Copy-paste-ready #define block with all pin assignments

## Verification Checklist
- [ ] Checkbox per subsystem for human sign-off
`

### Key Rules
- Extract ALL data from the schematic  never guess pin assignments
- Include firmware-relevant notes (active HIGH/LOW, I2C addresses, PWM requirements)
- Flag GPIO limitations (e.g., GPIO34/35 = input only, GPIO6-11 = flash pins)
- Note any pin conflicts or shared buses
- The report must be reviewable WITHOUT opening KiCad

---

## Production Output (Gerber/Drill)

### Pre-Production Checklist
- [ ] DRC: 0 errors, 0 unconnected
- [ ] All nets routed
- [ ] Board outline on Edge.Cuts layer
- [ ] 3D model verification (optional but recommended)

### Generate Gerber Files (All 9 Layers)
```powershell
$pcbFile = "$projectDir\$name.kicad_pcb"
$gerberDir = "$projectDir\output\gerbers"
New-Item -ItemType Directory -Force -Path $gerberDir | Out-Null

$layers = @("F.Cu","B.Cu","F.Paste","B.Paste","F.SilkS","B.SilkS","F.Mask","B.Mask","Edge.Cuts")

& "$kicadBin\kicad-cli.exe" pcb export gerbers `
    --output "$gerberDir\" `
    --layers ($layers -join ',') `
    --subtract-soldermask `
    --no-x2 `
    --use-drill-file-origin `
    $pcbFile
```

### Generate Drill File (Excellon)
```powershell
& "$kicadBin\kicad-cli.exe" pcb export drill `
    --output "$gerberDir\" `
    --format excellon `
    --excellon-units mm `
    --generate-map `
    --map-format gerberx2 `
    $pcbFile
```

### Create Production ZIP
```powershell
$zipPath = "$projectDir\output\$name-gerbers.zip"
if (Test-Path $zipPath) { Remove-Item $zipPath }
Compress-Archive -Path "$gerberDir\*" -DestinationPath $zipPath
Write-Host "Created: $zipPath ($(Get-Item $zipPath | Select-Object -Expand Length) bytes)"
```

### Expected Output Files
| File Extension | Layer | Purpose |
|---------------|-------|---------|
| `.gtl` | F.Cu | Front copper traces |
| `.gbl` | B.Cu | Back copper traces |
| `.gts` | F.Mask | Front solder mask openings |
| `.gbs` | B.Mask | Back solder mask openings |
| `.gto` | F.SilkS | Front silkscreen (labels) |
| `.gbo` | B.SilkS | Back silkscreen |
| `.gtp` | F.Paste | Front solder paste |
| `.gbp` | B.Paste | Back solder paste |
| `.gm1` | Edge.Cuts | Board outline |
| `.drl` |  | Drill file (all holes) |
| `.gbrjob` |  | Gerber job metadata |

### Sanity Checks
- ZIP should be 520 KB for a simple 2-layer board
- F.Cu and B.Cu files should have content (not 0 bytes unless single-layer)
- Edge.Cuts must exist (defines board shape for manufacturer)
- Drill file must exist (defines all holes)

---

## Manufacturer Ordering (JLCPCB)

### Order Process (Manual  No Public API)
1. Go to **https://order.jlcpcb.com/quote**
2. Click **"Add Gerber File"**  upload the production ZIP
3. JLCPCB auto-detects:
   - Board dimensions
   - Layer count
   - Drill holes
4. Review/adjust settings:
   - **PCB Qty**: 5 (minimum)
   - **Layers**: 2
   - **Thickness**: 1.6mm
   - **PCB Color**: Green (cheapest, fastest)
   - **Surface Finish**: HASL (lead-free recommended)
   - **Remove Order Number**: "Specify a location" or "Yes" (extra cost)
5. Click **"Save to Cart"**  Checkout

### JLCPCB Specs for Reference
| Parameter | Capability | Our Design |
|-----------|-----------|------------|
| Min trace width | 0.127mm (5mil) | 0.25mm  |
| Min clearance | 0.127mm | 0.2mm  |
| Min via drill | 0.2mm | 0.3mm  |
| Min hole size | 0.2mm | 0.3mm  |
| Board thickness | 0.42.4mm | 1.6mm  |
| Layers | 132 | 2  |

### Cost Expectations (20242025)
- 5 simple 2-layer boards: ~$25 USD
- Shipping (economy): ~$13 USD
- Total: ~$58 USD typical
- Lead time: 13 days manufacture + shipping

---

## KiCad GUI Tips

### Essential Shortcuts
| Action | Shortcut |
|--------|----------|
| 3D Viewer | **Alt+3** |
| Refresh/Reload | **Ctrl+R** or **File  Revert** |
| Zoom to fit | **Home** |
| Route trace | **X** |
| Move component | **M** |
| Rotate component | **R** |
| Flip to back | **F** |
| Properties dialog | **E** |
| Run DRC | **Inspect  Design Rules Checker** |
| Run ERC | **Inspect  Electrical Rules Checker** |

### After External Edits
When the AI modifies `.kicad_pcb` or `.kicad_sch` files externally:
1. In KiCad: **File  Revert** (reloads from disk)
2. If Revert not available: close and reopen the file
3. **Do NOT have the file open for editing** while the AI writes to it

### 3D Viewer
- **Alt+3** opens 3D view from PCB editor
- Only shows component shapes if `(model ...)` blocks are present
- Raytracing mode: **Preferences  Render Settings  Raytracing** (slower but photorealistic)
- Use `.wrl` models for best compatibility

---

## Common Circuit References

### 555 Astable Multivibrator (LED Blinker)
**Frequency**: `f = 1.44 / ((R1 + 2R2)  C1)`
**Duty Cycle**: `D = (R1 + R2) / (R1 + 2R2)`

**Variable speed** with potentiometer:
- Replace R2 with potentiometer wiper (pin 2) to CW terminal (pin 3)
- Pot value sets R2 range  variable frequency
- RV1=100kΩ, R1=1kΩ, C1=10µF  ~0.714 Hz range

**Schematic connections**:
```
VCC  R1  (DISCH, R2/pot)  (TRIG=THR)  C1  GND
RESET tied to VCC
CTRL bypassed to GND via 10nF cap
OUT  R_LED  LED  GND
```

**Typical BOM**:
| Ref | Value | Purpose |
|-----|-------|---------|
| U1 | NE555 | Timer IC |
| R1 | 1kΩ | Timing (charge path) |
| R2 | 220Ω | LED current limiter |
| RV1 | 100kΩ pot | Variable frequency |
| C1 | 10µF electrolytic | Timing capacitor |
| C2 | 10nF ceramic | Control voltage bypass |
| D1 | Red LED 5mm | Output indicator |
| J1 | 2-pin header | Power input (512V) |

---

## Troubleshooting

### KiCad CLI Not Found
```powershell
# Search for it
Get-ChildItem "$env:LOCALAPPDATA\Programs\KiCad\*\bin\kicad-cli.exe" -ErrorAction SilentlyContinue
Get-ChildItem "$env:ProgramFiles\KiCad\*\bin\kicad-cli.exe" -ErrorAction SilentlyContinue
```

### UTF-8 BOM Errors
**Symptom**: KiCad won't open the file, parser error on first character.
**Fix**: Rewrite with `UTF8Encoding($false)`:
```powershell
$content = [System.IO.File]::ReadAllText($path)
[System.IO.File]::WriteAllText($path, $content, (New-Object System.Text.UTF8Encoding $false))
```

### UUID Conflicts
**Symptom**: KiCad warns about duplicate UUIDs.
**Fix**: Ensure every `(uuid "...")` in the file is unique. Use `(New-Guid).ToString()`.

### File Won't Reload in KiCad
**Fix**: File  Revert, or close and reopen. KiCad caches file contents.

### ERC Shows Errors After Clean Run
**Cause**: Edits introduced coordinate misalignment. Power pins shifted off wires.
**Fix**: Verify all wire endpoints match pin positions exactly.

### DRC Shows Shorts After Routing
**Cause**: B.Cu traces passing through THT pad annular rings.
**Fix**: Move B.Cu traces 1.0mm from THT pad centers. This is the #1 routing bug.

### Gerber Files Are 0 Bytes
**Cause**: Layer has no content (e.g., B.SilkS on a board with no back silkscreen).
**Fix**: Normal for unused layers. Manufacturer ignores empty layers.

### KiCad Reformats File on Save
**Symptom**: Compact S-expressions become multi-line after user saves in KiCad GUI.
**Fix**: This is expected behavior. Read the file fresh before making further edits. Do not diff-match against previous version.

---

## Lessons Learned

### Hard-Won Rules (Violating These Causes Failures)

1. **UTF-8 BOM kills everything**  use `UTF8Encoding($false)` for EVERY file write
2. **THT pads short on ALL layers**  B.Cu trace through annular ring = short. #1 routing bug.
3. **Power pins must touch wires exactly**  0.01mm gap = ERC error
4. **PWR_FLAG required** on passive-connector power nets  ERC won't pass without it
5. **35 DRC iterations is normal**  don't try to get routing perfect on first attempt
6. **KiCad reformats on save**  always re-read files after user interaction
7. **Solder mask bridge errors follow shorts**  fix the short, mask error disappears
8. **Courtyard dimensions vary**  check actual library footprints, don't estimate
9. **CW rotation convention**  wrong formula = pads in wrong position = broken routing

### Workflow Efficiency
- **Spatial edits in KiCad GUI are 10x faster** than programmatic S-expression editing
- For routing, placement, footprint swaps: describe the change, let user do it in GUI, then verify with DRC
- Programmatic editing is best for: initial file generation, bulk additive changes (3D models), net renaming
- After user edits in GUI, always re-read the file  KiCad reformats and may change UUIDs

### Performance Tips
- Strip and regenerate ALL routing rather than editing individual traces
- Use sequential fake UUIDs  KiCad fixes them on save
- Check DRC after every routing change, not just at the end
- Parse DRC report programmatically to classify error types

### Cosmetic Warning Baseline
A typical 10-component THT board has ~23 permanent cosmetic warnings:
- ~11 `lib_footprint_mismatch` (embedded vs library)
- ~11 `silk_over_copper` (silkscreen over pads)
- ~1 `silk_overlap` (text overlap)

All are safe to ignore. **Only zero-error and zero-unconnected matter.**

---

*Last updated: ESP32 Arcade session. Added GUI-First Principle and Wiring Report format as standard workflow phase.*