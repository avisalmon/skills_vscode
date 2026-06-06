#!/usr/bin/env python3
"""
generate-skills-data.py
Reads all public skill SKILL.md files and generates skills-data.js
"""
import re
import json
from pathlib import Path

BASE = Path(r'c:\Users\asalmon\.copilot\skills')
OUT  = Path(r'c:\Projects\skills_vscode\skills-data.js')

CATALOG = [
    dict(id='docker-basics',              name='Docker Basics',                    icon='🐳', category='DevOps',        tags=['docker','containers','dockerfile','devops','deployment'],             version='1.0.0'),
    dict(id='pandas-data-analysis',       name='Pandas Data Analysis',             icon='📊', category='Data Science',  tags=['pandas','python','dataframe','csv','analysis','matplotlib'],           version='1.0.0'),
    dict(id='fastapi-development',        name='FastAPI Development',              icon='⚡', category='Backend',       tags=['fastapi','python','rest','api','pydantic','jwt'],                      version='1.0.0'),
    dict(id='github-actions-ci',          name='GitHub Actions CI/CD',             icon='🔄', category='DevOps',        tags=['github','ci-cd','actions','yaml','automation','testing'],               version='1.0.0'),
    dict(id='playwright-cli',             name='Playwright Browser Automation',    icon='🎭', category='Testing',       tags=['playwright','browser','automation','testing','e2e'],                   version='1.0.0'),
    dict(id='sqlite-power-queries',       name='SQLite Power Queries',             icon='🗄️', category='Backend',       tags=['sqlite','sql','database','window-functions','cte','python'],           version='1.0.0'),
    dict(id='langchain-rag',              name='LangChain RAG',                    icon='🦜', category='AI / ML',       tags=['langchain','rag','ai','llm','embeddings','vector-db'],                  version='1.0.0'),
    dict(id='ollama-local-llms',          name='Ollama Local LLMs',               icon='🦙', category='AI / ML',       tags=['ollama','llm','local-ai','llama','gemma','offline'],                   version='1.0.0'),
    dict(id='render-django',              name='Django on Render',                 icon='🚀', category='Backend',       tags=['django','render','deployment','python','web','cloud'],                  version='1.0.0'),
    dict(id='excel-powershell',           name='Excel Automation',                 icon='📗', category='Productivity',  tags=['excel','powershell','automation','office','com','windows'],             version='1.0.0'),
    dict(id='powerpoint-powershell',      name='PowerPoint Automation',            icon='📙', category='Productivity',  tags=['powerpoint','powershell','automation','office','presentation'],         version='1.0.0'),
    dict(id='word-powershell',            name='Word Automation',                  icon='📘', category='Productivity',  tags=['word','powershell','automation','office','documents'],                  version='1.0.0'),
    dict(id='outlook-powershell',         name='Outlook Automation',               icon='📧', category='Productivity',  tags=['outlook','email','powershell','automation','office'],                   version='1.0.0'),
    dict(id='ffmpeg-automation',          name='FFmpeg Video Automation',          icon='🎬', category='Media',         tags=['ffmpeg','video','audio','conversion','compression','media'],             version='1.0.0'),
    dict(id='youtube-media-downloader',   name='YouTube Downloader',               icon='📺', category='Media',         tags=['youtube','yt-dlp','mp3','mp4','download','spotify'],                   version='1.0.0'),
    dict(id='pdf-python-ai',              name='PDF Automation (Python)',           icon='📄', category='Productivity',  tags=['pdf','pymupdf','python','automation','extract','merge'],                version='1.0.0'),
    dict(id='whatsapp-api-messaging',     name='WhatsApp API Messaging',           icon='💬', category='Productivity',  tags=['whatsapp','messaging','api','nodejs','automation'],                     version='1.0.0'),
    dict(id='automation-dedup-guard',     name='Automation Dedup Guard',           icon='🛡️', category='AI / ML',       tags=['automation','dedup','ai-agents','idempotency','safety'],               version='1.0.0'),
    dict(id='de10lite-board-and-build',   name='DE10-Lite FPGA Development',       icon='🔌', category='Hardware',      tags=['fpga','de10-lite','quartus','verilog','hardware','games'],               version='1.0.0'),
    dict(id='de10lite-vga-graphics',      name='DE10-Lite VGA Graphics',           icon='🖥️', category='Hardware',      tags=['fpga','vga','graphics','de10-lite','sprites','hardware'],               version='1.0.0'),
    dict(id='de10lite-addon-peripherals', name='DE10-Lite Addon Peripherals',      icon='🕹️', category='Hardware',      tags=['fpga','joystick','lcd','de10-lite','peripherals'],                     version='1.0.0'),
    dict(id='esp32-firmware',             name='ESP32 Firmware',                   icon='📡', category='Hardware',      tags=['esp32','firmware','iot','arduino','micropython','wifi'],                version='1.0.0'),
    dict(id='kicad-board-design',         name='KiCad Board Design',               icon='🔲', category='Hardware',      tags=['kicad','pcb','schematic','electronics','eda'],                          version='1.0.0'),
    dict(id='skill-creator',              name='Skill Creator',                    icon='🧠', category='Meta',          tags=['skill','copilot','vscode','create','prompt-engineering'],               version='1.0.0'),
    dict(id='managed-project-setup',      name='Managed Project Setup',            icon='📋', category='Meta',          tags=['project','spec','backlog','planning','scaffolding'],                   version='1.0.0'),
    dict(id='autoagent-project-setup',    name='AutoAgent Project Setup',          icon='🤖', category='AI / ML',       tags=['autoagent','project','setup','ai','copilot'],                          version='1.0.0'),
    dict(id='writing-skills',             name='Writing and Research',             icon='✍️', category='Meta',          tags=['writing','research','documentation','markdown'],                        version='1.0.0'),
    dict(id='vscode-tips',                name='VS Code Tips',                     icon='💡', category='Meta',          tags=['vscode','tips','editor','markdown','productivity'],                     version='1.0.0'),
]

def get_description(content: str) -> str:
    """Extract description from YAML frontmatter."""
    # Try multiline description: > style
    m = re.search(r'(?s)description:\s*>\s*\n(.*?)(?:\n\w|\n---)', content)
    if m:
        lines = [l.strip() for l in m.group(1).splitlines() if l.strip()]
        return ' '.join(lines)
    # Try inline description: "value"
    m = re.search(r'description:\s*["\']?(.+)', content)
    if m:
        return m.group(1).strip().strip('"\'')
    return ''

def build_js():
    parts = []
    parts.append(
        '/* =============================================================================\n'
        '   VS Code Skills Store — Skill Catalog\n'
        '   Auto-generated by generate-skills-data.py\n'
        '   Add new skills here. Each entry is displayed as a card in the store.\n'
        '============================================================================= */\n'
        '\n'
        'window.SKILLS_DATA = [\n'
    )

    entries = []
    for meta in CATALOG:
        skill_path = BASE / meta['id'] / 'SKILL.md'
        if not skill_path.exists():
            print(f'  SKIPPING (not found): {meta["id"]}')
            continue

        raw = skill_path.read_text(encoding='utf-8', errors='replace')
        desc = get_description(raw)

        # Escape content for JS template literal: escape backticks and ${
        content_escaped = raw.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')

        tags_js = ', '.join(f"'{t}'" for t in meta['tags'])
        name_esc = meta['name'].replace("'", "\\'")
        desc_esc = desc.replace("'", "\\'").replace('\n', ' ')

        entry = (
            f"\n  // ── {meta['name']} ──\n"
            f"  {{\n"
            f"    id:          '{meta['id']}',\n"
            f"    name:        '{name_esc}',\n"
            f"    description: '{desc_esc}',\n"
            f"    category:    '{meta['category']}',\n"
            f"    tags:        [{tags_js}],\n"
            f"    icon:        '{meta['icon']}',\n"
            f"    author:      'Skills Store',\n"
            f"    version:     '{meta['version']}',\n"
            f"    content: `{content_escaped}`\n"
            f"  }}"
        )
        entries.append(entry)
        print(f'  OK: {meta["id"]} ({len(raw.splitlines())} lines)')

    parts.append(',\n'.join(entries))
    parts.append('\n\n];\n')
    return ''.join(parts)

if __name__ == '__main__':
    print('Generating skills-data.js ...')
    js = build_js()
    OUT.write_text(js, encoding='utf-8')
    size_kb = OUT.stat().st_size // 1024
    print(f'\nGenerated: {OUT}')
    print(f'Size: {size_kb} KB')
    print(f'Skills: {js.count("id:")} entries')
