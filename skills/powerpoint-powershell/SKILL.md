---
name: Powerpoint Powershell
description: >
  PowerPoint automation via PowerShell COM.
---

# Powerpoint Powershell

## PowerPoint Automation — PowerShell COM Guide

**Source**: Drory Shohat (email, 2026-02-16)
**Scope**: global | **Category**: tool-guide

This guide covers reading and writing `.pptx` files using **PowerPoint COM automation** in PowerShell. Same COM pattern used for Outlook, Word, and Excel in this workspace.

---

## Table of Contents

- [Getting Started](#getting-started)
- [Reading Presentations](#reading-presentations)
  - [Open a Presentation](#open-a-presentation)
  - [List Slides](#list-slides)
  - [Read Slide Text](#read-slide-text)
  - [Read All Text from Every Slide](#read-all-text-from-every-slide)
  - [Extract Slide Layout & Master Info](#extract-slide-layout--master-info)
  - [Read Shape Details](#read-shape-details)
  - [Read Tables](#read-tables)
  - [Read Charts](#read-charts)
  - [Read Images](#read-images)
  - [Extract Hyperlinks](#extract-hyperlinks)
  - [Read Slide Notes](#read-slide-notes)
  - [Read Transitions & Animations](#read-transitions--animations)
  - [Read Slide Dimensions](#read-slide-dimensions)
- [Writing Presentations](#writing-presentations)
  - [Create a New Presentation](#create-a-new-presentation)
  - [Add Slides with Layouts](#add-slides-with-layouts)
  - [Add Text to Placeholders](#add-text-to-placeholders)
  - [Add a Text Box](#add-a-text-box)
  - [Apply Font Formatting](#apply-font-formatting)
  - [Add Bullet & Numbered Lists](#add-bullet--numbered-lists)
  - [Add Hyperlinks](#add-hyperlinks)
  - [Add a Table](#add-a-table)
  - [Add an Image](#add-an-image)
  - [Add Shapes (Rectangles, Circles, Arrows)](#add-shapes-rectangles-circles-arrows)
  - [Add a Chart](#add-a-chart)
  - [Set Shape Fill & Line](#set-shape-fill--line)
  - [Add Slide Notes](#add-slide-notes)
  - [Add Transitions](#add-transitions)
  - [Set Slide Background](#set-slide-background)
  - [Duplicate & Reorder Slides](#duplicate--reorder-slides)
  - [Delete Slides](#delete-slides)
  - [Save the Presentation](#save-the-presentation)
- [Practical Recipes](#practical-recipes)
  - [Data-Driven Slide Deck](#data-driven-slide-deck)
  - [Template-Based Report](#template-based-report)
  - [Clone Conventions from Existing Presentation](#clone-conventions-from-existing-presentation)
- [Common Constants Reference](#common-constants-reference)
- [Cleanup & Best Practices](#cleanup--best-practices)

---

## Getting Started

```powershell
$ppt = New-Object -ComObject PowerPoint.Application
$ppt.Visible = [Microsoft.Office.Core.MsoTriState]::msoTrue  # PowerPoint must be visible (COM requirement)
# Use msoTrue (=-1) or just set to 1
```

> **Note:** Unlike Word/Excel, PowerPoint COM generally requires `Visible = $true` to work properly. You can minimize the window instead.

---

## Reading Presentations

### Open a Presentation

```powershell
$pres = $ppt.Presentations.Open("C:\path\to\file.pptx")
```

Open as **read-only**:

```powershell
$pres = $ppt.Presentations.Open("C:\path\to\file.pptx", $true)  # 2nd param = ReadOnly
```

Open without showing window:

```powershell
$pres = $ppt.Presentations.Open("C:\path\to\file.pptx", $false, $false, $false)
# Params: FileName, ReadOnly, Untitled, WithWindow
```

### List Slides

```powershell
Write-Output "Total slides: $($pres.Slides.Count)"
foreach ($slide in $pres.Slides) {
    $layoutName = $slide.Layout  # Layout enum value
    Write-Output "Slide $($slide.SlideIndex): Layout=$layoutName, Shapes=$($slide.Shapes.Count)"
}
```

### Read Slide Text

```powershell
$slide = $pres.Slides.Item(1)
foreach ($shape in $slide.Shapes) {
    if ($shape.HasTextFrame) {
        $text = $shape.TextFrame.TextRange.Text
        if ($text.Trim() -ne "") {
            Write-Output "[$($shape.Name)] $text"
        }
    }
}
```

### Read All Text from Every Slide

```powershell
for ($s = 1; $s -le $pres.Slides.Count; $s++) {
    $slide = $pres.Slides.Item($s)
    Write-Output "=== Slide $s ==="
    foreach ($shape in $slide.Shapes) {
        if ($shape.HasTextFrame) {
            $tf = $shape.TextFrame.TextRange
            if ($tf.Text.Trim() -ne "") {
                Write-Output "  [$($shape.Name)] $($tf.Text)"
            }
        }
    }
}
```

### Extract Slide Layout & Master Info

```powershell
foreach ($slide in $pres.Slides) {
    [PSCustomObject]@{
        SlideIndex = $slide.SlideIndex
        Layout     = $slide.Layout            # Enum value
        LayoutName = $slide.CustomLayout.Name  # e.g. "Title Slide", "Title and Content"
        MasterName = $slide.Design.Name
    }
}
```

### Read Shape Details

```powershell
foreach ($shape in $slide.Shapes) {
    [PSCustomObject]@{
        Name       = $shape.Name
        Type       = $shape.Type          # 1=AutoShape, 13=Picture, 14=Placeholder, etc.
        Left       = $shape.Left          # Points from left edge
        Top        = $shape.Top           # Points from top edge
        Width      = $shape.Width
        Height     = $shape.Height
        HasText    = $shape.HasTextFrame
        IsTable    = $shape.HasTable
        IsChart    = $shape.HasChart
        Rotation   = $shape.Rotation
    }
}
```

### Read Tables

```powershell
foreach ($shape in $slide.Shapes) {
    if ($shape.HasTable) {
        $table = $shape.Table
        Write-Output "Table: $($table.Rows.Count) rows x $($table.Columns.Count) cols"
        for ($r = 1; $r -le $table.Rows.Count; $r++) {
            $rowData = @()
            for ($c = 1; $c -le $table.Columns.Count; $c++) {
                $cellText = $table.Cell($r, $c).Shape.TextFrame.TextRange.Text
                $rowData += $cellText
            }
            Write-Output ($rowData -join " | ")
        }
    }
}
```

### Read Charts

```powershell
foreach ($shape in $slide.Shapes) {
    if ($shape.HasChart) {
        $chart = $shape.Chart
        [PSCustomObject]@{
            ChartType  = $chart.ChartType
            HasTitle   = $chart.HasTitle
            Title      = if ($chart.HasTitle) { $chart.ChartTitle.Text } else { "N/A" }
            HasLegend  = $chart.HasLegend
        }
    }
}
```

### Read Images

```powershell
foreach ($shape in $slide.Shapes) {
    if ($shape.Type -eq 13) {  # 13 = msoPicture
        [PSCustomObject]@{
            Name   = $shape.Name
            Width  = $shape.Width
            Height = $shape.Height
            Left   = $shape.Left
            Top    = $shape.Top
            Alt    = $shape.AlternativeText
        }
    }
}

# Export an image from a slide
$shape = $slide.Shapes.Item(3)  # Adjust index
$shape.Export("C:\path\to\exported_image.png", 2)  # 2 = ppShapeFormatPNG
```

### Extract Hyperlinks

```powershell
foreach ($slide in $pres.Slides) {
    foreach ($link in $slide.Hyperlinks) {
        [PSCustomObject]@{
            Slide      = $slide.SlideIndex
            Address    = $link.Address
            SubAddress = $link.SubAddress
            TextRange  = $link.TextToDisplay
            Type       = $link.Type  # 1=URL, 2=SlideLink
        }
    }
}
```

### Read Slide Notes

```powershell
foreach ($slide in $pres.Slides) {
    $notesPage = $slide.NotesPage
    $notesText = ""
    foreach ($shape in $notesPage.Shapes) {
        if ($shape.HasTextFrame) {
            $t = $shape.TextFrame.TextRange.Text
            if ($t.Trim() -ne "" -and $shape.PlaceholderFormat.Type -eq 2) {
                # Type 2 = ppPlaceholderBody (notes placeholder)
                $notesText = $t
            }
        }
    }
    if ($notesText) {
        Write-Output "Slide $($slide.SlideIndex) Notes: $notesText"
    }
}
```

### Read Transitions & Animations

```powershell
foreach ($slide in $pres.Slides) {
    $trans = $slide.SlideShowTransition
    if ($trans.EntryEffect -ne 0) {
        Write-Output "Slide $($slide.SlideIndex): Transition=$($trans.EntryEffect), Duration=$($trans.Duration)s"
    }
}

# Animation effects
foreach ($slide in $pres.Slides) {
    $timeline = $slide.TimeLine
    if ($timeline.MainSequence.Count -gt 0) {
        Write-Output "Slide $($slide.SlideIndex): $($timeline.MainSequence.Count) animations"
        foreach ($effect in $timeline.MainSequence) {
            Write-Output "  Shape: $($effect.Shape.Name) | Effect: $($effect.EffectType)"
        }
    }
}
```

### Read Slide Dimensions

```powershell
$width  = $pres.PageSetup.SlideWidth    # In points (1 inch = 72 points)
$height = $pres.PageSetup.SlideHeight
Write-Output "Slide size: $($width/72) x $($height/72) inches"
Write-Output "Slide size: $width x $height points"
```

---

## Writing Presentations

### Create a New Presentation

```powershell
$ppt = New-Object -ComObject PowerPoint.Application
$ppt.Visible = 1
$pres = $ppt.Presentations.Add()
```

Create from a **template**:

```powershell
$pres = $ppt.Presentations.Open("C:\path\to\template.potx")
```

### Add Slides with Layouts

```powershell
# Add a slide with a specific layout
# Layout reference: see Constants section below
$layout = $pres.SlideMaster.CustomLayouts.Item(1)  # First layout (usually Title Slide)
$slide = $pres.Slides.AddSlide($pres.Slides.Count + 1, $layout)

# Common approach: use ppLayout enum values
$slide1 = $pres.Slides.Add($pres.Slides.Count + 1, 1)   # ppLayoutTitle
$slide2 = $pres.Slides.Add($pres.Slides.Count + 1, 2)   # ppLayoutText (Title + Content)
$slide3 = $pres.Slides.Add($pres.Slides.Count + 1, 12)  # ppLayoutBlank
```

### Add Text to Placeholders

```powershell
# Placeholders are the predefined text areas on a slide layout
$slide = $pres.Slides.Item(1)

# Title placeholder (usually index 1)
$slide.Shapes.Placeholders.Item(1).TextFrame.TextRange.Text = "Presentation Title"

# Subtitle / Body placeholder (usually index 2)
$slide.Shapes.Placeholders.Item(2).TextFrame.TextRange.Text = "Subtitle or body text"
```

### Add a Text Box

```powershell
# AddTextbox(Orientation, Left, Top, Width, Height) — all in points
$textBox = $slide.Shapes.AddTextbox(
    1,      # msoTextOrientationHorizontal
    100,    # Left (points)
    200,    # Top (points)
    400,    # Width
    50      # Height
)
$textBox.TextFrame.TextRange.Text = "Custom text box content"
$textBox.TextFrame.WordWrap = -1   # msoTrue = enable word wrap
```

### Apply Font Formatting

```powershell
$textRange = $slide.Shapes.Placeholders.Item(1).TextFrame.TextRange

# Whole text range
$textRange.Font.Name = "Calibri"
$textRange.Font.Size = 28
$textRange.Font.Bold = -1          # msoTrue
$textRange.Font.Italic = -1
$textRange.Font.Color.RGB = 0x4472C4  # RGB (not BGR like Word/Excel!)
$textRange.Font.Underline = -1

# Format a portion of text
$textRange.Text = "Bold and Normal text"
$textRange.Characters(1, 4).Font.Bold = -1    # "Bold"
$textRange.Characters(10, 6).Font.Italic = -1  # "Normal"

# Paragraph alignment
$textRange.ParagraphFormat.Alignment = 2  # ppAlignCenter
```

> **Important:** PowerPoint uses **RGB** for colors (not BGR like Word/Excel COM).

### Add Bullet & Numbered Lists

```powershell
$textRange = $slide.Shapes.Placeholders.Item(2).TextFrame.TextRange
$textRange.Text = "First item`rSecond item`rThird item"  # Use `r for new paragraphs

# Bullet list (default for content placeholders)
$textRange.ParagraphFormat.Bullet.Type = 1  # ppBulletUnnumbered

# Numbered list
$textRange.ParagraphFormat.Bullet.Type = 2  # ppBulletNumbered
$textRange.ParagraphFormat.Bullet.Style = 1 # ppBulletArabicPeriod (1. 2. 3.)

# Custom bullet character
$textRange.ParagraphFormat.Bullet.Type = 1
$textRange.ParagraphFormat.Bullet.Character = 8226  # Unicode bullet •

# Indent levels (sub-bullets)
$textRange.Paragraphs(2).IndentLevel = 2  # Sub-bullet
$textRange.Paragraphs(3).IndentLevel = 3  # Sub-sub-bullet

# Remove bullets
$textRange.ParagraphFormat.Bullet.Type = 0  # ppBulletNone
```

### Add Hyperlinks

```powershell
# Hyperlink on text
$textRange = $slide.Shapes.Placeholders.Item(2).TextFrame.TextRange
$textRange.Text = "Visit our website"
$slide.Hyperlinks.Add($textRange, "https://www.example.com", "", "", "")

# Hyperlink on a shape
$shape = $slide.Shapes.Item(3)
$slide.Hyperlinks.Add($shape.TextFrame.TextRange, "https://www.example.com")

# Link to another slide in the same presentation
$textRange2 = $slide.Shapes.AddTextbox(1, 100, 400, 300, 30).TextFrame.TextRange
$textRange2.Text = "Jump to Slide 3"
$pres.Slides.Item(1).Hyperlinks.Add($textRange2, "", "3,1,Slide 3")
# SubAddress format: "slideIndex,clickAction,slideTitle"
```

### Add a Table

```powershell
# AddTable(NumRows, NumColumns, Left, Top, Width, Height)
$tableShape = $slide.Shapes.AddTable(4, 3, 50, 150, 600, 200)
$table = $tableShape.Table

# Populate headers
$table.Cell(1, 1).Shape.TextFrame.TextRange.Text = "Name"
$table.Cell(1, 2).Shape.TextFrame.TextRange.Text = "Role"
$table.Cell(1, 3).Shape.TextFrame.TextRange.Text = "Score"

# Populate data
$table.Cell(2, 1).Shape.TextFrame.TextRange.Text = "Alice"
$table.Cell(2, 2).Shape.TextFrame.TextRange.Text = "Engineer"
$table.Cell(2, 3).Shape.TextFrame.TextRange.Text = "95"

# Format header row
for ($c = 1; $c -le 3; $c++) {
    $cell = $table.Cell(1, $c)
    $cell.Shape.TextFrame.TextRange.Font.Bold = -1
    $cell.Shape.TextFrame.TextRange.Font.Color.RGB = 0xFFFFFF  # White
    $cell.Shape.Fill.ForeColor.RGB = 0x4472C4                   # Blue background
}

# Set column widths
$table.Columns.Item(1).Width = 200
$table.Columns.Item(2).Width = 200
$table.Columns.Item(3).Width = 200

# Set row height
$table.Rows.Item(1).Height = 40
```

### Add an Image

```powershell
# AddPicture(FileName, LinkToFile, SaveWithDocument, Left, Top, Width, Height)
$pic = $slide.Shapes.AddPicture(
    "C:\path\to\image.png",
    0,       # msoFalse — don't link to file
    -1,      # msoTrue — save with document
    100,     # Left
    100,     # Top
    400,     # Width (-1 to keep original)
    300      # Height (-1 to keep original)
)

# Keep aspect ratio
$pic.LockAspectRatio = -1  # msoTrue
$pic.Width = 400            # Height adjusts automatically

# Add alt text
$pic.AlternativeText = "Description of the image"
```

### Add Shapes (Rectangles, Circles, Arrows)

```powershell
# AddShape(AutoShapeType, Left, Top, Width, Height)

# Rectangle
$rect = $slide.Shapes.AddShape(1, 100, 100, 200, 100)   # msoShapeRectangle
$rect.TextFrame.TextRange.Text = "Rectangle"

# Rounded Rectangle
$rrect = $slide.Shapes.AddShape(5, 350, 100, 200, 100)  # msoShapeRoundedRectangle

# Oval / Circle
$oval = $slide.Shapes.AddShape(9, 100, 250, 100, 100)   # msoShapeOval

# Right Arrow
$arrow = $slide.Shapes.AddShape(33, 250, 270, 150, 60)  # msoShapeRightArrow

# Callout
$callout = $slide.Shapes.AddShape(105, 400, 250, 200, 100)  # msoShapeRoundedRectangularCallout

# Line
$line = $slide.Shapes.AddLine(100, 400, 500, 400)  # X1, Y1, X2, Y2

# Connector (arrow line)
$connector = $slide.Shapes.AddConnector(1, 100, 450, 500, 450)  # msoConnectorStraight
$connector.Line.EndArrowheadStyle = 2  # msoArrowheadTriangle
```

### Add a Chart

```powershell
# AddChart2(ChartStyle, ChartType, Left, Top, Width, Height)
$chartShape = $slide.Shapes.AddChart2(-1, 51, 50, 150, 600, 350)  # 51 = xlColumnClustered
$chart = $chartShape.Chart

# Edit chart data
$chartData = $chart.ChartData
$chartData.Activate()
$workbook = $chartData.Workbook
$ws = $workbook.Worksheets.Item(1)

# Clear existing data
$ws.UsedRange.Clear()

# Write new data
$ws.Range("A1").Value2 = "Category"
$ws.Range("B1").Value2 = "Series 1"
$ws.Range("C1").Value2 = "Series 2"
$ws.Range("A2").Value2 = "Q1"
$ws.Range("B2").Value2 = 100
$ws.Range("C2").Value2 = 80
$ws.Range("A3").Value2 = "Q2"
$ws.Range("B3").Value2 = 120
$ws.Range("C3").Value2 = 95

# Set chart source range
$chart.SetSourceData($ws.Range("A1:C3"))

# Title
$chart.HasTitle = $true
$chart.ChartTitle.Text = "Quarterly Results"

# Close the data editor
$workbook.Close($true)

# Legend
$chart.HasLegend = $true
$chart.Legend.Position = -4107  # xlBottom
```

### Set Shape Fill & Line

```powershell
$shape = $slide.Shapes.Item(1)

# Solid fill
$shape.Fill.Visible = -1
$shape.Fill.ForeColor.RGB = 0x4472C4        # Blue
$shape.Fill.Transparency = 0.2               # 20% transparent

# Gradient fill
$shape.Fill.TwoColorGradient(1, 1)           # msoGradientHorizontal, variant 1
$shape.Fill.ForeColor.RGB = 0x4472C4
$shape.Fill.BackColor.RGB = 0x70AD47

# No fill (transparent)
$shape.Fill.Visible = 0                      # msoFalse

# Line (border)
$shape.Line.Visible = -1
$shape.Line.ForeColor.RGB = 0x000000         # Black
$shape.Line.Weight = 2                        # 2 points
$shape.Line.DashStyle = 1                     # msoLineSolid

# No border
$shape.Line.Visible = 0

# Shadow
$shape.Shadow.Visible = -1
$shape.Shadow.Type = 21                       # msoShadow21
$shape.Shadow.ForeColor.RGB = 0x808080
```

### Add Slide Notes

```powershell
$slide = $pres.Slides.Item(1)
$slide.NotesPage.Shapes.Placeholders.Item(2).TextFrame.TextRange.Text = "Speaker notes for this slide. Remember to mention key points."
```

### Add Transitions

```powershell
$slide = $pres.Slides.Item(1)
$trans = $slide.SlideShowTransition

# Fade transition
$trans.EntryEffect = 3844          # ppEffectFade

# Duration
$trans.Duration = 1.5              # Seconds

# Advance automatically after 5 seconds
$trans.AdvanceOnTime = -1          # msoTrue
$trans.AdvanceTime = 5

# Advance on click
$trans.AdvanceOnClick = -1         # msoTrue

# Apply to all slides
foreach ($s in $pres.Slides) {
    $s.SlideShowTransition.EntryEffect = 3844
    $s.SlideShowTransition.Duration = 1.0
}
```

### Set Slide Background

```powershell
$slide = $pres.Slides.Item(1)
$bg = $slide.Background.Fill

# Solid color background
$bg.Visible = -1
$bg.Solid
$bg.ForeColor.RGB = 0x1F3864    # Dark blue

# Gradient background
$bg.TwoColorGradient(1, 1)
$bg.ForeColor.RGB = 0x1F3864
$bg.BackColor.RGB = 0x4472C4

# Image background
$bg.UserPicture("C:\path\to\background.jpg")

# Follow master slide background
$slide.FollowMasterBackground = -1
```

### Duplicate & Reorder Slides

```powershell
# Duplicate a slide
$newSlide = $pres.Slides.Item(1).Duplicate()

# Move a slide to a new position
$pres.Slides.Item(3).MoveTo(1)   # Move slide 3 to position 1

# Copy slide from another presentation
$sourcePres = $ppt.Presentations.Open("C:\path\to\source.pptx", $true)
$sourcePres.Slides.Item(2).Copy()
$pres.Slides.Paste($pres.Slides.Count + 1)
$sourcePres.Close()
```

### Delete Slides

```powershell
# Delete by index
$pres.Slides.Item(3).Delete()

# Delete last slide
$pres.Slides.Item($pres.Slides.Count).Delete()
```

### Save the Presentation

```powershell
# Save as .pptx
$savePath = "C:\path\to\output.pptx"
$pres.SaveAs($savePath, 24)   # 24 = ppSaveAsOpenXMLPresentation (.pptx)

# Format constants:
#   24 = ppSaveAsOpenXMLPresentation    (.pptx)
#   25 = ppSaveAsOpenXMLPresentationMacroEnabled (.pptm)
#   27 = ppSaveAsOpenXMLShow            (.ppsx — auto-play)
#   32 = ppSaveAsPDF                    (.pdf)
#   18 = ppSaveAsPNG                    (folder of PNGs, one per slide)
#   17 = ppSaveAsJPG                    (folder of JPGs)

# Save as PDF
$pres.SaveAs("C:\path\to\output.pdf", 32)

# Export all slides as images
$pres.SaveAs("C:\path\to\slides_folder", 18)  # Creates a folder with Slide1.png, Slide2.png, etc.

# Export a single slide as image
$pres.Slides.Item(1).Export("C:\path\to\slide1.png", "PNG", 1920, 1080)
```

---

## Practical Recipes

### Data-Driven Slide Deck

Generate slides from data (e.g., one slide per team member):

```powershell
$ppt = New-Object -ComObject PowerPoint.Application
$ppt.Visible = 1
$pres = $ppt.Presentations.Add()

# Title slide
$titleSlide = $pres.Slides.Add(1, 1)  # ppLayoutTitle
$titleSlide.Shapes.Placeholders.Item(1).TextFrame.TextRange.Text = "Team Overview"
$titleSlide.Shapes.Placeholders.Item(2).TextFrame.TextRange.Text = "Auto-generated report — $(Get-Date -Format 'MMMM yyyy')"

# Data
$team = @(
    @{ Name = "Alice"; Role = "Engineer"; Score = 95 },
    @{ Name = "Bob"; Role = "Designer"; Score = 88 },
    @{ Name = "Charlie"; Role = "Manager"; Score = 92 }
)

foreach ($member in $team) {
    $s = $pres.Slides.Add($pres.Slides.Count + 1, 2)  # ppLayoutText
    $s.Shapes.Placeholders.Item(1).TextFrame.TextRange.Text = $member.Name
    $body = $s.Shapes.Placeholders.Item(2).TextFrame.TextRange
    $body.Text = "Role: $($member.Role)`rScore: $($member.Score)`rStatus: $(if ($member.Score -ge 90) { 'Excellent' } else { 'Good' })"
    $body.Font.Size = 20
}

# Summary slide with table
$summarySlide = $pres.Slides.Add($pres.Slides.Count + 1, 12)  # ppLayoutBlank
$tableShape = $summarySlide.Shapes.AddTable($team.Count + 1, 3, 50, 80, 600, 250)
$table = $tableShape.Table

$table.Cell(1,1).Shape.TextFrame.TextRange.Text = "Name"
$table.Cell(1,2).Shape.TextFrame.TextRange.Text = "Role"
$table.Cell(1,3).Shape.TextFrame.TextRange.Text = "Score"

for ($i = 0; $i -lt $team.Count; $i++) {
    $table.Cell($i+2, 1).Shape.TextFrame.TextRange.Text = $team[$i].Name
    $table.Cell($i+2, 2).Shape.TextFrame.TextRange.Text = $team[$i].Role
    $table.Cell($i+2, 3).Shape.TextFrame.TextRange.Text = "$($team[$i].Score)"
}

$pres.SaveAs("C:\path\to\TeamOverview.pptx", 24)
$pres.Close()
$ppt.Quit()
```

### Template-Based Report

Fill in an existing template's placeholders:

```powershell
$ppt = New-Object -ComObject PowerPoint.Application
$ppt.Visible = 1
$pres = $ppt.Presentations.Open("C:\path\to\template.pptx")

# Replace placeholder text
foreach ($slide in $pres.Slides) {
    foreach ($shape in $slide.Shapes) {
        if ($shape.HasTextFrame) {
            $text = $shape.TextFrame.TextRange.Text
            $text = $text -replace '\{DATE\}', (Get-Date -Format 'MMMM dd, yyyy')
            $text = $text -replace '\{AUTHOR\}', 'Drory Shohat'
            $text = $text -replace '\{PROJECT\}', 'OfficeHelper'
            $shape.TextFrame.TextRange.Text = $text
        }
    }
}

$pres.SaveAs("C:\path\to\FilledReport.pptx", 24)
$pres.Close()
$ppt.Quit()
```

### Clone Conventions from Existing Presentation

#### Phase 1 — Analyze Source Presentation

```powershell
$ppt = New-Object -ComObject PowerPoint.Application
$ppt.Visible = 1
$pres = $ppt.Presentations.Open("C:\path\to\source.pptx", $true)

# Slide dimensions
Write-Output "Size: $($pres.PageSetup.SlideWidth/72) x $($pres.PageSetup.SlideHeight/72) inches"

# Available layouts
Write-Output "`n--- Layouts ---"
foreach ($layout in $pres.SlideMaster.CustomLayouts) {
    Write-Output "  $($layout.Name)"
}

# Per-slide analysis
foreach ($slide in $pres.Slides) {
    Write-Output "`n=== Slide $($slide.SlideIndex): $($slide.CustomLayout.Name) ==="
    foreach ($shape in $slide.Shapes) {
        $info = "  [$($shape.Name)] Type=$($shape.Type) Size=$($shape.Width)x$($shape.Height)"
        if ($shape.HasTextFrame) {
            $tf = $shape.TextFrame.TextRange
            $info += " | Font=$($tf.Font.Name) $($tf.Font.Size)pt"
            $info += " | Color=$($tf.Font.Color.RGB)"
            $info += " | Bold=$($tf.Font.Bold)"
            $info += " | Text='$($tf.Text.Substring(0, [Math]::Min(50, $tf.Text.Length)))'"
        }
        Write-Output $info
    }
}

# Background analysis
foreach ($slide in $pres.Slides) {
    $bg = $slide.Background.Fill
    Write-Output "Slide $($slide.SlideIndex) BG Type: $($bg.Type)"
}

$pres.Close()
$ppt.Quit()
```

#### Phase 2 — Recreate with Same Conventions

Use extracted layout names, fonts, sizes, colors, and dimensions to build the new presentation using the writing techniques above.

---

## Common Constants Reference

### ppSaveAsFileType

| Constant                                | Value | Extension |
|-----------------------------------------|-------|-----------|
| `ppSaveAsOpenXMLPresentation`           | 24    | `.pptx`   |
| `ppSaveAsOpenXMLPresentationMacroEnabled` | 25  | `.pptm`   |
| `ppSaveAsOpenXMLShow`                   | 27    | `.ppsx`   |
| `ppSaveAsPDF`                           | 32    | `.pdf`    |
| `ppSaveAsPNG`                           | 18    | `.png`    |
| `ppSaveAsJPG`                           | 17    | `.jpg`    |
| `ppSaveAsPresentation`                  | 1     | `.ppt`    |

### ppSlideLayout

| Layout                   | Value |
|--------------------------|-------|
| `ppLayoutTitle`          | 1     |
| `ppLayoutText`           | 2     |
| `ppLayoutTwoColumnText`  | 3     |
| `ppLayoutTable`          | 4     |
| `ppLayoutTextAndChart`   | 5     |
| `ppLayoutChartAndText`   | 6     |
| `ppLayoutTitleOnly`      | 11    |
| `ppLayoutBlank`          | 12    |
| `ppLayoutContentWithCaption` | 13|
| `ppLayoutPictureWithCaption` | 14|
| `ppLayoutTwoObjects`     | 29    |
| `ppLayoutSectionHeader`  | 37    |

### ppParagraphAlignment

| Alignment | Value |
|-----------|-------|
| Left      | 1     |
| Center    | 2     |
| Right     | 3     |
| Justify   | 4     |
| Distribute| 5     |

### msoShapeType (Common)

| Shape Type          | Value |
|---------------------|-------|
| AutoShape           | 1     |
| Callout             | 2     |
| Chart               | 3     |
| Comment             | 4     |
| Freeform            | 5     |
| Group               | 6     |
| EmbeddedOLE         | 7     |
| Line                | 9     |
| Picture             | 13    |
| Placeholder         | 14    |
| Table               | 19    |
| TextBox             | 17    |

### msoAutoShapeType (Common)

| Shape                     | Value |
|---------------------------|-------|
| Rectangle                 | 1     |
| Parallelogram             | 2     |
| Diamond                   | 4     |
| Rounded Rectangle         | 5     |
| Oval                      | 9     |
| Triangle                  | 7     |
| Right Arrow               | 33    |
| Left Arrow                | 34    |
| Up Arrow                  | 35    |
| Down Arrow                | 36    |
| Pentagon                  | 51    |
| Hexagon                   | 10    |
| Star 5-Point              | 12    |
| Heart                     | 21    |
| Lightning Bolt            | 22    |
| Rounded Rectangular Callout| 105  |

### msoTriState

| Value | Constant   | Meaning |
|-------|------------|---------|
| -1    | `msoTrue`  | True    |
| 0     | `msoFalse` | False   |

### ppEntryEffect (Transitions — Common)

| Transition      | Value |
|-----------------|-------|
| None            | 0     |
| Fade            | 3844  |
| Push            | 3845  |
| Wipe            | 3847  |
| Split           | 3848  |
| Cut             | 3849  |
| Cover           | 3850  |
| Dissolve        | 3851  |

### Common Colors (RGB — PowerPoint uses RGB, not BGR!)

| Color        | Value      |
|--------------|------------|
| Black        | `0x000000` |
| White        | `0xFFFFFF` |
| Red          | `0xFF0000` |
| Green        | `0x00FF00` |
| Blue         | `0x0000FF` |
| Yellow       | `0xFFFF00` |
| Orange       | `0xFFA500` |
| Brand Blue   | `0x0071C5` |
| Dark Blue    | `0x1F3864` |
| Accent Blue  | `0x4472C4` |

---

## Cleanup & Best Practices

**Always close and quit** to avoid orphaned processes:

```powershell
$pres.Close()
$ppt.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($ppt) | Out-Null
[System.GC]::Collect()
[System.GC]::WaitForPendingFinalizers()
```

**Kill orphaned processes** (if needed):

```powershell
Get-Process POWERPNT -ErrorAction SilentlyContinue | Stop-Process -Force
```

**Use try/finally for safe cleanup:**

```powershell
$ppt = New-Object -ComObject PowerPoint.Application
$ppt.Visible = 1
try {
    $pres = $ppt.Presentations.Open("C:\path\file.pptx")
    # ... work ...
} finally {
    if ($pres) { $pres.Close() }
    $ppt.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($ppt) | Out-Null
}
```

**Tips:**
- PowerPoint COM requires `Visible = $true` (unlike Word/Excel). Minimize the window if needed: `$ppt.WindowState = 2` (ppWindowMinimized).
- Use **points** for positioning (72 points = 1 inch, 28.35 points = 1 cm).
- PowerPoint uses **RGB** colors, while Word/Excel COM use **BGR** — don't mix them up.
- When building many slides, consider creating a template `.potx` first with your layouts, then programmatically filling in content. This is much easier than styling from scratch.
- Export slides as images for thumbnails: `$slide.Export("path.png", "PNG", 1920, 1080)`.
