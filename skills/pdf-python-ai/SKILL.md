---
name: Pdf Python Ai
description: >
  PDF operations using PyMuPDF library. PDF read/write automation using
  Python.
---

# Pdf Python Ai

## PDF Automation — Python Guide

**Source**: Drory Shohat (email, 2026-02-16)
**Scope**: global | **Category**: tool-guide

This guide covers reading and writing `.pdf` files using **Python**, including **AI-powered image analysis** via Azure OpenAI (o3 vision). Complements the PowerShell COM guides for Word, Excel, and PowerPoint in this workspace.

---

## Table of Contents

- [Setup](#setup)
- [Reading PDFs](#reading-pdfs)
  - [Open a PDF](#open-a-pdf)
  - [Read Full Text](#read-full-text)
  - [Read Page by Page](#read-page-by-page)
  - [Extract Metadata](#extract-metadata)
  - [Extract Table of Contents (Bookmarks)](#extract-table-of-contents-bookmarks)
  - [Extract Hyperlinks](#extract-hyperlinks)
  - [Extract Tables](#extract-tables)
  - [Extract Images](#extract-images)
  - [Extract Annotations](#extract-annotations)
  - [Search for Text](#search-for-text)
  - [Render Pages as Images](#render-pages-as-images)
- [AI-Powered Image Analysis](#ai-powered-image-analysis)
  - [Azure OpenAI Setup](#azure-openai-setup)
  - [Analyze a Single Image](#analyze-a-single-image)
  - [Extract Text from Images (AI OCR)](#extract-text-from-images-ai-ocr)
  - [Describe Charts & Diagrams](#describe-charts--diagrams)
  - [Full PDF Extraction with AI Vision](#full-pdf-extraction-with-ai-vision)
- [Writing PDFs](#writing-pdfs)
  - [Create a Simple PDF (fpdf2)](#create-a-simple-pdf-fpdf2)
  - [Add Text with Formatting](#add-text-with-formatting)
  - [Add Headers & Footers](#add-headers--footers)
  - [Add Images](#add-images)
  - [Add Tables](#add-tables)
  - [Add Hyperlinks](#add-hyperlinks-1)
  - [Add Table of Contents](#add-table-of-contents)
  - [Multi-Page Documents](#multi-page-documents)
  - [Create a PDF with ReportLab](#create-a-pdf-with-reportlab)
- [Modifying Existing PDFs](#modifying-existing-pdfs)
  - [Merge PDFs](#merge-pdfs)
  - [Split a PDF](#split-a-pdf)
  - [Extract Specific Pages](#extract-specific-pages)
  - [Rotate Pages](#rotate-pages)
  - [Add Watermark / Overlay](#add-watermark--overlay)
  - [Encrypt / Password-Protect](#encrypt--password-protect)
  - [Redact Text](#redact-text)
- [Practical Recipes](#practical-recipes)
  - [PDF to Markdown with AI Vision](#pdf-to-markdown-with-ai-vision)
  - [Batch Process PDF Folder](#batch-process-pdf-folder)
  - [Invoice / Report Generator](#invoice--report-generator)
- [PowerShell Integration](#powershell-integration)
- [Library Reference](#library-reference)

---

## Setup

### Python Environment

```powershell
# Use the workspace venv
$python = "python"

# Proxy settings (a corporate network)
$env:NO_PROXY = ".openai.azure.com,10.*,example.com,.example.com,10.0.0.0/8,192.168.0.0/16,localhost,.local,127.0.0.0/8,172.16.0.0/12,134.134.0.0/16,.search.windows.net"
$env:HTTP_PROXY = "http://proxy.example.com:8080"
$env:HTTPS_PROXY = "http://proxy.example.com:8080"

# Install dependencies
& $python -m pip install PyMuPDF openai httpx python-dotenv reportlab fpdf2 --proxy http://proxy.example.com:8080
```

### Required Libraries

| Library        | Purpose                          |
|----------------|----------------------------------|
| `PyMuPDF`      | Read/modify PDFs (text, images, metadata) |
| `fpdf2`        | Create new PDFs (lightweight)    |
| `reportlab`    | Create complex PDFs (advanced)   |
| `openai`       | Azure OpenAI for AI image analysis |
| `httpx`        | HTTP client with explicit proxy support |
| `python-dotenv`| Load API keys from `.env`        |

### .env File

To use the AI-powered features (image analysis, OCR, chart description), you need an Azure OpenAI API key.

**How to get your API key:**

1. Go to the [your Azure subscription](https://portal.azure.com) and navigate to your Azure OpenAI resource
2. Navigate to **Azure OpenAI** → select the `your-azure-openai-resource` resource
3. Go to **Keys and Endpoint** → copy **Key 1** or **Key 2**
4. Create a `.env` file in the workspace root:

```env
API_KEY=paste_your_key_here
```

> **Important:** Never commit `.env` to version control. Add it to `.gitignore`.

---

## Reading PDFs

### Open a PDF

```python
import fitz  # PyMuPDF

doc = fitz.open("path/to/file.pdf")
print(f"Pages: {doc.page_count}")
print(f"Metadata: {doc.metadata}")
```

Open a password-protected PDF:

```python
doc = fitz.open("path/to/encrypted.pdf")
doc.authenticate("password123")
```

### Read Full Text

```python
doc = fitz.open("path/to/file.pdf")
full_text = ""
for page in doc:
    full_text += page.get_text()
print(full_text)
doc.close()
```

### Read Page by Page

```python
doc = fitz.open("path/to/file.pdf")

for page_num in range(doc.page_count):
    page = doc[page_num]
    text = page.get_text()
    print(f"=== Page {page_num + 1} ===")
    print(text)

# Read a specific page
page = doc[0]  # First page (0-indexed)
print(page.get_text())
```

**Text extraction modes:**

```python
page = doc[0]

# Default: plain text
text = page.get_text("text")

# Preserve layout (whitespace positioning)
text = page.get_text("text", flags=fitz.TEXT_PRESERVE_WHITESPACE)

# As HTML
html = page.get_text("html")

# As dictionary (detailed: spans, fonts, sizes, colors)
blocks = page.get_text("dict")
for block in blocks["blocks"]:
    if block["type"] == 0:  # Text block
        for line in block["lines"]:
            for span in line["spans"]:
                print(f"  Font: {span['font']}, Size: {span['size']}, "
                      f"Color: #{span['color']:06x}, Text: {span['text']}")

# As JSON
json_text = page.get_text("json")

# Words with positions (word, x0, y0, x1, y1, block, line, word_num)
words = page.get_text("words")
for w in words:
    print(f"  '{w[4]}' at ({w[0]:.0f}, {w[1]:.0f})")
```

### Extract Metadata

```python
doc = fitz.open("path/to/file.pdf")

meta = doc.metadata
print(f"Title:    {meta.get('title', 'N/A')}")
print(f"Author:   {meta.get('author', 'N/A')}")
print(f"Subject:  {meta.get('subject', 'N/A')}")
print(f"Creator:  {meta.get('creator', 'N/A')}")
print(f"Producer: {meta.get('producer', 'N/A')}")
print(f"Created:  {meta.get('creationDate', 'N/A')}")
print(f"Modified: {meta.get('modDate', 'N/A')}")
print(f"Pages:    {doc.page_count}")
print(f"Encrypted: {doc.is_encrypted}")
```

### Extract Table of Contents (Bookmarks)

```python
toc = doc.get_toc()  # Returns list of [level, title, page_number]

for entry in toc:
    level, title, page = entry
    indent = "  " * (level - 1)
    print(f"{indent}{title} (page {page})")
```

Example output:
```
Chapter 1: Introduction (page 1)
  1.1 Background (page 3)
  1.2 Objectives (page 5)
Chapter 2: Methods (page 8)
```

### Extract Hyperlinks

```python
for page_num in range(doc.page_count):
    page = doc[page_num]
    links = page.get_links()
    for link in links:
        link_type = link.get("kind")  # 0=internal, 1=URI, 2=launch, 3=named
        if link_type == 1:  # External URL
            print(f"Page {page_num+1}: {link.get('uri')}")
        elif link_type == 0:  # Internal link
            print(f"Page {page_num+1}: -> page {link.get('page', '?') + 1}")
```

### Extract Tables

PyMuPDF can detect tables:

```python
page = doc[0]
tables = page.find_tables()

for i, table in enumerate(tables):
    print(f"=== Table {i+1} ({table.row_count} rows x {table.col_count} cols) ===")
    data = table.extract()
    for row in data:
        print(" | ".join(str(cell) if cell else "" for cell in row))
```

### Extract Images

```python
doc = fitz.open("path/to/file.pdf")

for page_num in range(doc.page_count):
    page = doc[page_num]
    images = page.get_images(full=True)

    for img_idx, img in enumerate(images):
        xref = img[0]
        base_image = doc.extract_image(xref)
        image_bytes = base_image["image"]
        image_ext = base_image["ext"]       # e.g. "png", "jpeg"
        image_width = base_image["width"]
        image_height = base_image["height"]

        # Save to file
        output_path = f"page{page_num+1}_img{img_idx+1}.{image_ext}"
        with open(output_path, "wb") as f:
            f.write(image_bytes)
        print(f"Saved: {output_path} ({image_width}x{image_height})")
```

### Extract Annotations

```python
for page in doc:
    annots = page.annots()
    if annots:
        for annot in annots:
            print(f"  Type: {annot.type}, Content: {annot.info.get('content', '')}")
```

### Search for Text

```python
page = doc[0]

# Search returns list of Rect objects (bounding boxes)
results = page.search_for("keyword")
print(f"Found {len(results)} matches on page 1")

for rect in results:
    print(f"  At position: ({rect.x0:.0f}, {rect.y0:.0f}) to ({rect.x1:.0f}, {rect.y1:.0f})")

# Highlight search results
for rect in results:
    highlight = page.add_highlight_annot(rect)
    highlight.update()

# Save with highlights
doc.save("highlighted_output.pdf")
```

### Render Pages as Images

```python
page = doc[0]

# Render at default resolution (72 DPI)
pix = page.get_pixmap()
pix.save("page1.png")

# Render at higher resolution (300 DPI for print quality)
zoom = 300 / 72  # 4.17x zoom
mat = fitz.Matrix(zoom, zoom)
pix = page.get_pixmap(matrix=mat)
pix.save("page1_hires.png")

# Render all pages
for page_num in range(doc.page_count):
    page = doc[page_num]
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 144 DPI
    pix.save(f"page_{page_num+1}.png")
```

---

## AI-Powered Image Analysis

Use Azure OpenAI's o3 model with vision capabilities to understand images extracted from PDFs — including diagrams, charts, handwritten text, screenshots, and more.

### Azure OpenAI Setup

> **Note:** On the a corporate network, the `openai` SDK may route requests through the HTTP proxy, which can cause connection timeouts to Azure OpenAI. The fix is to create an explicit `httpx.Client` with `proxy` set to the corporate proxy. The `NO_PROXY` env var alone is not reliably honoured by httpx.

```python
import os
import base64
import httpx
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()  # Loads API_KEY from .env file

# Explicit proxy for a corporate network — avoids connection timeouts
http_client = httpx.Client(
    timeout=httpx.Timeout(300.0, connect=60.0),
    proxy="http://proxy.example.com:8080",
)

client = AzureOpenAI(
    azure_endpoint="https://your-azure-openai-resource.openai.azure.com/",
    api_key=os.getenv("API_KEY"),
    api_version="2025-01-01-preview",
    http_client=http_client,
)
DEPLOYMENT = "o3"
```

> **o3 parameter note:** The o3 model requires `max_completion_tokens` instead of `max_tokens`. Using `max_tokens` will return a 400 error.

### Analyze a Single Image

```python
def analyze_image(image_path: str, prompt: str = "Describe this image in detail.") -> str:
    """Send an image to Azure OpenAI o3 for analysis."""
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")

    # Detect MIME type
    ext = image_path.rsplit(".", 1)[-1].lower()
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
            "gif": "image/gif", "webp": "image/webp", "bmp": "image/bmp"}.get(ext, "image/png")

    response = client.chat.completions.create(
        model=DEPLOYMENT,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {
                        "url": f"data:{mime};base64,{image_data}"
                    }}
                ]
            }
        ],
        max_completion_tokens=4096,
    )
    return response.choices[0].message.content
```

### Analyze from Bytes (No File Save Needed)

```python
def analyze_image_bytes(image_bytes: bytes, ext: str = "png",
                        prompt: str = "Describe this image in detail.") -> str:
    """Analyze image bytes directly without saving to disk."""
    image_data = base64.b64encode(image_bytes).decode("utf-8")
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg"}.get(ext, "image/png")

    response = client.chat.completions.create(
        model=DEPLOYMENT,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {
                        "url": f"data:{mime};base64,{image_data}"
                    }}
                ]
            }
        ],
        max_completion_tokens=4096,
    )
    return response.choices[0].message.content
```

### Extract Text from Images (AI OCR)

```python
def ocr_image(image_path: str) -> str:
    """Extract all text from an image using AI vision."""
    return analyze_image(image_path,
        prompt="Extract ALL text from this image. Return only the text content, "
               "preserving the original layout and formatting as closely as possible. "
               "If there are tables, format them as markdown tables."
    )
```

### Describe Charts & Diagrams

```python
def describe_chart(image_path: str) -> str:
    """Get a detailed description of a chart or diagram."""
    return analyze_image(image_path,
        prompt="Analyze this chart/diagram in detail. Include:\n"
               "1. Type of chart (bar, line, pie, flowchart, etc.)\n"
               "2. Title and axis labels\n"
               "3. All data points and values visible\n"
               "4. Key trends or insights\n"
               "5. Any legends or annotations\n"
               "Return a structured description with the data."
    )
```

### Full PDF Extraction with AI Vision

This is the main recipe — extract everything from a PDF, including AI analysis of all images:

```python
import fitz
import base64
import os
import httpx
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

# Explicit proxy for a corporate network
http_client = httpx.Client(
    timeout=httpx.Timeout(300.0, connect=60.0),
    proxy="http://proxy.example.com:8080",
)

client = AzureOpenAI(
    azure_endpoint="https://your-azure-openai-resource.openai.azure.com/",
    api_key=os.getenv("API_KEY"),
    api_version="2025-01-01-preview",
    http_client=http_client,
)
DEPLOYMENT = "o3"


def analyze_image_bytes(image_bytes, ext="png", prompt="Describe this image in detail."):
    image_data = base64.b64encode(image_bytes).decode("utf-8")
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg"}.get(ext, "image/png")
    response = client.chat.completions.create(
        model=DEPLOYMENT,
        messages=[{"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{image_data}"}}
        ]}],
        max_completion_tokens=4096,
    )
    return response.choices[0].message.content


def extract_pdf_full(pdf_path, analyze_images=True):
    """
    Extract all content from a PDF including AI-analyzed images.

    Returns a list of dicts, one per page:
    {
        "page": int,
        "text": str,
        "tables": list[list[list[str]]],
        "images": list[{"bytes": bytes, "ext": str, "description": str}],
        "links": list[dict],
    }
    """
    doc = fitz.open(pdf_path)
    results = []

    for page_num in range(doc.page_count):
        page = doc[page_num]
        page_data = {
            "page": page_num + 1,
            "text": page.get_text("text"),
            "tables": [],
            "images": [],
            "links": [],
        }

        # Extract tables
        for table in page.find_tables():
            page_data["tables"].append(table.extract())

        # Extract and analyze images
        for img_idx, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base_image = doc.extract_image(xref)
            img_info = {
                "index": img_idx + 1,
                "ext": base_image["ext"],
                "width": base_image["width"],
                "height": base_image["height"],
                "size_kb": len(base_image["image"]) / 1024,
            }

            if analyze_images:
                print(f"  Analyzing image {img_idx+1} on page {page_num+1}...")
                try:
                    description = analyze_image_bytes(
                        base_image["image"],
                        base_image["ext"],
                        prompt="Analyze this image from a PDF document. "
                               "Extract any text, describe any charts/diagrams, "
                               "and summarize the visual content. "
                               "If it contains a table, format it as markdown."
                    )
                    img_info["description"] = description
                except Exception as e:
                    img_info["description"] = f"[Analysis failed: {e}]"
            else:
                img_info["description"] = "[Skipped]"

            page_data["images"].append(img_info)

        # Extract links
        for link in page.get_links():
            if link.get("kind") == 1:
                page_data["links"].append({"type": "url", "uri": link.get("uri")})
            elif link.get("kind") == 0:
                page_data["links"].append({"type": "internal", "target_page": link.get("page", 0) + 1})

        results.append(page_data)
        print(f"Page {page_num+1}/{doc.page_count} processed.")

    doc.close()
    return results


# === Usage ===
if __name__ == "__main__":
    pages = extract_pdf_full("path/to/document.pdf", analyze_images=True)

    for p in pages:
        print(f"\n{'='*60}")
        print(f"PAGE {p['page']}")
        print(f"{'='*60}")
        print(p["text"][:500])

        if p["tables"]:
            print(f"\n  Tables: {len(p['tables'])}")
            for t in p["tables"]:
                for row in t:
                    print("  " + " | ".join(str(c) for c in row))

        if p["images"]:
            print(f"\n  Images: {len(p['images'])}")
            for img in p["images"]:
                print(f"  - Image {img['index']} ({img['width']}x{img['height']}, "
                      f"{img['size_kb']:.1f} KB)")
                print(f"    AI Description: {img['description'][:200]}...")

        if p["links"]:
            print(f"\n  Links: {len(p['links'])}")
            for link in p["links"]:
                print(f"  - {link}")
```

### Analyze Full Pages as Screenshots

For PDFs with complex layouts where text extraction misses visual context:

```python
def extract_pdf_as_screenshots(pdf_path, dpi=200):
    """
    Render each page as an image and send to AI for full-page analysis.
    Best for: scanned documents, complex layouts, mixed text+graphics.
    """
    doc = fitz.open(pdf_path)
    results = []

    zoom = dpi / 72
    mat = fitz.Matrix(zoom, zoom)

    for page_num in range(doc.page_count):
        page = doc[page_num]
        pix = page.get_pixmap(matrix=mat)
        img_bytes = pix.tobytes("png")

        print(f"Analyzing page {page_num+1}/{doc.page_count} as screenshot...")
        description = analyze_image_bytes(
            img_bytes, "png",
            prompt="This is a screenshot of a PDF page. Extract ALL content:\n"
                   "1. All text, preserving headings and structure\n"
                   "2. Describe any images, charts, or diagrams\n"
                   "3. Extract any tables as markdown tables\n"
                   "4. Note any special formatting (bold, italic, colors)\n"
                   "Return the content as clean markdown."
        )
        results.append({
            "page": page_num + 1,
            "content": description
        })

    doc.close()
    return results
```

---

## Writing PDFs

### Create a Simple PDF (fpdf2)

```python
from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("Helvetica", size=16)
pdf.cell(text="Hello, World!", center=True, new_x="LMARGIN", new_y="NEXT")

pdf.set_font("Helvetica", size=12)
pdf.cell(text="This is a simple PDF created with Python.", new_x="LMARGIN", new_y="NEXT")

pdf.output("output.pdf")
```

### Add Text with Formatting

```python
from fpdf import FPDF

pdf = FPDF()
pdf.add_page()

# Title
pdf.set_font("Helvetica", "B", 24)
pdf.cell(text="Document Title", center=True, new_x="LMARGIN", new_y="NEXT")
pdf.ln(10)

# Subtitle
pdf.set_font("Helvetica", "I", 14)
pdf.set_text_color(100, 100, 100)  # Gray
pdf.cell(text="A subtitle with gray italic text", center=True, new_x="LMARGIN", new_y="NEXT")
pdf.ln(15)

# Body text
pdf.set_font("Helvetica", "", 11)
pdf.set_text_color(0, 0, 0)  # Black
pdf.multi_cell(w=0, text=(
    "This is body text that wraps automatically. It supports "
    "multiple paragraphs and line breaks. You can set fonts, "
    "sizes, colors, and alignment."
))
pdf.ln(5)

# Bold text inline (using write)
pdf.set_font("Helvetica", "B", 11)
pdf.write(text="Bold text ")
pdf.set_font("Helvetica", "", 11)
pdf.write(text="followed by normal text.")
pdf.ln(10)

# Colored text
pdf.set_text_color(0, 113, 197)  # Brand Blue
pdf.set_font("Helvetica", "B", 12)
pdf.cell(text="Brand Blue colored text", new_x="LMARGIN", new_y="NEXT")
pdf.set_text_color(0, 0, 0)

# Right-aligned text
pdf.cell(w=0, text="Right aligned", align="R", new_x="LMARGIN", new_y="NEXT")

pdf.output("formatted.pdf")
```

### Add Headers & Footers

```python
from fpdf import FPDF

class PDFWithHeaderFooter(FPDF):
    def header(self):
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(128, 128, 128)
        self.cell(w=0, text="CONFIDENTIAL — Example Corp", align="C",
                  new_x="LMARGIN", new_y="NEXT")
        self.line(10, 15, self.w - 10, 15)  # Horizontal line
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(w=0, text=f"Page {self.page_no()}/{{nb}}", align="C")

pdf = PDFWithHeaderFooter()
pdf.alias_nb_pages()
pdf.add_page()
pdf.set_font("Helvetica", size=12)
pdf.cell(text="Content goes here", new_x="LMARGIN", new_y="NEXT")
pdf.output("with_header_footer.pdf")
```

### Add Images

```python
pdf = FPDF()
pdf.add_page()

# Add image with automatic sizing
pdf.image("path/to/image.png", x=10, y=30, w=100)

# Add image centered
page_width = pdf.w - 2 * pdf.l_margin
pdf.image("path/to/image.png", x=(pdf.w - 120) / 2, w=120)

# Add image with specific dimensions
pdf.image("path/to/image.png", x=10, y=100, w=80, h=60)

# Add image from URL
pdf.image("https://example.com/image.png", x=10, w=100)

pdf.output("with_images.pdf")
```

### Add Tables

```python
from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("Helvetica", size=10)

# Table data
headers = ["Name", "Department", "Score", "Status"]
data = [
    ["Alice", "Engineering", "95", "Pass"],
    ["Bob", "Design", "88", "Pass"],
    ["Charlie", "Marketing", "72", "Review"],
    ["Diana", "Engineering", "97", "Pass"],
]

col_widths = [45, 45, 30, 30]

# Header row
pdf.set_fill_color(0, 113, 197)   # Brand Blue
pdf.set_text_color(255, 255, 255)  # White
pdf.set_font("Helvetica", "B", 10)
for i, header in enumerate(headers):
    pdf.cell(w=col_widths[i], h=10, text=header, border=1,
             align="C", fill=True, new_x="RIGHT", new_y="TOP")
pdf.ln()

# Data rows
pdf.set_text_color(0, 0, 0)
pdf.set_font("Helvetica", "", 10)
for row_idx, row in enumerate(data):
    # Alternating row colors
    if row_idx % 2 == 0:
        pdf.set_fill_color(240, 240, 240)
    else:
        pdf.set_fill_color(255, 255, 255)

    for i, cell in enumerate(row):
        pdf.cell(w=col_widths[i], h=8, text=cell, border=1,
                 align="C", fill=True, new_x="RIGHT", new_y="TOP")
    pdf.ln()

pdf.output("with_table.pdf")
```

### Add Hyperlinks

```python
pdf = FPDF()
pdf.add_page()
pdf.set_font("Helvetica", size=12)

# External URL link
pdf.set_text_color(0, 0, 255)
pdf.cell(w=0, text="Visit Example.com", link="https://www.example.com",
         new_x="LMARGIN", new_y="NEXT")

# Internal link (to another page)
pdf.add_page()
pdf.set_font("Helvetica", "B", 16)
link_target = pdf.add_link(page=1)
pdf.cell(w=0, text="Go back to page 1", link=link_target,
         new_x="LMARGIN", new_y="NEXT")

pdf.output("with_links.pdf")
```

### Add Table of Contents

```python
from fpdf import FPDF

class PDFWithTOC(FPDF):
    def __init__(self):
        super().__init__()
        self.toc_entries = []

    def add_heading(self, text, level=1):
        sizes = {1: 20, 2: 16, 3: 13}
        fonts = {1: "B", 2: "B", 3: "BI"}

        # Record TOC entry
        self.toc_entries.append({
            "title": text,
            "level": level,
            "page": self.page_no()
        })

        self.set_font("Helvetica", fonts.get(level, ""), sizes.get(level, 12))
        self.cell(text=text, new_x="LMARGIN", new_y="NEXT")
        self.ln(5)

    def insert_toc(self):
        self.add_page()
        self.set_font("Helvetica", "B", 20)
        self.cell(text="Table of Contents", center=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(10)

        self.set_font("Helvetica", "", 11)
        for entry in self.toc_entries:
            indent = "    " * (entry["level"] - 1)
            self.cell(
                w=0,
                text=f"{indent}{entry['title']}",
                new_x="LMARGIN", new_y="NEXT"
            )
        self.ln(5)


pdf = PDFWithTOC()

# Build content
pdf.add_page()
pdf.add_heading("Chapter 1: Introduction", level=1)
pdf.set_font("Helvetica", "", 11)
pdf.multi_cell(w=0, text="Content of chapter 1...")
pdf.ln(5)

pdf.add_heading("1.1 Background", level=2)
pdf.multi_cell(w=0, text="Background content...")

pdf.add_page()
pdf.add_heading("Chapter 2: Methods", level=1)
pdf.multi_cell(w=0, text="Methods content...")

# Insert TOC at the beginning (after generating content)
# Note: fpdf2 doesn't support inserting pages, so build TOC first
# or use reportlab for more control

pdf.output("with_toc.pdf")
```

### Multi-Page Documents

```python
pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)

# Long text that auto-paginates
pdf.add_page()
pdf.set_font("Helvetica", size=11)

long_text = "Lorem ipsum... " * 500  # Very long text
pdf.multi_cell(w=0, text=long_text)

# Manual page breaks
pdf.add_page()
pdf.set_font("Helvetica", "B", 16)
pdf.cell(text="New Section on New Page", new_x="LMARGIN", new_y="NEXT")

# Landscape page
pdf.add_page(orientation="L")
pdf.cell(text="Landscape page", new_x="LMARGIN", new_y="NEXT")

pdf.output("multipage.pdf")
```

### Create a PDF with ReportLab

For more complex PDFs with precise positioning:

```python
from reportlab.lib.pagesizes import A4, letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import HexColor, black, blue, white

# Basic document
c = canvas.Canvas("reportlab_output.pdf", pagesize=A4)
width, height = A4

# Title
c.setFont("Helvetica-Bold", 24)
c.drawCentredString(width / 2, height - 50, "Report Title")

# Body text
c.setFont("Helvetica", 12)
c.drawString(72, height - 100, "This is body text at exact coordinates.")

# Colored text
c.setFillColor(HexColor("#0071C5"))  # Brand Blue
c.drawString(72, height - 130, "Brand Blue colored text")
c.setFillColor(black)

# Shapes
c.setStrokeColor(blue)
c.setFillColor(HexColor("#E8F0FE"))
c.rect(72, height - 250, 200, 80, fill=True)

# Image
c.drawImage("path/to/image.png", 72, 100, width=200, height=150)

# Line
c.setStrokeColor(black)
c.line(72, height - 80, width - 72, height - 80)

# Save
c.showPage()
c.save()
```

**ReportLab with Platypus (high-level API for flowing documents):**

```python
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white

doc = SimpleDocTemplate("platypus_output.pdf", pagesize=A4)
styles = getSampleStyleSheet()

# Custom style
styles.add(ParagraphStyle(
    name="IntelBlue",
    parent=styles["Heading1"],
    textColor=HexColor("#0071C5"),
))

story = []

# Title
story.append(Paragraph("Report Title", styles["Title"]))
story.append(Spacer(1, 12))

# Paragraphs
story.append(Paragraph("This is a paragraph with <b>bold</b> and <i>italic</i> text.", styles["Normal"]))
story.append(Spacer(1, 12))

# Table
data = [
    ["Name", "Score", "Status"],
    ["Alice", "95", "Pass"],
    ["Bob", "88", "Pass"],
]
table = Table(data, colWidths=[150, 80, 80])
table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), HexColor("#0071C5")),
    ("TEXTCOLOR", (0, 0), (-1, 0), white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("GRID", (0, 0), (-1, -1), 1, black),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, HexColor("#F0F0F0")]),
]))
story.append(table)

doc.build(story)
```

---

## Modifying Existing PDFs

### Merge PDFs

```python
import fitz

output = fitz.open()

files = ["file1.pdf", "file2.pdf", "file3.pdf"]
for f in files:
    doc = fitz.open(f)
    output.insert_pdf(doc)
    doc.close()

output.save("merged.pdf")
output.close()
```

### Split a PDF

```python
doc = fitz.open("large_document.pdf")

# Split into individual pages
for page_num in range(doc.page_count):
    single = fitz.open()
    single.insert_pdf(doc, from_page=page_num, to_page=page_num)
    single.save(f"page_{page_num + 1}.pdf")
    single.close()

doc.close()
```

### Extract Specific Pages

```python
doc = fitz.open("source.pdf")
output = fitz.open()

# Extract pages 3, 5, 7 (0-indexed: 2, 4, 6)
for page_num in [2, 4, 6]:
    output.insert_pdf(doc, from_page=page_num, to_page=page_num)

# Or extract a range (pages 5-10)
output.insert_pdf(doc, from_page=4, to_page=9)

output.save("extracted.pdf")
```

### Rotate Pages

```python
doc = fitz.open("source.pdf")

# Rotate page 1 by 90 degrees clockwise
doc[0].set_rotation(90)

# Rotate all pages
for page in doc:
    page.set_rotation(180)  # 0, 90, 180, 270

doc.save("rotated.pdf")
```

### Add Watermark / Overlay

```python
import fitz

doc = fitz.open("source.pdf")

for page in doc:
    # Text watermark
    rect = page.rect
    text = "CONFIDENTIAL"

    # Create a text writer for the watermark
    tw = fitz.TextWriter(page.rect)
    font = fitz.Font("helv")
    fontsize = 60

    # Calculate center position
    text_width = font.text_length(text, fontsize=fontsize)
    x = (rect.width - text_width) / 2
    y = rect.height / 2

    # Insert semi-transparent watermark
    page.insert_text(
        (x, y),
        text,
        fontsize=fontsize,
        fontname="helv",
        color=(0.8, 0.8, 0.8),  # Light gray
        rotate=45,
    )

doc.save("watermarked.pdf")
```

### Encrypt / Password-Protect

```python
doc = fitz.open("source.pdf")

# Encrypt with password
doc.save(
    "encrypted.pdf",
    encryption=fitz.PDF_ENCRYPT_AES_256,
    owner_pw="owner_password",   # Full access password
    user_pw="user_password",      # View-only password
    permissions=(
        fitz.PDF_PERM_PRINT |      # Allow printing
        fitz.PDF_PERM_COPY         # Allow copy
        # Omit to deny: fitz.PDF_PERM_MODIFY, fitz.PDF_PERM_ANNOTATE
    ),
)
```

### Redact Text

```python
doc = fitz.open("source.pdf")
page = doc[0]

# Find and redact text
results = page.search_for("CONFIDENTIAL DATA")
for rect in results:
    page.add_redact_annot(rect, fill=(0, 0, 0))  # Black fill

# Apply all redactions (permanently removes content)
page.apply_redactions()

doc.save("redacted.pdf")
```

---

## Practical Recipes

### PDF to Markdown with AI Vision

Convert an entire PDF to clean markdown, using AI to understand images:

```python
import fitz
import base64
import os
import httpx
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

# Explicit proxy for a corporate network
http_client = httpx.Client(
    timeout=httpx.Timeout(300.0, connect=60.0),
    proxy="http://proxy.example.com:8080",
)

client = AzureOpenAI(
    azure_endpoint="https://your-azure-openai-resource.openai.azure.com/",
    api_key=os.getenv("API_KEY"),
    api_version="2025-01-01-preview",
    http_client=http_client,
)
DEPLOYMENT = "o3"


def pdf_to_markdown(pdf_path, output_md_path, use_ai_for_images=True, dpi=200):
    """Convert a PDF to a markdown file, with AI image descriptions."""
    doc = fitz.open(pdf_path)
    md_lines = [f"# {doc.metadata.get('title', os.path.basename(pdf_path))}\n"]

    # Add TOC if available
    toc = doc.get_toc()
    if toc:
        md_lines.append("## Table of Contents\n")
        for level, title, page in toc:
            indent = "  " * (level - 1)
            md_lines.append(f"{indent}- {title} (p.{page})")
        md_lines.append("\n---\n")

    zoom = dpi / 72
    mat = fitz.Matrix(zoom, zoom)

    for page_num in range(doc.page_count):
        page = doc[page_num]
        md_lines.append(f"\n---\n\n## Page {page_num + 1}\n")

        # Extract text
        text = page.get_text("text").strip()
        if text:
            md_lines.append(text)

        # Extract tables
        for table in page.find_tables():
            data = table.extract()
            if data:
                md_lines.append("\n")
                # Header row
                headers = [str(c) if c else "" for c in data[0]]
                md_lines.append("| " + " | ".join(headers) + " |")
                md_lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
                for row in data[1:]:
                    cells = [str(c) if c else "" for c in row]
                    md_lines.append("| " + " | ".join(cells) + " |")
                md_lines.append("")

        # Extract and describe images
        images = page.get_images(full=True)
        if images and use_ai_for_images:
            for img_idx, img in enumerate(images):
                xref = img[0]
                base_image = doc.extract_image(xref)
                img_bytes = base_image["image"]
                ext = base_image["ext"]

                # Skip tiny images (likely icons/bullets)
                if base_image["width"] < 50 or base_image["height"] < 50:
                    continue

                print(f"  Analyzing image {img_idx+1} on page {page_num+1}...")
                try:
                    img_b64 = base64.b64encode(img_bytes).decode("utf-8")
                    mime = {"png": "image/png", "jpeg": "image/jpeg",
                            "jpg": "image/jpeg"}.get(ext, "image/png")
                    response = client.chat.completions.create(
                        model=DEPLOYMENT,
                        messages=[{"role": "user", "content": [
                            {"type": "text", "text":
                             "Describe this image from a PDF. If it contains text, "
                             "extract it. If it's a chart/diagram, describe the data "
                             "and insights. Be concise but thorough."},
                            {"type": "image_url", "image_url": {
                                "url": f"data:{mime};base64,{img_b64}"}}
                        ]}],
                        max_completion_tokens=2048,
                    )
                    desc = response.choices[0].message.content
                    md_lines.append(f"\n> **[Image {img_idx+1}]:** {desc}\n")
                except Exception as e:
                    md_lines.append(f"\n> **[Image {img_idx+1}]:** *(Analysis failed: {e})*\n")

    doc.close()

    # Write markdown file
    with open(output_md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    print(f"Saved: {output_md_path}")
    return output_md_path


# === Usage ===
pdf_to_markdown("input.pdf", "output.md", use_ai_for_images=True)
```

### Batch Process PDF Folder

```python
import os
import fitz

def batch_extract_text(folder_path, output_folder):
    """Extract text from all PDFs in a folder."""
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(folder_path, filename)
            txt_path = os.path.join(output_folder, filename.replace(".pdf", ".txt"))

            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()

            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(text)

            print(f"Extracted: {filename} -> {txt_path}")


def batch_merge_pdfs(folder_path, output_path):
    """Merge all PDFs in a folder into one."""
    output = fitz.open()
    files = sorted(f for f in os.listdir(folder_path) if f.lower().endswith(".pdf"))

    for filename in files:
        doc = fitz.open(os.path.join(folder_path, filename))
        output.insert_pdf(doc)
        doc.close()
        print(f"Added: {filename}")

    output.save(output_path)
    output.close()
    print(f"Merged {len(files)} PDFs -> {output_path}")
```

### Invoice / Report Generator

```python
from fpdf import FPDF
from datetime import datetime

def generate_invoice(invoice_data, output_path):
    """
    invoice_data = {
        "number": "INV-2026-001",
        "date": "2026-02-16",
        "company": "Example Corp",
        "items": [
            {"description": "Engineering Services", "qty": 40, "rate": 150},
            {"description": "Design Review", "qty": 8, "rate": 200},
        ]
    }
    """

    class InvoicePDF(FPDF):
        def header(self):
            self.set_font("Helvetica", "B", 20)
            self.set_text_color(0, 113, 197)
            self.cell(w=0, text="INVOICE", align="R", new_x="LMARGIN", new_y="NEXT")
            self.line(10, 25, self.w - 10, 25)
            self.ln(10)

        def footer(self):
            self.set_y(-15)
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(128, 128, 128)
            self.cell(w=0, text=f"Page {self.page_no()}", align="C")

    pdf = InvoicePDF()
    pdf.add_page()

    # Invoice details
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(w=95, text=f"Invoice #: {invoice_data['number']}", new_x="RIGHT")
    pdf.cell(w=95, text=f"Date: {invoice_data['date']}", align="R",
             new_x="LMARGIN", new_y="NEXT")
    pdf.cell(w=0, text=f"To: {invoice_data['company']}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(15)

    # Table header
    col_w = [80, 30, 35, 45]
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(0, 113, 197)
    pdf.set_text_color(255, 255, 255)
    for i, h in enumerate(["Description", "Qty", "Rate", "Amount"]):
        pdf.cell(w=col_w[i], h=10, text=h, border=1, align="C", fill=True,
                 new_x="RIGHT", new_y="TOP")
    pdf.ln()

    # Table rows
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(0, 0, 0)
    total = 0
    for item in invoice_data["items"]:
        amount = item["qty"] * item["rate"]
        total += amount
        pdf.cell(w=col_w[0], h=8, text=item["description"], border=1, new_x="RIGHT", new_y="TOP")
        pdf.cell(w=col_w[1], h=8, text=str(item["qty"]), border=1, align="C", new_x="RIGHT", new_y="TOP")
        pdf.cell(w=col_w[2], h=8, text=f"${item['rate']:,.2f}", border=1, align="R", new_x="RIGHT", new_y="TOP")
        pdf.cell(w=col_w[3], h=8, text=f"${amount:,.2f}", border=1, align="R", new_x="LMARGIN", new_y="NEXT")

    # Total
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(w=sum(col_w[:3]), h=12, text="TOTAL", border=1, align="R", new_x="RIGHT", new_y="TOP")
    pdf.cell(w=col_w[3], h=12, text=f"${total:,.2f}", border=1, align="R",
             new_x="LMARGIN", new_y="NEXT")

    pdf.output(output_path)
    print(f"Invoice saved: {output_path}")


# Usage
generate_invoice({
    "number": "INV-2026-042",
    "date": "2026-02-16",
    "company": "Example Corp",
    "items": [
        {"description": "Engineering Services", "qty": 40, "rate": 150},
        {"description": "Design Review", "qty": 8, "rate": 200},
    ]
}, "invoice.pdf")
```

---

## PowerShell Integration

Call the Python scripts from PowerShell to stay consistent with the other guides:

```powershell
$python = "python"

# Set proxy (a corporate network)
$env:NO_PROXY = ".openai.azure.com,10.*,example.com,.example.com,10.0.0.0/8,192.168.0.0/16,localhost,.local,127.0.0.0/8,172.16.0.0/12,134.134.0.0/16,.search.windows.net"
$env:HTTP_PROXY = "http://proxy.example.com:8080"
$env:HTTPS_PROXY = "http://proxy.example.com:8080"

# Extract text from a PDF
& $python -c "
import fitz
doc = fitz.open(r'C:\path\to\file.pdf')
for page in doc:
    print(page.get_text())
doc.close()
"

# Convert PDF to markdown with AI image analysis
& $python "C:\path\to\pdf_to_markdown.py" "input.pdf" "output.md"

# Quick image extraction
& $python -c "
import fitz
doc = fitz.open(r'C:\path\to\file.pdf')
for i, page in enumerate(doc):
    for j, img in enumerate(page.get_images(full=True)):
        xref = img[0]
        data = doc.extract_image(xref)
        with open(f'page{i+1}_img{j+1}.{data[\"ext\"]}', 'wb') as f:
            f.write(data['image'])
        print(f'Saved page{i+1}_img{j+1}.{data[\"ext\"]}')
doc.close()
"
```

---

## Library Reference

### PyMuPDF (fitz) — Key Methods

| Method                        | Description                              |
|-------------------------------|------------------------------------------|
| `fitz.open(path)`             | Open a PDF                               |
| `doc.page_count`              | Number of pages                          |
| `doc.metadata`                | Dict of title, author, etc.              |
| `doc.get_toc()`               | Table of contents (bookmarks)            |
| `doc[n]`                      | Get page n (0-indexed)                   |
| `page.get_text(opt)`          | Extract text ("text", "html", "dict", "json", "words") |
| `page.get_images(full=True)`  | List embedded images                     |
| `doc.extract_image(xref)`     | Get image bytes by xref                  |
| `page.find_tables()`          | Detect and extract tables                |
| `page.get_links()`            | Get hyperlinks                           |
| `page.search_for(text)`       | Search text, returns Rects               |
| `page.get_pixmap(matrix)`     | Render page as image                     |
| `page.insert_text(point, text)` | Add text to page                       |
| `page.add_highlight_annot(rect)` | Add highlight annotation              |
| `page.add_redact_annot(rect)` | Add redaction                            |
| `page.apply_redactions()`     | Apply all redactions                     |
| `doc.insert_pdf(other)`       | Merge another PDF                        |
| `doc.save(path)`              | Save the document                        |

### fpdf2 — Key Methods

| Method                          | Description                            |
|---------------------------------|----------------------------------------|
| `FPDF()`                       | Create new PDF                          |
| `pdf.add_page()`               | Add a page                              |
| `pdf.set_font(family, style, size)` | Set font                           |
| `pdf.cell(w, h, text, ...)`    | Write a cell                            |
| `pdf.multi_cell(w, text)`      | Write wrapping text                     |
| `pdf.write(text=...)`          | Write inline text                       |
| `pdf.image(path, x, y, w, h)`  | Add image                               |
| `pdf.set_text_color(r, g, b)`  | Text color                              |
| `pdf.set_fill_color(r, g, b)`  | Fill color                              |
| `pdf.line(x1, y1, x2, y2)`    | Draw a line                             |
| `pdf.rect(x, y, w, h)`        | Draw rectangle                          |
| `pdf.ln(h)`                    | Line break                              |
| `pdf.add_link(page=n)`         | Create internal link target             |
| `pdf.output(path)`             | Save PDF                                |

### ReportLab — Key Components

| Component                       | Description                            |
|---------------------------------|----------------------------------------|
| `canvas.Canvas(path)`          | Low-level PDF canvas                    |
| `SimpleDocTemplate(path)`      | High-level flowing document             |
| `Paragraph(text, style)`       | Formatted paragraph                     |
| `Table(data)`                  | Table with data                         |
| `TableStyle(cmds)`             | Table styling commands                  |
| `Image(path, w, h)`           | Image element                           |
| `Spacer(w, h)`                | Vertical space                          |
| `getSampleStyleSheet()`       | Built-in paragraph styles               |

---

## PDF Read/Write Operations (PyMuPDF)

> **For AI Assistant**: Use this guide when the user needs to read, create, modify, or extract content from PDF files. The library is `PyMuPDF`, imported as `fitz`.

---

## Setup
```python
import fitz  # PyMuPDF
```

## Read PDF Text
```python
doc = fitz.open("document.pdf")
print(f"Pages: {doc.page_count}")
print(f"Author: {doc.metadata.get('author', 'N/A')}")

for page in doc:
    text = page.get_text()
    print(f"--- Page {page.number + 1} ---")
    print(text)

doc.close()
```

## Read Specific Pages
```python
doc = fitz.open("document.pdf")
page = doc[0]  # First page (0-indexed)
text = page.get_text()
doc.close()
```

## Extract Text as Structured Blocks
```python
doc = fitz.open("document.pdf")
for page in doc:
    blocks = page.get_text("blocks")  # Returns list of (x0, y0, x1, y1, text, block_no, block_type)
    for b in blocks:
        print(b[4])  # text content
doc.close()
```

## Search for Text in PDF
```python
doc = fitz.open("document.pdf")
for page in doc:
    results = page.search_for("keyword")
    for rect in results:
        print(f"Found on page {page.number + 1} at {rect}")
doc.close()
```

## Extract Images from PDF
```python
doc = fitz.open("document.pdf")
for page_num, page in enumerate(doc):
    images = page.get_images(full=True)
    for img_index, img in enumerate(images):
        xref = img[0]
        base_image = doc.extract_image(xref)
        image_bytes = base_image["image"]
        ext = base_image["ext"]
        with open(f"image_p{page_num}_{img_index}.{ext}", "wb") as f:
            f.write(image_bytes)
doc.close()
```

## Create a New PDF
```python
doc = fitz.open()  # New empty PDF
page = doc.new_page(width=595, height=842)  # A4 size in points
text_point = fitz.Point(72, 72)  # 1 inch from top-left
page.insert_text(text_point, "Hello, World!", fontsize=14)
doc.save("output.pdf")
doc.close()
```

## Add Text to Existing PDF (Annotate)
```python
doc = fitz.open("existing.pdf")
page = doc[0]
text_point = fitz.Point(72, 750)
page.insert_text(text_point, "Added annotation", fontsize=10, color=(1, 0, 0))  # Red text
doc.save("annotated.pdf")
doc.close()
```

## Merge PDFs
```python
doc_out = fitz.open()  # New empty
for pdf_path in ["file1.pdf", "file2.pdf", "file3.pdf"]:
    doc_in = fitz.open(pdf_path)
    doc_out.insert_pdf(doc_in)
    doc_in.close()
doc_out.save("merged.pdf")
doc_out.close()
```

## Split PDF (Extract Pages)
```python
doc = fitz.open("large.pdf")
doc_out = fitz.open()
doc_out.insert_pdf(doc, from_page=2, to_page=5)  # Pages 3-6 (0-indexed)
doc_out.save("pages_3_to_6.pdf")
doc.close()
doc_out.close()
```

## Get PDF Metadata
```python
doc = fitz.open("document.pdf")
meta = doc.metadata
# Keys: format, title, author, subject, keywords, creator, producer, creationDate, modDate
for key, value in meta.items():
    if value:
        print(f"{key}: {value}")
doc.close()
```

## Set PDF Metadata
```python
doc = fitz.open("document.pdf")
doc.set_metadata({
    "title": "My Document",
    "author": "Author Name",
    "subject": "Subject",
})
doc.save("updated.pdf")
doc.close()
```

## Convert PDF Page to Image
```python
doc = fitz.open("document.pdf")
page = doc[0]
pix = page.get_pixmap(dpi=150)
pix.save("page1.png")
doc.close()
```

---

## Common Workflows for AI Assistant

### Read email attachment PDF and summarize
```python
import fitz

doc = fitz.open(r"C:\path\to\attachment.pdf")
full_text = ""
for page in doc:
    full_text += page.get_text()
doc.close()
print(full_text)
# Then summarize the text
```

### Save PDF text to a file for reference
```python
import fitz

doc = fitz.open(r"C:\path\to\document.pdf")
with open("extracted_text.txt", "w", encoding="utf-8") as f:
    for page in doc:
        f.write(f"--- Page {page.number + 1} ---\n")
        f.write(page.get_text())
        f.write("\n")
doc.close()
```

---

## Notes
- PyMuPDF is imported as `fitz` (historical name from MuPDF library)
- Page numbers are 0-indexed in the API
- Default page size is A4 (595 x 842 points)
- 1 point = 1/72 inch
- Supports PDF, XPS, EPUB, MOBI, FB2, CBZ, SVG, and image formats

---

## Hebrew / RTL PDF Generation (fpdf2)

> **For AI Assistant**: Use this section whenever generating PDFs containing Hebrew text.
> fpdf2 does NOT have native RTL/bidi support. You MUST manually reshape text to visual order before passing it to `cell()` or `multi_cell()`.

### Critical Rules

1. **Always use a Hebrew-capable TTF font**  David (`C:\Windows\Fonts\david.ttf`, `davidbd.ttf`) or Arial work well.
2. **Do NOT pass `uni=True`** to `add_font()`  it's deprecated in fpdf2 and causes warnings.
3. **All text must be reshaped to visual order** before rendering. Hebrew text in logical order will appear reversed and broken.
4. **Parentheses are the #1 pain point**  naive RTL reversal puts `(` and `)` in wrong positions. Treat parenthesized groups as atomic units.
5. **Use `align="R"`** for all Hebrew cells and multi_cells.

### The Bidi Problem Explained

PDF renderers (fpdf2, reportlab) lay out characters left-to-right. Hebrew logical order is right-to-left. A naive character reversal breaks:
- **Parenthesized English inside Hebrew**: `הגנת סייבר (OT)` becomes `(OT)` with parens detached  `הגנת סייבר ()OT`
- **Mixed Hebrew + English**: `כולל Safety vs Security`  English words get reversed letter-by-letter

### Correct Approach: Tokenizer-Based Bidi Reshaping

```python
def is_hebrew(ch):
    return '\u0590' <= ch <= '\u05FF' or '\uFB1D' <= ch <= '\uFB4F'


def reshape_rtl_line(text):
    """Convert logical-order bidi text to visual order for LTR PDF rendering.

    Algorithm:
    1. Tokenize into: Hebrew runs, Latin/digit runs, paren groups (atomic), neutrals.
    2. Resolve neutral directions based on surrounding strong types (default: RTL).
    3. Group consecutive same-direction tokens into runs.
    4. Reverse run order (RTL base direction).
    5. Reverse characters within RTL runs; keep LTR runs as-is.
    6. Recursively reshape paren-group contents.
    """
    if not text or not any(is_hebrew(c) for c in text):
        return text

    tokens = []
    i, n = 0, len(text)
    while i < n:
        ch = text[i]
        # Parenthesized group  treat as atomic unit
        if ch in ('(', '[', '{'):
            close_ch = {'(': ')', '[': ']', '{': '}'}[ch]
            depth, j = 1, i + 1
            while j < n and depth > 0:
                if text[j] == ch:
                    depth += 1
                elif text[j] == close_ch:
                    depth -= 1
                j += 1
            tokens.append({'type': 'paren', 'text': text[i:j]})
            i = j
        elif is_hebrew(ch):
            j = i
            while j < n and is_hebrew(text[j]):
                j += 1
            tokens.append({'type': 'rtl', 'text': text[i:j]})
            i = j
        elif ch.isalpha() or ch.isdigit():
            j = i
            while j < n and (text[j].isalpha() or text[j].isdigit()) and not is_hebrew(text[j]):
                j += 1
            tokens.append({'type': 'ltr', 'text': text[i:j]})
            i = j
        else:
            tokens.append({'type': 'neutral', 'text': ch})
            i += 1

    # Resolve neutrals
    for idx in range(len(tokens)):
        if tokens[idx]['type'] != 'neutral':
            continue
        prev_dir = next_dir = None
        for p in range(idx - 1, -1, -1):
            if tokens[p]['type'] in ('rtl', 'ltr'):
                prev_dir = tokens[p]['type']
                break
        for q in range(idx + 1, len(tokens)):
            if tokens[q]['type'] in ('rtl', 'ltr'):
                next_dir = tokens[q]['type']
                break
        if prev_dir == next_dir and prev_dir is not None:
            tokens[idx]['type'] = prev_dir
        else:
            tokens[idx]['type'] = 'rtl'  # base direction fallback

    # Group consecutive same-direction tokens
    runs = []
    for tok in tokens:
        if runs and runs[-1]['type'] == tok['type']:
            runs[-1]['text'] += tok['text']
        else:
            runs.append({'type': tok['type'], 'text': tok['text']})

    # Reverse run order (RTL base)
    runs.reverse()

    # Build visual output
    parts = []
    for run in runs:
        if run['type'] == 'rtl':
            parts.append(run['text'][::-1])
        elif run['type'] == 'ltr':
            parts.append(run['text'])
        elif run['type'] == 'paren':
            inner = run['text'][1:-1]
            open_ch = run['text'][0]
            close_ch = run['text'][-1] if len(run['text']) > 1 else ''
            reshaped_inner = reshape_rtl_line(inner) if inner and any(is_hebrew(c) for c in inner) else inner
            parts.append(open_ch + reshaped_inner + close_ch)
        else:
            parts.append(run['text'])

    return ''.join(parts)


def rtl(text):
    """Shorthand for reshaping a line."""
    return reshape_rtl_line(text)
```

### Font Setup (fpdf2)

```python
from fpdf import FPDF

pdf = FPDF()
# Do NOT use uni=True  deprecated in fpdf2
pdf.add_font("David", "", r"C:\Windows\Fonts\david.ttf")
pdf.add_font("David", "B", r"C:\Windows\Fonts\davidbd.ttf")
# Arial also works for Hebrew
pdf.add_font("Arial", "", r"C:\Windows\Fonts\arial.ttf")
pdf.add_font("Arial", "B", r"C:\Windows\Fonts\arialbd.ttf")
```

### Rendering Hebrew Text

```python
pdf.add_page()
pdf.set_font("David", "B", 16)
pdf.set_text_color(0, 0, 0)
# ALWAYS reshape before rendering, ALWAYS align="R"
pdf.cell(0, 10, rtl("הגנת סייבר על מערכות תפעוליות (OT)"), align="R",
         new_x="LMARGIN", new_y="NEXT")

# Multi-line Hebrew text
text = "שורה ראשונה\nשורה שנייה\nשורה שלישית"
for line in text.split('\n'):
    if line.strip():
        pdf.cell(0, 7, rtl(line.strip()), align="R", new_x="LMARGIN", new_y="NEXT")
```

### Hebrew Tables

```python
# Column order is visual (left-to-right in PDF), but content is RTL.
# Put the rightmost Hebrew column LAST in the col_widths array.
col_widths = [25, 25, 140]  # type | hours | topic (topic is rightmost = widest)
headers = [rtl("סוג"), rtl("שעות"), rtl("נושא")]

pdf.set_font("David", "B", 10)
pdf.set_fill_color(0, 90, 156)
pdf.set_text_color(255, 255, 255)
for i, hdr in enumerate(headers):
    pdf.cell(col_widths[i], 7, hdr, border=1, align="C", fill=True,
             new_x="RIGHT", new_y="TOP")
pdf.ln()
```

### Known Gotchas

| Issue | Solution |
|-------|----------|
| Parentheses appear detached: `()OT` | Use tokenizer-based reshaper (above) that treats paren groups as atomic |
| English words inside Hebrew appear letter-reversed | Tokenizer keeps LTR runs intact, only reverses run order |
| `uni=True` warning in fpdf2 | Remove the parameter entirely  fpdf2 handles Unicode automatically with TTF |
| David font missing glyph for `` (U+25CB) | Use `` (U+2022) or `-` as bullet characters instead |
| Numbers appear reversed | Tokenizer treats digits as LTR  they stay in correct order |
| Colon/comma between Hebrew words misplaced | Neutral-resolution step assigns direction based on surrounding strong types |
| `python-bidi` library unavailable (pip timeout) | Use the built-in tokenizer above  no external dependency needed |

### Recommended PDF Class Structure for Hebrew Documents

```python
class HebrewPDF(FPDF):
    def __init__(self, title_text=""):
        super().__init__()
        self.title_text = title_text
        self.set_auto_page_break(auto=True, margin=20)
        self.add_font("David", "", r"C:\Windows\Fonts\david.ttf")
        self.add_font("David", "B", r"C:\Windows\Fonts\davidbd.ttf")

    def header(self):
        if self.page_no() > 1:
            self.set_font("David", "B", 9)
            self.set_text_color(120, 120, 120)
            self.cell(0, 8, rtl(self.title_text), align="R")
            self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("David", "", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"{self.page_no()}/{{nb}}", align="C")

    def section_header(self, text):
        """Blue bar with white RTL text."""
        self.set_fill_color(0, 90, 156)
        self.rect(10, self.get_y(), self.w - 20, 10, style="F")
        self.set_font("David", "B", 16)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, rtl(text), align="R", new_x="LMARGIN", new_y="NEXT")
        self.ln(4)

    def bullet_list(self, items):
        """RTL bullet list using  character."""
        self.set_font("David", "", 11)
        self.set_text_color(30, 30, 30)
        for item in items:
            self.cell(0, 7, rtl(f"\u2022  {item}"), align="R",
                      new_x="LMARGIN", new_y="NEXT")
        self.ln(2)
```

### Python Environment Notes

- Use Python 3.12: `%USERPROFILE%\AppData\Local\Programs\Python\Python312\python.exe`
- fpdf2 is installed there. pip may have network issues  avoid relying on runtime installs.
- Run scripts with: `& "%USERPROFILE%\AppData\Local\Programs\Python\Python312\python.exe" "script.py"`
