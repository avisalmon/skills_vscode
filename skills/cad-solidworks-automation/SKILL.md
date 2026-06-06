---
name: CAD SolidWorks Automation
description: >
  Help engineers automate CAD workflows with SolidWorks macros and API patterns:
  parts, sketches, dimensions, equations, configurations, drawings, assemblies,
  export formats, design tables, and batch checks. TRIGGER: SolidWorks, CAD,
  macro, VBA, model automation, drawing automation, assembly automation,
  design table, STEP export, DXF export.
version: 1.0.0
category: CAD / Mechanical
tags: [solidworks, cad, mechanical, vba, automation, drawings, assemblies]
---

# CAD SolidWorks Automation

## Overview

Use this skill when working on mechanical CAD workflows, especially SolidWorks macro and API automation. The goal is to help engineers turn repetitive model, drawing, export, and inspection work into reliable scripts.

**Trigger words:** "SolidWorks", "CAD macro", "VBA macro", "automate drawing", "assembly automation", "batch export STEP", "design table", "configurations", "dimension equations".

---

## 1. Good CAD Automation Tasks

Strong automation candidates:

- Create or update repetitive features from parameters
- Rename features, sketches, configurations, or custom properties consistently
- Export many parts or drawings to STEP, PDF, DXF, STL, or neutral formats
- Check that drawings have required sheets, title blocks, balloons, dimensions, and revision fields
- Generate simple variants using dimensions, equations, and configurations
- Traverse assemblies to collect mass, material, part number, and missing-file information
- Create manufacturing handoff packages from a known folder structure

Poor automation candidates:

- Complex aesthetic surfacing decisions
- Ambiguous geometry repair that needs design judgment
- One-off modeling where macro setup takes longer than manual work
- Anything that silently modifies released design files without a backup

---

## 2. Macro Safety Rules

Before writing or running a CAD macro:

1. Work on a copy of the model or in a version-controlled workspace.
2. Save before batch operations.
3. Prefer read-only checks before write operations.
4. Log every changed file path.
5. Fail loudly when units, active document type, or selection state is not what the script expects.
6. Never assume the active document is the right one. Check document type first.
7. Avoid absolute machine paths. Use project-relative folders or ask the user for an output directory.

---

## 3. SolidWorks VBA Macro Skeleton

```vb
Option Explicit

Dim swApp As SldWorks.SldWorks
Dim swModel As SldWorks.ModelDoc2

Sub main()
    Set swApp = Application.SldWorks
    Set swModel = swApp.ActiveDoc

    If swModel Is Nothing Then
        MsgBox "Open a part, assembly, or drawing before running this macro."
        Exit Sub
    End If

    Debug.Print "Active document: " & swModel.GetTitle
    Debug.Print "Document path: " & swModel.GetPathName
End Sub
```

Document type guard:

```vb
Function RequirePart(model As SldWorks.ModelDoc2) As Boolean
    If model Is Nothing Then
        MsgBox "No active document."
        RequirePart = False
        Exit Function
    End If

    If model.GetType <> swDocPART Then
        MsgBox "This macro requires an active part document."
        RequirePart = False
        Exit Function
    End If

    RequirePart = True
End Function
```

---

## 4. Custom Properties Pattern

Use custom properties for engineering metadata such as part number, material, finish, revision, mass source, project, and designer.

```vb
Sub SetCustomProperty(propName As String, propValue As String)
    Dim ext As SldWorks.ModelDocExtension
    Dim props As CustomPropertyManager

    Set ext = swModel.Extension
    Set props = ext.CustomPropertyManager("")

    props.Add3 propName, swCustomInfoText, propValue, swCustomPropertyReplaceValue
End Sub
```

Example calls:

```vb
Call SetCustomProperty("Part Number", "BRACKET-001")
Call SetCustomProperty("Finish", "Black anodized")
Call SetCustomProperty("Manufacturing Process", "CNC milled")
```

Best practice: write properties once in the part or assembly, then have drawings reference them in title blocks and BOM tables.

---

## 5. Batch Export Pattern

Use batch export for release packages. Keep exports deterministic and separate source CAD from generated files.

```vb
Sub ExportActiveAsStep()
    Dim inputPath As String
    Dim outputPath As String
    Dim errors As Long
    Dim warnings As Long

    inputPath = swModel.GetPathName
    If inputPath = "" Then
        MsgBox "Save the file before exporting."
        Exit Sub
    End If

    outputPath = Left(inputPath, InStrRev(inputPath, ".") - 1) & ".step"

    swModel.Extension.SaveAs outputPath, _
        swSaveAsCurrentVersion, _
        swSaveAsOptions_Silent, _
        Nothing, errors, warnings

    If errors <> 0 Then
        MsgBox "Export failed. Error code: " & errors
    Else
        Debug.Print "Exported: " & outputPath
    End If
End Sub
```

Batch export checklist:

- Verify file is saved before export
- Skip unsaved or read-only files unless explicitly allowed
- Log errors and warnings
- Export to a generated output folder, not into source folders when possible
- Include date or release tag only if the team expects it

---

## 6. Configurations and Equations

Configurations are best for discrete product variants. Equations are best for parametric relationships.

Useful workflow:

1. Define named dimensions in sketches or features.
2. Use equations for relationships such as clearance, wall thickness, or symmetric offsets.
3. Use configurations for variant tables: length, width, mounting pattern, material, or customer option.
4. Rebuild after parameter changes.
5. Export a validation table listing configuration name, key dimensions, mass, and export status.

Common failure modes:

- Dimension names change after deleting and recreating sketches
- Suppressed features make a dimension unavailable in some configurations
- Design tables get out of sync with manually edited configurations
- Units are mixed between model settings and macro assumptions

---

## 7. Assembly Traversal Pattern

When traversing assemblies, collect metadata first, then write reports. Do not modify components during the first traversal.

```vb
Sub ReportAssemblyComponents()
    Dim swAssy As SldWorks.AssemblyDoc
    Dim components As Variant
    Dim comp As SldWorks.Component2
    Dim i As Long

    If swModel.GetType <> swDocASSEMBLY Then
        MsgBox "Open an assembly first."
        Exit Sub
    End If

    Set swAssy = swModel
    components = swAssy.GetComponents(False)

    For i = 0 To UBound(components)
        Set comp = components(i)
        Debug.Print comp.Name2 & " | " & comp.GetPathName
    Next i
End Sub
```

Useful checks:

- Missing component file path
- Suppressed or lightweight component state
- Duplicate part numbers
- Missing material
- Missing drawing file for manufactured components
- Vendor components accidentally included in manufacturing export

---

## 8. Drawing Automation

Good drawing checks:

- Required sheet sizes
- Title block fields populated
- Revision field present
- Drawing references the expected model
- All views are up to date
- BOM exists for assemblies
- Balloon count roughly matches BOM item count
- Required output PDF/DXF can be generated

Avoid fully automatic dimensioning unless the drawing standard is narrow and well tested. Drawing dimension placement is often judgment-heavy.

---

## 9. Useful Prompts for Copilot

Ask for specific CAD deliverables:

```text
Write a SolidWorks VBA macro that checks the active drawing for missing title block custom properties and prints a report. Do not modify the file.
```

```text
Create a SolidWorks macro that exports every saved part in the active assembly to STEP into an exports/step folder and logs failures.
```

```text
Design a safe workflow for generating 10 bracket configurations from width, height, thickness, and hole spacing parameters.
```

---

## Best Practices

- Treat CAD automation as engineering change automation, not just scripting.
- Separate read-only audit macros from write macros.
- Always log file paths, document type, and operation result.
- Use model custom properties as the single source of metadata.
- Prefer configurations for discrete variants and equations for relationships.
- Keep generated outputs in a known release folder.
- Do not silently overwrite released exports.
- Validate units and rebuild status before reading mass or dimensions.
- When in doubt, produce a report first and let the engineer approve the changes.
