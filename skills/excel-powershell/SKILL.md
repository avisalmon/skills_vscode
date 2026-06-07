---
name: Excel Powershell
description: >
  Excel automation via PowerShell COM.
---

# Excel Powershell

## Excel Automation — PowerShell COM Guide

**Source**: Drory Shohat (email, 2026-02-16)
**Scope**: global | **Category**: tool-guide

This guide covers reading and writing `.xlsx` files using **Excel COM automation** in PowerShell. Same COM pattern used for Outlook and Word in this workspace.

---

## Table of Contents

- [Getting Started](#getting-started)
- [Reading Workbooks](#reading-workbooks)
  - [Open a Workbook](#open-a-workbook)
  - [List Worksheets](#list-worksheets)
  - [Read Cell Values](#read-cell-values)
  - [Read a Range of Cells](#read-a-range-of-cells)
  - [Read an Entire Used Range](#read-an-entire-used-range)
  - [Read Named Ranges](#read-named-ranges)
  - [Detect Formatting & Styles](#detect-formatting--styles)
  - [Read Charts](#read-charts)
  - [Read Formulas](#read-formulas)
  - [Read Filters & AutoFilter](#read-filters--autofilter)
  - [Read Pivot Tables](#read-pivot-tables)
- [Writing Workbooks](#writing-workbooks)
  - [Create a New Workbook](#create-a-new-workbook)
  - [Add & Rename Worksheets](#add--rename-worksheets)
  - [Write Cell Values](#write-cell-values)
  - [Write a Range from an Array](#write-a-range-from-an-array)
  - [Apply Cell Formatting](#apply-cell-formatting)
  - [Apply Number Formats](#apply-number-formats)
  - [Set Column Width & Row Height](#set-column-width--row-height)
  - [Add Borders](#add-borders)
  - [Merge Cells](#merge-cells)
  - [Add Formulas](#add-formulas)
  - [Add Hyperlinks](#add-hyperlinks)
  - [Add Data Validation (Dropdowns)](#add-data-validation-dropdowns)
  - [Add Conditional Formatting](#add-conditional-formatting)
  - [Add AutoFilter](#add-autofilter)
  - [Create Charts](#create-charts)
  - [Add a Pivot Table](#add-a-pivot-table)
  - [Freeze Panes](#freeze-panes)
  - [Protect a Sheet](#protect-a-sheet)
  - [Save the Workbook](#save-the-workbook)
- [Practical Recipes](#practical-recipes)
  - [CSV to Formatted Excel](#csv-to-formatted-excel)
  - [Multi-Sheet Report](#multi-sheet-report)
  - [Clone Conventions from Existing Workbook](#clone-conventions-from-existing-workbook)
- [Common Constants Reference](#common-constants-reference)
- [Cleanup & Best Practices](#cleanup--best-practices)

---

## Getting Started

```powershell
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false          # Set $true during development
$excel.DisplayAlerts = $false    # Suppress save/overwrite prompts
```

> **Important:** Always close workbooks and quit Excel when done to avoid orphaned `EXCEL.EXE` processes (see [Cleanup & Best Practices](#cleanup--best-practices)).

---

## Reading Workbooks

### Open a Workbook

```powershell
$wb = $excel.Workbooks.Open("C:\path\to\file.xlsx")
```

Open as **read-only**:

```powershell
$wb = $excel.Workbooks.Open("C:\path\to\file.xlsx", 0, $true)  # 3rd param = ReadOnly
```

### List Worksheets

```powershell
foreach ($ws in $wb.Worksheets) {
    Write-Output "Sheet: $($ws.Name) | Index: $($ws.Index)"
}
```

### Read Cell Values

```powershell
$ws = $wb.Worksheets.Item(1)   # By index (1-based)
# or by name:
$ws = $wb.Worksheets.Item("Sheet1")

# Single cell
$value = $ws.Cells.Item(1, 1).Value2      # Row 1, Col 1 (A1)
$value = $ws.Range("B3").Value2            # Cell B3

# .Value2 is faster than .Value (skips date/currency conversions)
```

### Read a Range of Cells

```powershell
# Read a rectangular range
$range = $ws.Range("A1:D10")
$data = $range.Value2   # Returns a 2D array [row, col]

# Iterate the 2D array
for ($r = 1; $r -le $data.GetLength(0); $r++) {
    $row = @()
    for ($c = 1; $c -le $data.GetLength(1); $c++) {
        $row += $data[$r, $c]
    }
    Write-Output ($row -join " | ")
}
```

### Read an Entire Used Range

```powershell
$used = $ws.UsedRange
$rowCount = $used.Rows.Count
$colCount = $used.Columns.Count
Write-Output "Used range: $rowCount rows x $colCount columns"

# Get all values as a 2D array
$allData = $used.Value2

# First row (headers)
$headers = @()
for ($c = 1; $c -le $colCount; $c++) {
    $headers += $allData[1, $c]
}
Write-Output "Headers: $($headers -join ', ')"
```

### Read Named Ranges

```powershell
foreach ($name in $wb.Names) {
    Write-Output "$($name.Name) = $($name.RefersTo)"
}

# Read value from a named range
$namedValue = $ws.Range("MyNamedRange").Value2
```

### Detect Formatting & Styles

```powershell
$cell = $ws.Range("A1")
[PSCustomObject]@{
    FontName      = $cell.Font.Name
    FontSize      = $cell.Font.Size
    Bold          = [bool]$cell.Font.Bold
    Italic        = [bool]$cell.Font.Italic
    FontColor     = $cell.Font.Color        # Long value (BGR)
    BgColor       = $cell.Interior.Color    # Background color
    BgColorIndex  = $cell.Interior.ColorIndex
    NumberFormat  = $cell.NumberFormat       # e.g. "0.00", "dd/mm/yyyy"
    HAlign        = $cell.HorizontalAlignment
    VAlign        = $cell.VerticalAlignment
    WrapText      = [bool]$cell.WrapText
    Merged        = [bool]$cell.MergeCells
}
```

### Read Charts

```powershell
foreach ($chart in $ws.ChartObjects) {
    [PSCustomObject]@{
        Name      = $chart.Name
        ChartType = $chart.Chart.ChartType
        Width     = $chart.Width
        Height    = $chart.Height
        Top       = $chart.Top
        Left      = $chart.Left
    }
}
```

### Read Formulas

```powershell
# Get the formula in a cell (instead of the computed value)
$formula = $ws.Range("C2").Formula        # e.g. "=SUM(A2:B2)"
$formulaR1C1 = $ws.Range("C2").FormulaR1C1  # e.g. "=SUM(RC[-2]:RC[-1])"
```

### Read Filters & AutoFilter

```powershell
if ($ws.AutoFilterMode) {
    $af = $ws.AutoFilter
    Write-Output "Filter range: $($af.Range.Address)"
    foreach ($f in $af.Filters) {
        if ($f.On) {
            Write-Output "Filter on column $($f.Count): Criteria1=$($f.Criteria1)"
        }
    }
}
```

### Read Pivot Tables

```powershell
foreach ($pt in $ws.PivotTables) {
    Write-Output "Pivot: $($pt.Name)"
    Write-Output "  Source: $($pt.SourceData)"
    Write-Output "  Rows: $($pt.RowFields | ForEach-Object { $_.Name })"
    Write-Output "  Columns: $($pt.ColumnFields | ForEach-Object { $_.Name })"
    Write-Output "  Values: $($pt.DataFields | ForEach-Object { $_.Name })"
}
```

---

## Writing Workbooks

### Create a New Workbook

```powershell
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false
$wb = $excel.Workbooks.Add()
$ws = $wb.Worksheets.Item(1)
```

### Add & Rename Worksheets

```powershell
# Rename the first sheet
$ws.Name = "Summary"

# Add new sheets
$ws2 = $wb.Worksheets.Add()
$ws2.Name = "Data"

# Add sheet at the end
$wsLast = $wb.Worksheets.Add([System.Reflection.Missing]::Value, $wb.Worksheets.Item($wb.Worksheets.Count))
$wsLast.Name = "Appendix"

# Delete a sheet
$wb.Worksheets.Item("Sheet2").Delete()
```

### Write Cell Values

```powershell
$ws.Cells.Item(1, 1).Value2 = "Name"       # A1
$ws.Cells.Item(1, 2).Value2 = "Score"       # B1
$ws.Range("A2").Value2 = "Alice"
$ws.Range("B2").Value2 = 95
```

### Write a Range from an Array

```powershell
# Write a header row
$headers = @("Name", "Department", "Score", "Date")
$ws.Range("A1:D1").Value2 = $headers

# Write multiple rows at once (MUCH faster than cell-by-cell)
$data = @(
    @("Alice",   "Engineering", 95, "2026-01-15"),
    @("Bob",     "Design",      88, "2026-01-16"),
    @("Charlie", "Engineering", 92, "2026-01-17")
)

# Convert to 2D array for COM
$rows = $data.Count
$cols = $data[0].Count
$array2D = New-Object 'object[,]' $rows, $cols
for ($r = 0; $r -lt $rows; $r++) {
    for ($c = 0; $c -lt $cols; $c++) {
        $array2D[$r, $c] = $data[$r][$c]
    }
}
$ws.Range("A2:D$($rows + 1)").Value2 = $array2D
```

### Apply Cell Formatting

```powershell
# Bold header row
$ws.Range("A1:D1").Font.Bold = $true
$ws.Range("A1:D1").Font.Size = 12
$ws.Range("A1:D1").Font.Name = "Calibri"
$ws.Range("A1:D1").Font.Color = 0xFFFFFF          # White text

# Background color (header)
$ws.Range("A1:D1").Interior.Color = 0x8B4513       # Dark blue (BGR)

# Alignment
$ws.Range("A1:D1").HorizontalAlignment = -4108     # xlCenter
$ws.Range("A1:D1").VerticalAlignment = -4108        # xlCenter

# Italic
$ws.Range("A2").Font.Italic = $true

# Underline
$ws.Range("A2").Font.Underline = 2                  # xlUnderlineStyleSingle
```

### Apply Number Formats

```powershell
# Currency
$ws.Range("C2:C100").NumberFormat = '$#,##0.00'

# Percentage
$ws.Range("D2:D100").NumberFormat = '0.0%'

# Date
$ws.Range("E2:E100").NumberFormat = 'dd/mm/yyyy'

# Integer with comma separator
$ws.Range("F2:F100").NumberFormat = '#,##0'

# Custom text format
$ws.Range("G2:G100").NumberFormat = '@'   # Force text
```

### Set Column Width & Row Height

```powershell
# Set specific column width
$ws.Columns.Item(1).ColumnWidth = 20     # Column A
$ws.Columns.Item(2).ColumnWidth = 15     # Column B

# Auto-fit all used columns
$ws.UsedRange.EntireColumn.AutoFit()

# Auto-fit specific columns
$ws.Range("A:D").EntireColumn.AutoFit()

# Set row height
$ws.Rows.Item(1).RowHeight = 30    # Header row height
```

### Add Borders

```powershell
# All borders on a range
$range = $ws.Range("A1:D10")

# Border edges: 7=Left, 8=Top, 9=Bottom, 10=Right, 11=InsideVertical, 12=InsideHorizontal
foreach ($edge in @(7, 8, 9, 10, 11, 12)) {
    $border = $range.Borders.Item($edge)
    $border.LineStyle = 1         # xlContinuous
    $border.Weight = 2            # xlThin
    $border.Color = 0x000000      # Black
}

# Thick bottom border on header row only
$ws.Range("A1:D1").Borders.Item(9).LineStyle = 1
$ws.Range("A1:D1").Borders.Item(9).Weight = 4    # xlThick
```

### Merge Cells

```powershell
# Merge a range
$ws.Range("A1:D1").Merge()

# Unmerge
$ws.Range("A1:D1").UnMerge()

# Merge + center
$ws.Range("A1:D1").Merge()
$ws.Range("A1").Value2 = "Report Title"
$ws.Range("A1").HorizontalAlignment = -4108  # xlCenter
$ws.Range("A1").Font.Size = 16
$ws.Range("A1").Font.Bold = $true
```

### Add Formulas

```powershell
# Simple formula
$ws.Range("C2").Formula = "=A2+B2"

# SUM
$ws.Range("C10").Formula = "=SUM(C2:C9)"

# VLOOKUP
$ws.Range("E2").Formula = '=VLOOKUP(A2,Sheet2!A:B,2,FALSE)'

# IF
$ws.Range("F2").Formula = '=IF(C2>90,"Pass","Fail")'

# COUNTIF
$ws.Range("G1").Formula = '=COUNTIF(C2:C100,">90")'

# Fill down a formula
$ws.Range("C2").Formula = "=A2*B2"
$ws.Range("C2").AutoFill($ws.Range("C2:C100"))
```

### Add Hyperlinks

```powershell
# External URL
$ws.Hyperlinks.Add(
    $ws.Range("A5"),                  # Anchor cell
    "https://www.example.com",        # URL
    "",                                # SubAddress
    "Click to open",                  # ScreenTip
    "Visit Example"                   # TextToDisplay
)

# Link to another sheet in the same workbook
$ws.Hyperlinks.Add(
    $ws.Range("A6"),
    "",                                # No external URL
    "'Data'!A1",                      # SubAddress: sheet + cell
    "Go to Data sheet",
    "Jump to Data"
)

# Email link
$ws.Hyperlinks.Add(
    $ws.Range("A7"),
    "mailto:someone@example.com",
    "",
    "Send email",
    "Contact Support"
)
```

### Add Data Validation (Dropdowns)

```powershell
$cell = $ws.Range("B2:B100")
$validation = $cell.Validation
$validation.Delete()   # Clear existing validation
$validation.Add(
    3,                 # xlValidateList
    1,                 # xlValidAlertStop
    1,                 # Operator (ignored for lists)
    "Engineering,Design,Marketing,Sales"  # Comma-separated list
)
$validation.ShowInput = $true
$validation.InputTitle = "Department"
$validation.InputMessage = "Select a department"
$validation.ShowError = $true
$validation.ErrorTitle = "Invalid"
$validation.ErrorMessage = "Please select from the list"
```

### Add Conditional Formatting

```powershell
# Highlight cells > 90 in green
$range = $ws.Range("C2:C100")
$cf = $range.FormatConditions.Add(1, 5, 90)  # 1=xlCellValue, 5=xlGreater
$cf.Interior.Color = 0x00FF00   # Green (BGR)
$cf.Font.Bold = $true

# Highlight cells < 60 in red
$cf2 = $range.FormatConditions.Add(1, 6, 60)  # 6=xlLess
$cf2.Interior.Color = 0x0000FF  # Red (BGR)
$cf2.Font.Color = 0xFFFFFF      # White text

# Color scale (3-color: Red → Yellow → Green)
$cf3 = $range.FormatConditions.AddColorScale(3)
$cf3.ColorScaleCriteria.Item(1).FormatColor.Color = 0x0000FF  # Red (low)
$cf3.ColorScaleCriteria.Item(2).FormatColor.Color = 0x00FFFF  # Yellow (mid)
$cf3.ColorScaleCriteria.Item(3).FormatColor.Color = 0x00FF00  # Green (high)

# Data bars
$db = $range.FormatConditions.AddDatabar()
$db.BarColor.Color = 0xFF8C00  # Orange
```

### Add AutoFilter

```powershell
# Enable AutoFilter on header row
$ws.Range("A1:D1").AutoFilter()

# Apply a filter on column 2 (Department = Engineering)
$ws.Range("A1:D1").AutoFilter(2, "Engineering")

# Multiple criteria (Engineering OR Design)
$ws.Range("A1:D1").AutoFilter(2, "Engineering", 7, "Design")  # 7 = xlOr

# Clear all filters
if ($ws.AutoFilterMode) { $ws.AutoFilter.ShowAllData() }
```

### Create Charts

```powershell
# Add a chart object to the sheet
$chartObj = $ws.ChartObjects.Add(300, 50, 500, 300)  # Left, Top, Width, Height
$chart = $chartObj.Chart

# Set chart type
$chart.ChartType = 51     # xlColumnClustered (see constants below)

# Set data source
$chart.SetSourceData($ws.Range("A1:C5"))

# Title
$chart.HasTitle = $true
$chart.ChartTitle.Text = "Scores by Person"

# Axis labels
$chart.Axes(1).HasTitle = $true      # 1 = xlCategory (X axis)
$chart.Axes(1).AxisTitle.Text = "Name"
$chart.Axes(2).HasTitle = $true      # 2 = xlValue (Y axis)
$chart.Axes(2).AxisTitle.Text = "Score"

# Legend
$chart.HasLegend = $true
$chart.Legend.Position = -4107   # xlBottom

# Style
$chart.ApplyLayout(1)
```

**Common Chart Types:**

| Chart Type          | Value |
|---------------------|-------|
| xlColumnClustered   | 51    |
| xlColumnStacked     | 52    |
| xlBarClustered      | 57    |
| xlLine              | 4     |
| xlLineMarkers       | 65    |
| xlPie               | 5     |
| xlXYScatter         | -4169 |
| xlArea              | 1     |
| xlDoughnut          | -4120 |
| xl3DColumnClustered | 54    |

### Add a Pivot Table

```powershell
# Define source data range
$sourceRange = $ws.Range("A1:D100")

# Create a pivot cache
$pivotCache = $wb.PivotCaches().Create(1, $sourceRange)  # 1 = xlDatabase

# Add pivot table to a new sheet
$pivotSheet = $wb.Worksheets.Add()
$pivotSheet.Name = "Pivot"
$pivotTable = $pivotCache.CreatePivotTable($pivotSheet.Range("A3"), "SalesPivot")

# Add fields
$pivotTable.PivotFields("Department").Orientation = 1   # xlRowField
$pivotTable.PivotFields("Name").Orientation = 2          # xlColumnField

$dataField = $pivotTable.AddDataField($pivotTable.PivotFields("Score"), "Avg Score", -4106)
# -4106 = xlAverage (use -4157 for xlSum)
```

### Freeze Panes

```powershell
# Freeze top row (header)
$ws.Activate()
$excel.ActiveWindow.SplitRow = 1
$excel.ActiveWindow.FreezePanes = $true

# Freeze first column
$excel.ActiveWindow.SplitColumn = 1
$excel.ActiveWindow.FreezePanes = $true

# Freeze at cell B2 (first row AND first column frozen)
$ws.Range("B2").Select()
$excel.ActiveWindow.FreezePanes = $true
```

### Protect a Sheet

```powershell
# Protect with password
$ws.Protect("myPassword123", $true, $true, $true)
# Args: Password, DrawingObjects, Contents, Scenarios

# Protect but allow filtering
$ws.Protect("myPassword123", $true, $true, $true, $false, $false, $false, $false, $false, $false, $false, $false, $false, $false, $true, $false)
# The 15th parameter allows AutoFilter

# Unprotect
$ws.Unprotect("myPassword123")

# Protect workbook structure (prevent adding/deleting sheets)
$wb.Protect("myPassword123", $true, $false)  # Structure=True, Windows=False
```

### Save the Workbook

```powershell
# Save as .xlsx (default format)
$savePath = "C:\path\to\output.xlsx"
$wb.SaveAs($savePath, 51)   # 51 = xlOpenXMLWorkbook (.xlsx)

# Other format constants:
#   51 = xlOpenXMLWorkbook        (.xlsx)
#   52 = xlOpenXMLWorkbookMacroEnabled (.xlsm)
#   50 = xlExcel12                (.xlsb, binary)
#   56 = xlCSV                    (.csv)
#   -4158 = xlWorkbookNormal      (.xls, legacy)
#   57 = xlCurrentPlatformText    (.txt)

# Save as CSV
$wb.SaveAs("C:\path\to\output.csv", 56)

# Save as PDF
$ws.ExportAsFixedFormat(0, "C:\path\to\output.pdf")  # 0 = xlTypePDF
```

---

## Practical Recipes

### CSV to Formatted Excel

```powershell
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false

# Import CSV
$csvPath = "C:\path\to\data.csv"
$wb = $excel.Workbooks.Open($csvPath)
$ws = $wb.Worksheets.Item(1)

# Format as table
$usedRange = $ws.UsedRange
$colCount = $usedRange.Columns.Count
$rowCount = $usedRange.Rows.Count

# Bold & color header row
$headerRange = $ws.Range($ws.Cells(1,1), $ws.Cells(1, $colCount))
$headerRange.Font.Bold = $true
$headerRange.Font.Color = 0xFFFFFF
$headerRange.Interior.Color = 0x8B4513

# Borders on all data
$allRange = $ws.Range($ws.Cells(1,1), $ws.Cells($rowCount, $colCount))
foreach ($edge in @(7,8,9,10,11,12)) {
    $allRange.Borders.Item($edge).LineStyle = 1
    $allRange.Borders.Item($edge).Weight = 2
}

# AutoFit
$usedRange.EntireColumn.AutoFit()

# AutoFilter
$headerRange.AutoFilter() | Out-Null

# Freeze header row
$ws.Range("A2").Select()
$excel.ActiveWindow.FreezePanes = $true

# Save as xlsx
$xlsxPath = $csvPath -replace '\.csv$', '.xlsx'
$wb.SaveAs($xlsxPath, 51)
$wb.Close()
$excel.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
```

### Multi-Sheet Report

```powershell
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false
$wb = $excel.Workbooks.Add()

# --- Summary Sheet ---
$summary = $wb.Worksheets.Item(1)
$summary.Name = "Summary"
$summary.Range("A1").Value2 = "Quarterly Report"
$summary.Range("A1").Font.Size = 18
$summary.Range("A1").Font.Bold = $true
$summary.Range("A3").Value2 = "Generated:"
$summary.Range("B3").Value2 = (Get-Date).ToString("yyyy-MM-dd HH:mm")

# Add links to other sheets
$summary.Hyperlinks.Add($summary.Range("A5"), "", "'Q1 Data'!A1", "", "Q1 Data")
$summary.Hyperlinks.Add($summary.Range("A6"), "", "'Q2 Data'!A1", "", "Q2 Data")

# --- Q1 Data Sheet ---
$q1 = $wb.Worksheets.Add([System.Reflection.Missing]::Value, $summary)
$q1.Name = "Q1 Data"
$q1.Range("A1:C1").Value2 = @("Metric", "Target", "Actual")
$q1.Range("A1:C1").Font.Bold = $true
$q1.Range("A2").Value2 = "Revenue"
$q1.Range("B2").Value2 = 1000000
$q1.Range("C2").Value2 = 1050000
$q1.Range("B2:C2").NumberFormat = '$#,##0'

# --- Q2 Data Sheet ---
$q2 = $wb.Worksheets.Add([System.Reflection.Missing]::Value, $q1)
$q2.Name = "Q2 Data"
$q2.Range("A1:C1").Value2 = @("Metric", "Target", "Actual")
$q2.Range("A1:C1").Font.Bold = $true

$wb.SaveAs("C:\path\to\QuarterlyReport.xlsx", 51)
$wb.Close()
$excel.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
```

### Clone Conventions from Existing Workbook

#### Phase 1 — Analyze Source Workbook

```powershell
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$wb = $excel.Workbooks.Open("C:\path\to\source.xlsx", 0, $true)

# --- Workbook-level info ---
[PSCustomObject]@{
    SheetCount   = $wb.Worksheets.Count
    SheetNames   = ($wb.Worksheets | ForEach-Object { $_.Name }) -join ", "
    HasMacros    = $wb.HasVBProject
    NamedRanges  = $wb.Names.Count
}

# --- Per-sheet analysis ---
foreach ($ws in $wb.Worksheets) {
    Write-Output "`n=== Sheet: $($ws.Name) ==="
    $used = $ws.UsedRange
    Write-Output "  Rows: $($used.Rows.Count), Cols: $($used.Columns.Count)"
    Write-Output "  AutoFilter: $($ws.AutoFilterMode)"
    Write-Output "  Charts: $($ws.ChartObjects.Count)"
    Write-Output "  PivotTables: $($ws.PivotTables().Count)"

    # Sample formatting from first row
    for ($c = 1; $c -le [Math]::Min($used.Columns.Count, 10); $c++) {
        $cell = $ws.Cells.Item(1, $c)
        Write-Output "  Col $c | Font: $($cell.Font.Name) $($cell.Font.Size)pt | Bold: $($cell.Font.Bold) | NumFmt: $($cell.NumberFormat) | BG: $($cell.Interior.Color)"
    }
}

# --- Column widths ---
foreach ($ws in $wb.Worksheets) {
    $widths = @()
    for ($c = 1; $c -le $ws.UsedRange.Columns.Count; $c++) {
        $widths += "$c=$($ws.Columns.Item($c).ColumnWidth)"
    }
    Write-Output "Widths ($($ws.Name)): $($widths -join ', ')"
}

$wb.Close($false)
$excel.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
```

#### Phase 2 — Recreate with Same Conventions

Use the extracted font names, sizes, colors, number formats, column widths, and structure to rebuild the workbook using the writing techniques above.

---

## Common Constants Reference

### xlFileFormat (Save Formats)

| Constant                          | Value  | Extension |
|-----------------------------------|--------|-----------|
| `xlOpenXMLWorkbook`               | 51     | `.xlsx`   |
| `xlOpenXMLWorkbookMacroEnabled`   | 52     | `.xlsm`   |
| `xlExcel12`                       | 50     | `.xlsb`   |
| `xlCSV`                           | 56     | `.csv`    |
| `xlWorkbookNormal`                | -4158  | `.xls`    |

### xlHAlign (Horizontal Alignment)

| Alignment | Value  |
|-----------|--------|
| General   | 1      |
| Left      | -4131  |
| Center    | -4108  |
| Right     | -4152  |
| Justify   | -4130  |

### xlVAlign (Vertical Alignment)

| Alignment | Value  |
|-----------|--------|
| Top       | -4160  |
| Center    | -4108  |
| Bottom    | -4107  |

### xlBordersIndex

| Border          | Value |
|-----------------|-------|
| Left            | 7     |
| Top             | 8     |
| Bottom          | 9     |
| Right           | 10    |
| InsideVertical  | 11    |
| InsideHorizontal| 12    |

### xlBorderWeight

| Weight     | Value |
|------------|-------|
| Hairline   | 1     |
| Thin       | 2     |
| Medium     | -4138 |
| Thick      | 4     |

### xlLineStyle

| Style       | Value |
|-------------|-------|
| Continuous  | 1     |
| Dash        | -4115 |
| Dot         | -4118 |
| DashDot     | 4     |
| Double      | -4119 |
| None        | -4142 |

### xlChartType (Common)

| Chart                | Value  |
|----------------------|--------|
| Column Clustered     | 51     |
| Column Stacked       | 52     |
| Bar Clustered        | 57     |
| Line                 | 4      |
| Line with Markers    | 65     |
| Pie                  | 5      |
| XY Scatter           | -4169  |
| Area                 | 1      |

### xlConsolidationFunction

| Function | Value  |
|----------|--------|
| Sum      | -4157  |
| Count    | -4112  |
| Average  | -4106  |
| Max      | -4136  |
| Min      | -4139  |

### xlPivotFieldOrientation

| Orientation | Value |
|-------------|-------|
| Row         | 1     |
| Column      | 2     |
| Page        | 3     |
| Data        | 4     |

### Common Colors (BGR Format)

| Color        | Value      |
|--------------|------------|
| Black        | `0x000000` |
| White        | `0xFFFFFF` |
| Red          | `0x0000FF` |
| Green        | `0x00FF00` |
| Blue         | `0xFF0000` |
| Yellow       | `0x00FFFF` |
| Orange       | `0x00A5FF` |
| Light Gray   | `0xD3D3D3` |
| Dark Blue    | `0x8B0000` |

---

## Cleanup & Best Practices

**Always close and quit** to avoid orphaned Excel processes:

```powershell
$wb.Close($false)     # $false = don't save; $true = save
$excel.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
[System.GC]::Collect()
[System.GC]::WaitForPendingFinalizers()
```

**Kill orphaned processes** (if needed):

```powershell
Get-Process EXCEL -ErrorAction SilentlyContinue | Stop-Process -Force
```

**Use try/finally for safe cleanup:**

```powershell
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false
try {
    $wb = $excel.Workbooks.Open("C:\path\file.xlsx")
    # ... work ...
} finally {
    if ($wb) { $wb.Close($false) }
    $excel.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
}
```

**Performance tips:**

- Set `$excel.ScreenUpdating = $false` before bulk operations, then `$true` after — dramatically faster.
- Set `$excel.Calculation = -4135` (`xlCalculationManual`) during bulk writes, then `-4105` (`xlCalculationAutomatic`) after.
- Write data as 2D arrays to ranges instead of cell-by-cell — orders of magnitude faster.
- Use `.Value2` instead of `.Value` — avoids slow date/currency conversion overhead.

```powershell
# Performance wrapper
$excel.ScreenUpdating = $false
$excel.Calculation = -4135        # Manual calc
$excel.EnableEvents = $false

# ... bulk operations here ...

$excel.Calculation = -4105        # Auto calc
$excel.ScreenUpdating = $true
$excel.EnableEvents = $true
```
