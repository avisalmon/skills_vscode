# generate-skills-data.ps1
# Reads all public skill SKILL.md files and generates skills-data.js

$base = 'c:\Users\asalmon\.copilot\skills'

# ── Skill catalog metadata ────────────────────────────────────────────────────
$catalog = @(
  @{ id='docker-basics';           name='Docker Basics';              icon='🐳'; category='DevOps';        tags=@('docker','containers','dockerfile','devops','deployment'); author='Skills Store'; version='1.0.0' },
  @{ id='pandas-data-analysis';    name='Pandas Data Analysis';       icon='📊'; category='Data Science';  tags=@('pandas','python','dataframe','csv','analysis','matplotlib'); author='Skills Store'; version='1.0.0' },
  @{ id='fastapi-development';     name='FastAPI Development';        icon='⚡'; category='Backend';       tags=@('fastapi','python','rest','api','pydantic','jwt'); author='Skills Store'; version='1.0.0' },
  @{ id='github-actions-ci';       name='GitHub Actions CI/CD';       icon='🔄'; category='DevOps';        tags=@('github','ci-cd','actions','yaml','automation','testing'); author='Skills Store'; version='1.0.0' },
  @{ id='playwright-cli';          name='Playwright Browser Automation'; icon='🎭'; category='Testing';   tags=@('playwright','browser','automation','testing','e2e'); author='Skills Store'; version='1.0.0' },
  @{ id='sqlite-power-queries';    name='SQLite Power Queries';       icon='🗄️'; category='Backend';       tags=@('sqlite','sql','database','window-functions','cte','python'); author='Skills Store'; version='1.0.0' },
  @{ id='langchain-rag';           name='LangChain RAG';              icon='🦜'; category='AI / ML';       tags=@('langchain','rag','ai','llm','embeddings','vector-db'); author='Skills Store'; version='1.0.0' },
  @{ id='ollama-local-llms';       name='Ollama Local LLMs';          icon='🦙'; category='AI / ML';       tags=@('ollama','llm','local-ai','llama','gemma','offline'); author='Skills Store'; version='1.0.0' },
  @{ id='render-django';           name='Django on Render';           icon='🚀'; category='Backend';       tags=@('django','render','deployment','python','web','cloud'); author='Skills Store'; version='1.0.0' },
  @{ id='excel-powershell';        name='Excel Automation (PowerShell)'; icon='📗'; category='Productivity'; tags=@('excel','powershell','automation','office','com','windows'); author='Skills Store'; version='1.0.0' },
  @{ id='powerpoint-powershell';   name='PowerPoint Automation';      icon='📙'; category='Productivity'; tags=@('powerpoint','powershell','automation','office','presentation'); author='Skills Store'; version='1.0.0' },
  @{ id='word-powershell';         name='Word Automation (PowerShell)'; icon='📘'; category='Productivity'; tags=@('word','powershell','automation','office','documents'); author='Skills Store'; version='1.0.0' },
  @{ id='outlook-powershell';      name='Outlook Automation';         icon='📧'; category='Productivity'; tags=@('outlook','email','powershell','automation','office'); author='Skills Store'; version='1.0.0' },
  @{ id='ffmpeg-automation';       name='FFmpeg Video Automation';    icon='🎬'; category='Media';         tags=@('ffmpeg','video','audio','conversion','compression','media'); author='Skills Store'; version='1.0.0' },
  @{ id='youtube-media-downloader';name='YouTube Downloader';         icon='📺'; category='Media';         tags=@('youtube','yt-dlp','mp3','mp4','download','spotify'); author='Skills Store'; version='1.0.0' },
  @{ id='pdf-python-ai';           name='PDF Automation (Python)';    icon='📄'; category='Productivity'; tags=@('pdf','pymupdf','python','automation','extract','merge'); author='Skills Store'; version='1.0.0' },
  @{ id='whatsapp-api-messaging';  name='WhatsApp API Messaging';     icon='💬'; category='Productivity'; tags=@('whatsapp','messaging','api','nodejs','automation'); author='Skills Store'; version='1.0.0' },
  @{ id='automation-dedup-guard';  name='Automation Dedup Guard';     icon='🛡️'; category='AI / ML';       tags=@('automation','dedup','ai-agents','idempotency','safety'); author='Skills Store'; version='1.0.0' },
  @{ id='de10lite-board-and-build';name='DE10-Lite FPGA Development'; icon='🔌'; category='Hardware';      tags=@('fpga','de10-lite','quartus','verilog','hardware','games'); author='Skills Store'; version='1.0.0' },
  @{ id='de10lite-vga-graphics';   name='DE10-Lite VGA Graphics';     icon='🖥️'; category='Hardware';      tags=@('fpga','vga','graphics','de10-lite','sprites','hardware'); author='Skills Store'; version='1.0.0' },
  @{ id='de10lite-addon-peripherals'; name='DE10-Lite Addon Peripherals'; icon='🕹️'; category='Hardware'; tags=@('fpga','joystick','lcd','de10-lite','peripherals'); author='Skills Store'; version='1.0.0' },
  @{ id='esp32-firmware';          name='ESP32 Firmware';             icon='📡'; category='Hardware';      tags=@('esp32','firmware','iot','arduino','micropython','wifi'); author='Skills Store'; version='1.0.0' },
  @{ id='kicad-board-design';      name='KiCad Board Design';         icon='🔲'; category='Hardware';      tags=@('kicad','pcb','schematic','electronics','eda'); author='Skills Store'; version='1.0.0' },
  @{ id='skill-creator';           name='Skill Creator';              icon='🧠'; category='Meta';          tags=@('skill','copilot','vscode','create','prompt-engineering'); author='Skills Store'; version='1.0.0' },
  @{ id='managed-project-setup';   name='Managed Project Setup';      icon='📋'; category='Meta';          tags=@('project','spec','backlog','planning','scaffolding'); author='Skills Store'; version='1.0.0' },
  @{ id='autoagent-project-setup'; name='AutoAgent Project Setup';    icon='🤖'; category='AI / ML';       tags=@('autoagent','project','setup','ai','copilot'); author='Skills Store'; version='1.0.0' },
  @{ id='writing-skills';          name='Writing & Research';         icon='✍️'; category='Meta';          tags=@('writing','research','documentation','markdown'); author='Skills Store'; version='1.0.0' },
  @{ id='vscode-tips';             name='VS Code Tips';               icon='💡'; category='Meta';          tags=@('vscode','tips','editor','markdown','productivity'); author='Skills Store'; version='1.0.0' }
)

# ── Extract description from YAML frontmatter ─────────────────────────────────
function Get-SkillDescription($content) {
  if ($content -match '(?s)---.*?description:\s*>?\s*\n(.*?)(?:---|\nversion|\ntags|\ncategory|\nauthor|\nname:)') {
    $raw = $Matches[1]
    # Collapse multiline YAML value, strip leading whitespace from each line
    $lines = $raw -split '\n' | ForEach-Object { $_.TrimStart() } | Where-Object { $_ -ne '' }
    return ($lines -join ' ').Trim()
  }
  # Fallback: grab first non-blank non-# line after frontmatter
  $inFront = $false; $pastFront = $false
  foreach ($line in $content -split '\n') {
    if ($line.Trim() -eq '---') {
      if (-not $inFront) { $inFront = $true } else { $pastFront = $true }
      continue
    }
    if ($pastFront -and $line.Trim() -ne '' -and -not $line.StartsWith('#') -and -not $line.StartsWith('>')) {
      return $line.Trim()
    }
  }
  return ''
}

# ── JS string escape ──────────────────────────────────────────────────────────
function EscapeForJS($str) {
  $str = $str -replace '\\', '\\\\'
  $str = $str -replace '`', '\`'
  $str = $str -replace '\$\{', '\${'
  return $str
}

# ── Build output ──────────────────────────────────────────────────────────────
$output = @()
$output += @"
/* =============================================================================
   VS Code Skills Store — Skill Catalog
   Auto-generated by generate-skills-data.ps1
   Add new skills here. Each entry is displayed as a card in the store.
============================================================================= */

window.SKILLS_DATA = [
"@

$first = $true
foreach ($meta in $catalog) {
  $skillPath = "$base\$($meta.id)\SKILL.md"
  
  if (-not (Test-Path $skillPath)) {
    Write-Warning "Skipping $($meta.id) — SKILL.md not found at $skillPath"
    continue
  }
  
  $rawContent = Get-Content $skillPath -Raw -Encoding UTF8
  $description = Get-SkillDescription $rawContent
  $contentEscaped = EscapeForJS $rawContent
  
  $tagsJs = ($meta.tags | ForEach-Object { "'$_'" }) -join ', '
  
  if (-not $first) { $output += ',' }
  $first = $false
  
  $output += @"

  // ── $($meta.name) ──
  {
    id:          '$($meta.id)',
    name:        '$($meta.name -replace "'","\'") ',
    description: '$($description -replace "'","\'" -replace '\n',' ')',
    category:    '$($meta.category)',
    tags:        [$tagsJs],
    icon:        '$($meta.icon)',
    author:      '$($meta.author)',
    version:     '$($meta.version)',
    content: ``$contentEscaped``
  }
"@
}

$output += @"

];
"@

$outputPath = 'c:\Projects\skills_vscode\skills-data.js'
$output -join "`n" | Set-Content $outputPath -Encoding UTF8
Write-Host "Generated: $outputPath"
Write-Host "Size: $([Math]::Round((Get-Item $outputPath).Length / 1KB)) KB"
