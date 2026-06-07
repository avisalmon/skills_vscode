#!/usr/bin/env python3
"""Generate the public skills catalog for the VS Code Skills Store.

All public skills are loaded from this repository's skills/ folder so the
GitHub Pages site is self-contained.

Only skills that have been reviewed as public-safe should be listed in CATALOG.
"""
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
LOCAL_SKILLS = REPO_ROOT / 'skills'
OUT = REPO_ROOT / 'skills-data.js'

CATALOG = [
    dict(id='pandas-data-analysis', name='Pandas Data Analysis', icon='📊', category='Data Science', tags=['pandas','python','dataframe','csv','analysis','matplotlib'], version='1.0.0'),
    dict(id='fastapi-development', name='FastAPI Development', icon='⚡', category='Backend', tags=['fastapi','python','rest','api','pydantic','jwt'], version='1.0.0'),
    dict(id='github-actions-ci', name='GitHub Actions CI/CD', icon='🔄', category='DevOps', tags=['github','ci-cd','actions','yaml','automation','testing'], version='1.0.0'),
    dict(id='cad-solidworks-automation', name='CAD SolidWorks Automation', icon='🧰', category='CAD / Mechanical', tags=['solidworks','cad','mechanical','vba','automation','drawings','assemblies'], version='1.0.0'),
    dict(id='robotics-ros2', name='Robotics with ROS 2', icon='🤖', category='Robotics', tags=['ros2','robotics','python','simulation','sensors','control','rviz','gazebo'], version='1.0.0'),
    dict(id='stock-market-analysis', name='Stock Market Analysis with Python', icon='📈', category='Finance / Data', tags=['stocks','yfinance','pandas','finance','backtesting','portfolio','risk'], version='1.0.0'),
    dict(id='open-meteo-weather-api', name='Open-Meteo Weather API', icon='🌦️', category='Free API', tags=['api','weather','open-meteo','json','python','javascript','teaching'], version='1.0.0'),
    dict(id='israel-home-front-alerts-api', name='Israel Home Front Alerts Data', icon='🚨', category='Free API', tags=['api','israel','emergency','alerts','json','teaching','safety'], version='1.0.0'),
    dict(id='israel-transport-gtfs-api', name='Israel Public Transport GTFS API', icon='🚆', category='Free API', tags=['api','israel','transport','gtfs','trains','buses','realtime','data'], version='1.0.0'),
    dict(id='nasa-open-apis', name='NASA Open APIs', icon='🛰️', category='Free API', tags=['api','nasa','space','apod','json','python','teaching'], version='1.0.0'),
    dict(id='wikipedia-api-lesson', name='Wikipedia API', icon='📚', category='Free API', tags=['api','wikipedia','wikimedia','mediawiki','search','json','teaching'], version='1.0.0'),
    dict(id='openstreetmap-nominatim-api', name='OpenStreetMap Nominatim API', icon='🗺️', category='Free API', tags=['api','maps','openstreetmap','geocoding','location','json','teaching'], version='1.0.0'),
    dict(id='rest-countries-api', name='REST Countries API', icon='🌍', category='Free API', tags=['api','countries','geography','json','flags','teaching'], version='1.0.0'),
    dict(id='openai-api-setup', name='OpenAI API Setup and Cost Tracking', icon='🔑', category='API', tags=['api','openai','ai','dotenv','python','cost','tokens','security'], version='1.0.0'),
    dict(id='github-public-api', name='GitHub Public API', icon='🐙', category='Free API', tags=['api','github','repositories','issues','commits','json','teaching'], version='1.0.0'),
    dict(id='pokeapi', name='PokéAPI', icon='🎮', category='Free API', tags=['api','pokemon','json','images','beginner','teaching'], version='1.0.0'),
    dict(id='open-library-api', name='Open Library API', icon='📖', category='Free API', tags=['api','books','library','isbn','search','json','teaching'], version='1.0.0'),
    dict(id='fake-crud-apis', name='Fake CRUD APIs', icon='🧪', category='Free API', tags=['api','crud','jsonplaceholder','dummyjson','rest','forms','teaching'], version='1.0.0'),
    dict(id='jokes-trivia-apis', name='Jokes and Trivia APIs', icon='❓', category='Free API', tags=['api','jokes','trivia','quiz','beginner','json','teaching'], version='1.0.0'),
    dict(id='rss-news-feeds', name='RSS News Feeds', icon='📰', category='Free API', tags=['api','rss','atom','news','xml','feeds','teaching'], version='1.0.0'),
    dict(id='exchange-rates-api', name='Exchange Rates API', icon='💱', category='Free API', tags=['api','currency','exchange-rates','finance','json','teaching'], version='1.0.0'),
    dict(id='public-holidays-api', name='Public Holidays API', icon='📅', category='Free API', tags=['api','holidays','calendar','dates','countries','json','teaching'], version='1.0.0'),
    dict(id='usgs-earthquake-api', name='USGS Earthquake API', icon='🌋', category='Free API', tags=['api','earthquake','usgs','geojson','maps','science','teaching'], version='1.0.0'),
    dict(id='open-meteo-air-quality-api', name='Open-Meteo Air Quality API', icon='🌫️', category='Free API', tags=['api','air-quality','open-meteo','environment','aqi','json','teaching'], version='1.0.0'),
    dict(id='skill-creator', name='Skill Creator', icon='🧭', category='Productivity', tags=['skills','copilot','prompts','evaluation','workflow','authoring'], version='1.0.0'),
    dict(id='playwright-cli', name='Playwright CLI', icon='🎭', category='Frontend', tags=['playwright','browser','testing','automation','e2e','web'], version='1.0.0'),
    dict(id='esp32-firmware', name='ESP32 Firmware', icon='📟', category='Hardware', tags=['esp32','platformio','arduino','firmware','lvgl','microcontroller'], version='1.0.0'),
    dict(id='kicad-board-design', name='KiCad Board Design', icon='🔌', category='Hardware', tags=['kicad','pcb','schematic','drc','erc','gerber'], version='1.0.0'),
    dict(id='vscode-tips', name='VS Code Tips', icon='💡', category='Productivity', tags=['vscode','markdown','editor','tips'], version='1.0.0'),
    dict(id='file-sync', name='File Sync', icon='🔁', category='DevOps', tags=['sync','files','windows','linux','scp','automation'], version='1.0.0'),
    dict(id='sqlite-power-queries', name='SQLite Power Queries', icon='🗃️', category='Data Science', tags=['sqlite','sql','cte','json','fts5','python'], version='1.0.0'),
    dict(id='render-django', name='Render Django Deployment', icon='🚀', category='Backend', tags=['django','render','deployment','sqlite','whitenoise','oauth'], version='1.0.0'),
    dict(id='managed-project-setup', name='Managed Project Setup', icon='📋', category='Productivity', tags=['project','spec','backlog','requirements','planning','traceability'], version='1.0.0'),
    dict(id='automation-dedup-guard', name='Automation Dedup Guard', icon='🛡️', category='Productivity', tags=['automation','dedup','safety','idempotency','guardrails'], version='1.0.0'),
    dict(id='docker-basics', name='Docker Basics', icon='🐳', category='DevOps', tags=['docker','container','dockerfile','compose','images','volumes'], version='1.0.0'),
    dict(id='ffmpeg-automation', name='FFmpeg Automation', icon='🎬', category='Productivity', tags=['ffmpeg','video','audio','conversion','compression','batch'], version='1.0.0'),
    dict(id='langchain-rag', name='LangChain RAG', icon='🔎', category='AI / ML', tags=['rag','langchain','embeddings','vector','documents','llm'], version='1.0.0'),
    dict(id='ollama-local-llms', name='Ollama Local LLMs', icon='🧠', category='AI / ML', tags=['ollama','local-llm','offline','models','python','api'], version='1.0.0'),
    dict(id='pdf-python-ai', name='PDF Python Automation', icon='📄', category='Python', tags=['pdf','pymupdf','python','automation','extraction','reportlab'], version='1.0.0'),
    dict(id='excel-powershell', name='Excel PowerShell', icon='📗', category='Productivity', tags=['excel','powershell','com','automation','spreadsheets'], version='1.0.0'),
    dict(id='powerpoint-powershell', name='PowerPoint PowerShell', icon='📙', category='Productivity', tags=['powerpoint','powershell','com','automation','slides'], version='1.0.0'),
    dict(id='word-powershell', name='Word PowerShell', icon='📘', category='Productivity', tags=['word','powershell','com','automation','documents'], version='1.0.0'),
    dict(id='m365-graph-mcp', name='Microsoft 365 Graph MCP', icon='☁️', category='Productivity', tags=['microsoft-365','graph','mcp','teams','sharepoint','onedrive'], version='1.0.0'),
    dict(id='whatsapp-api-messaging', name='WhatsApp API Messaging', icon='💬', category='API', tags=['whatsapp','api','node','messaging','automation','javascript'], version='1.0.0'),
    dict(id='agentic-github-flow', name='Agentic GitHub Flow', icon='🤖', category='DevOps', tags=['github','actions','issues','agents','ci','automation'], version='1.0.0'),
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
        skill_path = LOCAL_SKILLS / meta['id'] / 'SKILL.md'
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
    print(f'Skills: {len(CATALOG)} entries')
