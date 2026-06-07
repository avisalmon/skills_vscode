---
name: Word Powershell
description: >
  Word document automation via PowerShell COM.
---

# Word Powershell

## Word Document Automation — PowerShell COM Guide

**Source**: Drory Shohat (email, 2026-02-16)
**Scope**: global | **Category**: tool-guide

This guide covers reading and writing `.docx` files using **Word COM automation** in PowerShell. It follows the same COM pattern used for Outlook in this workspace.

---

## Table of Contents

- [Getting Started](#getting-started)
- [Reading Documents](#reading-documents)
  - [Open a Document](#open-a-document)
  - [Read Full Text](#read-full-text)
  - [Read Paragraph by Paragraph](#read-paragraph-by-paragraph)
  - [Extract Style & Formatting Info](#extract-style--formatting-info)
  - [Extract Hyperlinks](#extract-hyperlinks)
  - [Extract Tables](#extract-tables)
  - [Detect Table of Contents](#detect-table-of-contents)
  - [Extract Headers & Footers](#extract-headers--footers)
  - [Extract Images (Inline Shapes)](#extract-images-inline-shapes)
- [Writing Documents](#writing-documents)
  - [Create a New Document](#create-a-new-document)
  - [Add Text with Styles](#add-text-with-styles)
  - [Apply Font Formatting](#apply-font-formatting)
  - [Add Bullet & Numbered Lists](#add-bullet--numbered-lists)
  - [Add a Hyperlink](#add-a-hyperlink)
  - [Add a Table](#add-a-table)
  - [Insert a Table of Contents](#insert-a-table-of-contents)
  - [Add Headers & Footers](#add-headers--footers)
  - [Insert an Image](#insert-an-image)
  - [Insert a Page Break](#insert-a-page-break)
  - [Save the Document](#save-the-document)
- [Cloning Conventions from an Existing Document](#cloning-conventions-from-an-existing-document)
  - [Phase 1 — Analyze Source Document](#phase-1--analyze-source-document)
  - [Phase 2 — Recreate with Same Conventions](#phase-2--recreate-with-same-conventions)
- [Common Constants Reference](#common-constants-reference)
- [Cleanup & Best Practices](#cleanup--best-practices)

---

## Getting Started

All operations begin by creating a Word COM application instance:

```powershell
$word = New-Object -ComObject Word.Application
$word.Visible = $false   # Set to $true if you want to see Word open
```

> **Important:** Always close documents and quit Word when done to avoid orphaned `WINWORD.EXE` processes (see [Cleanup & Best Practices](#cleanup--best-practices)).

---

## Reading Documents

### Open a Document

```powershell
$docPath = "C:\path\to\document.docx"
$doc = $word.Documents.Open($docPath)
```

Open as **read-only**:

```powershell
$doc = $word.Documents.Open($docPath, $false, $true)  # 3rd param = ReadOnly
```

### Read Full Text

```powershell
$fullText = $doc.Content.Text
Write-Output $fullText
```

### Read Paragraph by Paragraph

```powershell
foreach ($para in $doc.Paragraphs) {
    $text  = $para.Range.Text.TrimEnd("`r")
    $style = $para.Style.NameLocal

    if ($text.Trim() -ne "") {
        Write-Output "[$style] $text"
    }
}
```

### Extract Style & Formatting Info

Get a full structural blueprint of every paragraph:

```powershell
$blueprint = foreach ($para in $doc.Paragraphs) {
    [PSCustomObject]@{
        Style       = $para.Style.NameLocal          # e.g. "Heading 1", "Normal"
        FontName    = $para.Range.Font.Name           # e.g. "Calibri"
        FontSize    = $para.Range.Font.Size           # e.g. 11
        Bold        = [bool]$para.Range.Font.Bold
        Italic      = [bool]$para.Range.Font.Italic
        Underline   = $para.Range.Font.Underline      # 0 = none, 1 = single
        Color       = $para.Range.Font.Color
        Alignment   = $para.Alignment                 # 0=Left, 1=Center, 2=Right, 3=Justify
        SpaceBefore = $para.SpaceBefore
        SpaceAfter  = $para.SpaceAfter
        LineSpacing = $para.LineSpacing
        ListType    = $para.Range.ListFormat.ListType  # 0=None, 1=Bullet, 2=Number
        IndentLevel = $para.Range.ListFormat.ListLevelNumber
        Text        = $para.Range.Text.Substring(0, [Math]::Min(100, $para.Range.Text.Length))
    }
}

$blueprint | Format-Table -AutoSize
```

### Extract Hyperlinks

```powershell
foreach ($link in $doc.Hyperlinks) {
    [PSCustomObject]@{
        DisplayText = $link.TextToDisplay
        URL         = $link.Address
        SubAddress  = $link.SubAddress    # For internal bookmarks / anchors
    }
}
```

### Extract Tables

```powershell
for ($t = 1; $t -le $doc.Tables.Count; $t++) {
    $table = $doc.Tables.Item($t)
    Write-Output "=== Table $t (Rows: $($table.Rows.Count), Cols: $($table.Columns.Count)) ==="

    for ($r = 1; $r -le $table.Rows.Count; $r++) {
        $rowData = @()
        for ($c = 1; $c -le $table.Columns.Count; $c++) {
            $cellText = $table.Cell($r, $c).Range.Text
            # Word cell text ends with special chars — trim them
            $cellText = $cellText -replace '[\r\n\a\x07]', ''
            $rowData += $cellText
        }
        Write-Output ($rowData -join " | ")
    }
}
```

### Detect Table of Contents

```powershell
$tocCount = $doc.TablesOfContents.Count
if ($tocCount -gt 0) {
    Write-Output "Document has $tocCount Table(s) of Contents"
    foreach ($toc in $doc.TablesOfContents) {
        Write-Output "  Heading levels: 1 to $($toc.LowerHeadingLevel)"
        Write-Output "  Uses hyperlinks: $($toc.UseHyperlinks)"
    }
} else {
    Write-Output "No Table of Contents found"
}
```

### Extract Headers & Footers

```powershell
foreach ($section in $doc.Sections) {
    # Primary header (odd pages / all pages)
    $header = $section.Headers.Item(1).Range.Text  # 1 = wdHeaderFooterPrimary
    $footer = $section.Footers.Item(1).Range.Text

    Write-Output "Header: $header"
    Write-Output "Footer: $footer"
}
```

Header/Footer index values:
| Index | Constant                     | Meaning            |
|-------|------------------------------|--------------------|
| 1     | `wdHeaderFooterPrimary`      | All / odd pages    |
| 2     | `wdHeaderFooterFirstPage`    | First page only    |
| 3     | `wdHeaderFooterEvenPages`    | Even pages         |

### Extract Images (Inline Shapes)

```powershell
Write-Output "Inline shapes: $($doc.InlineShapes.Count)"
foreach ($shape in $doc.InlineShapes) {
    [PSCustomObject]@{
        Type   = $shape.Type     # 3 = wdInlineShapePicture
        Width  = $shape.Width
        Height = $shape.Height
        Alt    = $shape.AlternativeText
    }
}
```

---

## Writing Documents

### Create a New Document

```powershell
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$doc = $word.Documents.Add()
```

Create from a **template**:

```powershell
$doc = $word.Documents.Add("C:\path\to\template.dotx")
```

### Add Text with Styles

```powershell
# Helper function: append a styled paragraph
function Add-WordParagraph {
    param(
        [object]$Doc,
        [string]$Text,
        [string]$Style = "Normal"
    )
    $para = $Doc.Content.Paragraphs.Add()
    $para.Range.Text = $Text
    $para.Style = $Style
    $para.Range.InsertParagraphAfter()
}

# Usage
Add-WordParagraph -Doc $doc -Text "Main Title"      -Style "Title"
Add-WordParagraph -Doc $doc -Text "Chapter One"      -Style "Heading 1"
Add-WordParagraph -Doc $doc -Text "Section A"        -Style "Heading 2"
Add-WordParagraph -Doc $doc -Text "Subsection i"     -Style "Heading 3"
Add-WordParagraph -Doc $doc -Text "This is body text." -Style "Normal"
```

### Apply Font Formatting

```powershell
$range = $doc.Content.Paragraphs.Last.Range
$range.Text = "Formatted text example"
$range.Font.Name      = "Calibri"
$range.Font.Size      = 12
$range.Font.Bold      = $true
$range.Font.Italic    = $true
$range.Font.Underline = 1          # 1 = wdUnderlineSingle
$range.Font.Color     = 0xFF0000   # Blue (BGR format) — or use wdColor constants
$range.ParagraphFormat.Alignment = 1  # Center
$range.InsertParagraphAfter()
```

**Common wdColor values (BGR, not RGB):**

| Color  | Value        |
|--------|--------------|
| Black  | `0x000000`   |
| Red    | `0x0000FF`   |
| Green  | `0x00FF00`   |
| Blue   | `0xFF0000`   |
| White  | `0xFFFFFF`   |

### Add Bullet & Numbered Lists

```powershell
# Bullet list
$items = @("First item", "Second item", "Third item")
foreach ($item in $items) {
    $para = $doc.Content.Paragraphs.Add()
    $para.Range.Text = $item
    $para.Style = "List Bullet"
    $para.Range.InsertParagraphAfter()
}

# Numbered list
foreach ($item in $items) {
    $para = $doc.Content.Paragraphs.Add()
    $para.Range.Text = $item
    $para.Style = "List Number"
    $para.Range.InsertParagraphAfter()
}
```

### Add a Hyperlink

```powershell
$para = $doc.Content.Paragraphs.Add()
$para.Range.Text = ""  # Placeholder — hyperlink replaces it
$doc.Hyperlinks.Add(
    $para.Range,                    # Anchor range
    "https://www.example.com",      # URL
    "",                              # SubAddress (for bookmarks)
    "Click to visit Example",       # ScreenTip
    "Visit Example.com"             # DisplayText
)
$para.Range.InsertParagraphAfter()
```

**Internal bookmark link (for TOC-like navigation):**

```powershell
# Create a bookmark at a heading
$headingRange = $doc.Content.Paragraphs.Item(3).Range
$doc.Bookmarks.Add("Section_A", $headingRange)

# Link to it from elsewhere
$linkRange = $doc.Content.Paragraphs.Last.Range
$doc.Hyperlinks.Add($linkRange, "", "Section_A", "", "Jump to Section A")
```

### Add a Table

```powershell
$rows = 4
$cols = 3
$range = $doc.Content.Paragraphs.Last.Range
$table = $doc.Tables.Add($range, $rows, $cols)

# Style the table
$table.Style = "Grid Table 4 - Accent 1"   # Built-in table style
$table.ApplyStyleHeadingRows = $true

# Populate headers
$table.Cell(1,1).Range.Text = "Name"
$table.Cell(1,2).Range.Text = "Role"
$table.Cell(1,3).Range.Text = "Email"

# Populate data
$table.Cell(2,1).Range.Text = "Alice"
$table.Cell(2,2).Range.Text = "Engineer"
$table.Cell(2,3).Range.Text = "alice@example.com"

# Bold the header row
$table.Rows.Item(1).Range.Font.Bold = $true
```

### Insert a Table of Contents

The TOC is auto-generated from Heading styles in the document:

```powershell
# Insert TOC at the beginning of the document
$tocRange = $doc.Range(0, 0)
$doc.TablesOfContents.Add(
    $tocRange,
    $true,          # UseHeadingStyles
    1,              # UpperHeadingLevel (Heading 1)
    3,              # LowerHeadingLevel (Heading 3)
    $false,         # UseFields
    $null,          # TableID
    $true,          # RightAlignPageNumbers
    $true,          # IncludePageNumbers
    "",             # AddedStyles
    $true           # UseHyperlinks (clickable in PDF/Word)
)

# Update the TOC after adding content
$doc.TablesOfContents.Item(1).Update()
```

### Add Headers & Footers

```powershell
$section = $doc.Sections.Item(1)

# Primary header
$header = $section.Headers.Item(1)  # wdHeaderFooterPrimary
$header.Range.Text = "CONFIDENTIAL — Example Corp"
$header.Range.Font.Size = 9
$header.Range.Font.Color = 0x808080  # Gray
$header.Range.ParagraphFormat.Alignment = 1  # Center

# Primary footer with page number
$footer = $section.Footers.Item(1)
$footer.Range.Text = ""
$footer.Range.Fields.Add($footer.Range, -1, "PAGE", $false)  # Page number field
$footer.Range.ParagraphFormat.Alignment = 1  # Center
```

### Insert an Image

```powershell
$range = $doc.Content.Paragraphs.Last.Range
$img = $doc.InlineShapes.AddPicture(
    "C:\path\to\image.png",
    $false,   # LinkToFile
    $true,    # SaveWithDocument
    $range
)

# Optionally resize
$img.Width  = 300
$img.Height = 200
$img.AlternativeText = "Description of the image"
```

### Insert a Page Break

```powershell
$range = $doc.Content.Paragraphs.Last.Range
$range.InsertBreak(7)  # 7 = wdPageBreak
```

### Save the Document

```powershell
# Save as .docx (default format)
$savePath = "C:\path\to\output.docx"
$doc.SaveAs([ref]$savePath, [ref]16)  # 16 = wdFormatDocumentDefault (.docx)

# Other format constants:
#   0  = wdFormatDocument      (.doc, legacy)
#   16 = wdFormatDocumentDefault (.docx)
#   17 = wdFormatPDF           (.pdf)
#   6  = wdFormatRTF           (.rtf)
#   2  = wdFormatText          (.txt)
```

**Save as PDF:**

```powershell
$pdfPath = "C:\path\to\output.pdf"
$doc.SaveAs([ref]$pdfPath, [ref]17)  # 17 = wdFormatPDF
```

---

## Cloning Conventions from an Existing Document

This two-phase approach lets Copilot analyze an existing document's formatting conventions and replicate them in a new document.

### Phase 1 — Analyze Source Document

Run this to extract the full blueprint:

```powershell
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$doc = $word.Documents.Open("C:\path\to\source.docx")

# --- Document-level settings ---
$pageSetup = $doc.PageSetup
$docInfo = [PSCustomObject]@{
    PaperSize     = $pageSetup.PaperSize
    Orientation   = $pageSetup.Orientation    # 0=Portrait, 1=Landscape
    TopMargin     = $pageSetup.TopMargin
    BottomMargin  = $pageSetup.BottomMargin
    LeftMargin    = $pageSetup.LeftMargin
    RightMargin   = $pageSetup.RightMargin
    HasTOC        = $doc.TablesOfContents.Count -gt 0
    TableCount    = $doc.Tables.Count
    HyperlinkCount= $doc.Hyperlinks.Count
    ImageCount    = $doc.InlineShapes.Count
    SectionCount  = $doc.Sections.Count
}
$docInfo | Format-List

# --- Paragraph styles used ---
$stylesUsed = $doc.Paragraphs | ForEach-Object {
    [PSCustomObject]@{
        Style     = $_.Style.NameLocal
        FontName  = $_.Range.Font.Name
        FontSize  = $_.Range.Font.Size
        Bold      = [bool]$_.Range.Font.Bold
        Alignment = $_.Alignment
    }
} | Sort-Object Style -Unique
$stylesUsed | Format-Table

# --- Hyperlinks ---
$doc.Hyperlinks | ForEach-Object {
    [PSCustomObject]@{
        Display = $_.TextToDisplay
        URL     = $_.Address
        Sub     = $_.SubAddress
    }
} | Format-Table

# --- TOC settings ---
if ($doc.TablesOfContents.Count -gt 0) {
    $toc = $doc.TablesOfContents.Item(1)
    [PSCustomObject]@{
        UpperLevel = $toc.UpperHeadingLevel
        LowerLevel = $toc.LowerHeadingLevel
        Hyperlinks = $toc.UseHyperlinks
        PageNumbers= $toc.IncludePageNumbers
    } | Format-List
}

# --- Headers / Footers ---
foreach ($sec in $doc.Sections) {
    Write-Output "Header: $($sec.Headers.Item(1).Range.Text)"
    Write-Output "Footer: $($sec.Footers.Item(1).Range.Text)"
}

$doc.Close($false)
$word.Quit()
```

### Phase 2 — Recreate with Same Conventions

Using the extracted info, build the new document with matching settings:

```powershell
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$doc = $word.Documents.Add()

# Apply page setup from source
$doc.PageSetup.TopMargin    = $sourceTopMargin
$doc.PageSetup.BottomMargin = $sourceBottomMargin
$doc.PageSetup.LeftMargin   = $sourceLeftMargin
$doc.PageSetup.RightMargin  = $sourceRightMargin
$doc.PageSetup.Orientation  = $sourceOrientation

# Add content using same heading styles, fonts, alignment, TOC, links, etc.
# ... (use the Add-WordParagraph helper and other techniques above)

# Insert TOC with same settings as source
$tocRange = $doc.Range(0, 0)
$doc.TablesOfContents.Add($tocRange, $true, 1, 3, $false, $null, $true, $true, "", $true)

# Update TOC
$doc.TablesOfContents.Item(1).Update()

# Save
$savePath = "C:\path\to\new_document.docx"
$doc.SaveAs([ref]$savePath, [ref]16)
$doc.Close()
$word.Quit()
```

---

## Common Constants Reference

### wdSaveFormat

| Constant                  | Value | Extension |
|---------------------------|-------|-----------|
| `wdFormatDocument`        | 0     | `.doc`    |
| `wdFormatText`            | 2     | `.txt`    |
| `wdFormatRTF`             | 6     | `.rtf`    |
| `wdFormatDocumentDefault` | 16    | `.docx`   |
| `wdFormatPDF`             | 17    | `.pdf`    |

### wdBuiltInStyle (commonly used)

| Style Name      | Constant Value |
|-----------------|----------------|
| `Normal`        | -1             |
| `Heading 1`     | -2             |
| `Heading 2`     | -3             |
| `Heading 3`     | -4             |
| `Title`         | -63            |
| `Subtitle`      | -75            |
| `List Bullet`   | -49            |
| `List Number`   | -50            |
| `TOC 1`         | -20            |
| `TOC 2`         | -21            |
| `TOC 3`         | -22            |

### wdParagraphAlignment

| Alignment | Value |
|-----------|-------|
| Left      | 0     |
| Center    | 1     |
| Right     | 2     |
| Justify   | 3     |

### wdBreakType

| Break        | Value |
|--------------|-------|
| Page         | 7     |
| Column       | 8     |
| Section Next | 2     |
| Line         | 6     |

### wdUnderline

| Style     | Value |
|-----------|-------|
| None      | 0     |
| Single    | 1     |
| Double    | 3     |
| Dotted    | 4     |
| Wavy      | 11    |

---

## Cleanup & Best Practices

**Always close and quit** to avoid orphaned Word processes:

```powershell
$doc.Close($false)   # $false = don't save changes (or $true to save)
$word.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null
[System.GC]::Collect()
[System.GC]::WaitForPendingFinalizers()
```

**Kill orphaned processes** (if needed):

```powershell
Get-Process WINWORD -ErrorAction SilentlyContinue | Stop-Process -Force
```

**Tips:**
- Set `$word.Visible = $true` during development to see what's happening.
- Use `$word.DisplayAlerts = 0` to suppress save/overwrite prompts.
- Wrap operations in `try/finally` to ensure cleanup runs even on errors:

```powershell
$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $doc = $word.Documents.Open("C:\path\file.docx")
    # ... work ...
} finally {
    if ($doc) { $doc.Close($false) }
    $word.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null
}
```
