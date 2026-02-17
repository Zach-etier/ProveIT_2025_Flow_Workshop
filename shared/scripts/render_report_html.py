#!/usr/bin/env python3
"""render_report_html.py — Convert a shift report markdown file to styled HTML.

Shift-report-aware renderer that produces rich HTML with card-based layout,
bar charts, progress bars, status badges, and navigation. Inspired by the
report.html UX patterns.

Zero external dependencies (stdlib only).

Usage:
    python3 render_report_html.py --input report.md --output report.html
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Markdown helpers
# ---------------------------------------------------------------------------

def _inline(text: str) -> str:
    """Convert inline markdown: **bold**, *italic*, `code`."""
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    return text


def _parse_md_table(lines: list[str]) -> list[dict]:
    """Parse a markdown table into a list of row dicts {header: value}.

    Returns list of dicts (one per body row), or empty list if not a valid table.
    """
    if len(lines) < 2:
        return []

    # First line is header
    header_cells = [c.strip() for c in lines[0].strip().strip('|').split('|')]

    # Second line should be separator
    sep = lines[1].strip().strip('|')
    sep_cells = [c.strip() for c in sep.split('|')]
    if not all(re.match(r'^:?-+:?$', c) for c in sep_cells):
        return []

    rows = []
    for line in lines[2:]:
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        row = {}
        for j, header in enumerate(header_cells):
            row[header] = cells[j] if j < len(cells) else ''
        rows.append(row)

    return rows


def _extract_pct(text: str) -> float | None:
    """Extract a percentage value from text like '87.9%' or '**14.5%**'."""
    cleaned = re.sub(r'\*+', '', text).strip()
    m = re.match(r'^([\d.]+)\s*%$', cleaned)
    return float(m.group(1)) if m else None


def _extract_number(text: str) -> float | None:
    """Extract a number from text like '12,457 bottles' or '52,000'."""
    cleaned = re.sub(r'\*+', '', text).strip()
    m = re.search(r'([\d,]+(?:\.\d+)?)', cleaned)
    if m:
        return float(m.group(1).replace(',', ''))
    return None


def _paragraphs_and_bullets(text: str) -> str:
    """Convert section text (paragraphs and bullet lists) to HTML."""
    lines = text.split('\n')
    html_parts = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        # Sub-headers (###)
        hm = re.match(r'^(#{3,6})\s+(.+)$', stripped)
        if hm:
            level = len(hm.group(1))
            html_parts.append(f'<h{level}>{_inline(hm.group(2))}</h{level}>')
            i += 1
            continue

        # Horizontal rule
        if re.match(r'^-{3,}$', stripped) or re.match(r'^\*{3,}$', stripped):
            i += 1
            continue

        # Table — render as standard HTML table
        if stripped.startswith('|'):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                table_lines.append(lines[i])
                i += 1
            rows = _parse_md_table(table_lines)
            if rows:
                html_parts.append(_render_html_table(rows))
            continue

        # Bullet list
        if re.match(r'^[-*]\s+', stripped):
            html_parts.append('<ul>')
            while i < len(lines) and re.match(r'^\s*[-*]\s+', lines[i]):
                item_text = re.sub(r'^\s*[-*]\s+', '', lines[i])
                html_parts.append(f'<li>{_inline(item_text.strip())}</li>')
                i += 1
            html_parts.append('</ul>')
            continue

        # Numbered list
        if re.match(r'^\d+\.\s+', stripped):
            html_parts.append('<ol>')
            while i < len(lines) and re.match(r'^\s*\d+\.\s+', lines[i]):
                item_text = re.sub(r'^\s*\d+\.\s+', '', lines[i])
                html_parts.append(f'<li>{_inline(item_text.strip())}</li>')
                i += 1
            html_parts.append('</ol>')
            continue

        # Blockquote
        if stripped.startswith('>'):
            bq_lines = []
            while i < len(lines) and lines[i].strip().startswith('>'):
                bq_lines.append(re.sub(r'^>\s*', '', lines[i].strip()))
                i += 1
            html_parts.append(f'<blockquote>{_inline(" ".join(bq_lines))}</blockquote>')
            continue

        # Paragraph
        para_lines = []
        while i < len(lines):
            l = lines[i].strip()
            if not l or l.startswith('#') or l.startswith('|') or re.match(r'^[-*]\s+', l) or re.match(r'^\d+\.\s+', l) or l.startswith('>'):
                break
            para_lines.append(l)
            i += 1
        if para_lines:
            html_parts.append(f'<p>{_inline(" ".join(para_lines))}</p>')

    return '\n'.join(html_parts)


def _render_html_table(rows: list[dict]) -> str:
    """Render parsed table rows as HTML table with status coloring."""
    if not rows:
        return ''
    headers = list(rows[0].keys())
    parts = ['<table>', '<thead><tr>']
    for h in headers:
        parts.append(f'<th>{_inline(h)}</th>')
    parts.append('</tr></thead><tbody>')
    for row in rows:
        parts.append('<tr>')
        for h in headers:
            val = row.get(h, '')
            td_class = _td_status_class(val)
            parts.append(f'<td{td_class}>{_inline(val)}</td>')
        parts.append('</tr>')
    parts.append('</tbody></table>')
    return '\n'.join(parts)


def _td_status_class(val: str) -> str:
    """Determine CSS class for a table cell based on value."""
    clean = re.sub(r'\*+', '', val).strip().lower()
    if clean in ('running', 'active', 'completed', 'above'):
        return ' class="status-ok"'
    if clean in ('down', 'fault', 'stopped', 'unplanned', 'below'):
        return ' class="status-bad"'
    if clean in ('idle', 'unknown', 'cleaning', 'planned downtime'):
        return ' class="status-warn"'
    pct = _extract_pct(val)
    if pct is not None:
        if pct < 80:
            return ' class="status-bad"'
        if pct < 90:
            return ' class="status-warn"'
    return ''


# ---------------------------------------------------------------------------
# Section parser
# ---------------------------------------------------------------------------

SECTION_PATTERN = re.compile(r'^##\s+(\d+)\.\s+(.+)$', re.MULTILINE)

SECTION_IDS = {
    '1': 'executive-summary',
    '2': 'safety',
    '3': 'production',
    '4': 'oee',
    '5': 'quality',
    '6': 'equipment',
    '7': 'work-orders',
    '8': 'upcoming',
    '9': 'notes',
}

SECTION_ICONS = {
    '1': '\U0001f4cb',  # clipboard
    '2': '\U0001f6e1',  # shield
    '3': '\U0001f3ed',  # factory
    '4': '\U0001f4ca',  # bar chart
    '5': '\u2705',      # check mark
    '6': '\u2699',      # gear
    '7': '\U0001f4e6',  # package
    '8': '\U0001f4c5',  # calendar
    '9': '\U0001f4dd',  # memo
}


def parse_report(md: str) -> dict:
    """Parse the shift report markdown into structured data.

    Returns dict with:
        - preamble: text before first section
        - sections: ordered list of {num, title, content, id, icon}
        - metadata: {title, site, shift, date}
    """
    # Extract metadata from preamble
    metadata = {}
    h1 = re.search(r'^#\s+(.+)$', md, re.MULTILINE)
    if h1:
        metadata['title'] = h1.group(1).strip()
        site_m = re.search(r'(Site\s*\d+)', h1.group(1), re.IGNORECASE)
        if site_m:
            metadata['site'] = site_m.group(1)

    # Extract shift/date from preamble bold fields
    shift_m = re.search(r'\*\*Shift\*\*:\s*(.+)', md)
    if shift_m:
        metadata['shift'] = shift_m.group(1).strip()
    date_m = re.search(r'\*\*Date\*\*:\s*(.+)', md)
    if date_m:
        metadata['date'] = date_m.group(1).strip()
    site_m2 = re.search(r'\*\*Site\*\*:\s*(.+)', md)
    if site_m2:
        metadata['site'] = site_m2.group(1).strip()

    # Split into sections
    matches = list(SECTION_PATTERN.finditer(md))
    sections = []

    for i, m in enumerate(matches):
        num = m.group(1)
        title = m.group(2).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(md)
        content = md[start:end].strip()
        sections.append({
            'num': num,
            'title': title,
            'content': content,
            'id': SECTION_IDS.get(num, f'section-{num}'),
            'icon': SECTION_ICONS.get(num, ''),
        })

    # Preamble is everything before first section header
    preamble = md[:matches[0].start()].strip() if matches else md.strip()

    return {
        'preamble': preamble,
        'sections': sections,
        'metadata': metadata,
    }


def _find_tables_in_content(content: str) -> list[tuple[list[dict], int, int]]:
    """Find all markdown tables in content. Returns [(rows, start_idx, end_idx), ...]."""
    lines = content.split('\n')
    tables = []
    i = 0
    while i < len(lines):
        if lines[i].strip().startswith('|'):
            table_lines = []
            start = i
            while i < len(lines) and lines[i].strip().startswith('|'):
                table_lines.append(lines[i])
                i += 1
            rows = _parse_md_table(table_lines)
            if rows:
                tables.append((rows, start, i))
        else:
            i += 1
    return tables


def _content_after_tables(content: str) -> str:
    """Get content that follows tables (notes, bullet points, etc.)."""
    lines = content.split('\n')
    # Find last table end
    last_table_end = 0
    i = 0
    while i < len(lines):
        if lines[i].strip().startswith('|'):
            while i < len(lines) and lines[i].strip().startswith('|'):
                i += 1
            last_table_end = i
        else:
            i += 1
    remaining = '\n'.join(lines[last_table_end:]).strip()
    return remaining


# ---------------------------------------------------------------------------
# Data extractors
# ---------------------------------------------------------------------------

def extract_hero_stats(sections: list[dict]) -> dict:
    """Extract hero statistics from parsed sections."""
    stats = {
        'avg_oee': None,
        'total_production': 0,
        'total_defects': 0,
        'active_lines': 0,
        'total_lines': 0,
    }

    # Extract from OEE section (section 4)
    oee_section = next((s for s in sections if s['num'] == '4'), None)
    if oee_section:
        tables = _find_tables_in_content(oee_section['content'])
        if tables:
            oee_values = []
            for row in tables[0][0]:
                for key in row:
                    if key.lower() == 'oee':
                        pct = _extract_pct(row[key])
                        if pct is not None:
                            oee_values.append(pct)
            if oee_values:
                stats['avg_oee'] = round(sum(oee_values) / len(oee_values), 1)
                stats['total_lines'] = len(oee_values)

    # Extract from Production section (section 3)
    prod_section = next((s for s in sections if s['num'] == '3'), None)
    if prod_section:
        tables = _find_tables_in_content(prod_section['content'])
        if tables:
            for row in tables[0][0]:
                for key in row:
                    if key.lower() == 'actual':
                        n = _extract_number(row[key])
                        if n is not None:
                            stats['total_production'] += int(n)

    # Extract from Equipment section (section 6) - count running lines
    equip_section = next((s for s in sections if s['num'] == '6'), None)
    if equip_section:
        tables = _find_tables_in_content(equip_section['content'])
        if tables:
            for row in tables[0][0]:
                for key in row:
                    if 'overall' in key.lower() or 'status' in key.lower():
                        if 'active' in row[key].lower() or 'production' in row[key].lower() or 'running' in row[key].lower():
                            stats['active_lines'] += 1

    # Extract defects from Quality section (section 5)
    quality_section = next((s for s in sections if s['num'] == '5'), None)
    if quality_section:
        if 'zero defect' in quality_section['content'].lower():
            stats['total_defects'] = 0

    return stats


# ---------------------------------------------------------------------------
# Section renderers
# ---------------------------------------------------------------------------

def render_at_a_glance(section: dict) -> str:
    """Render executive summary as an amber 'At a Glance' card."""
    # Parse the exec summary content into sentences for structured display
    content = section['content']
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
    text = ' '.join(paragraphs)

    # Try to split into structured highlights
    sentences = re.split(r'(?<=[.!])\s+', text)

    highlights_html = ''
    for sentence in sentences:
        if sentence.strip():
            highlights_html += f'<div class="glance-item">{_inline(sentence.strip())}</div>\n'

    return f'''
    <div class="at-a-glance" id="{section['id']}">
      <div class="glance-header">
        <span class="glance-icon">{section['icon']}</span>
        <span class="glance-title">{section['title']}</span>
      </div>
      <div class="glance-body">
        {highlights_html}
      </div>
      <div class="glance-nav">
        Jump to: <a href="#production">Production</a> &middot;
        <a href="#oee">OEE</a> &middot;
        <a href="#quality">Quality</a> &middot;
        <a href="#equipment">Equipment</a> &middot;
        <a href="#work-orders">Work Orders</a>
      </div>
    </div>'''


def render_stats_row(stats: dict) -> str:
    """Render hero statistics row."""
    items = []

    if stats['avg_oee'] is not None:
        oee_class = 'stat-ok' if stats['avg_oee'] >= 85 else ('stat-warn' if stats['avg_oee'] >= 80 else 'stat-bad')
        items.append(f'''
        <div class="stat">
          <div class="stat-value {oee_class}">{stats['avg_oee']}%</div>
          <div class="stat-label">Avg OEE</div>
        </div>''')

    if stats['total_production'] > 0:
        items.append(f'''
        <div class="stat">
          <div class="stat-value">{stats['total_production']:,}</div>
          <div class="stat-label">Total Units</div>
        </div>''')

    items.append(f'''
    <div class="stat">
      <div class="stat-value {"stat-ok" if stats["total_defects"] == 0 else "stat-bad"}">{stats['total_defects']:,}</div>
      <div class="stat-label">Defects</div>
    </div>''')

    if stats['total_lines'] > 0:
        items.append(f'''
        <div class="stat">
          <div class="stat-value">{stats['active_lines']}/{stats['total_lines']}</div>
          <div class="stat-label">Lines Active</div>
        </div>''')

    return f'<div class="stats-row">{"".join(items)}</div>'


def render_nav_toc(sections: list[dict]) -> str:
    """Render navigation TOC with pill-style links."""
    links = []
    for s in sections:
        links.append(f'<a href="#{s["id"]}">{s["icon"]} {s["title"]}</a>')
    return f'<nav class="nav-toc">{"".join(links)}</nav>'


def render_safety(section: dict) -> str:
    """Render safety section with appropriate color coding."""
    content = section['content'].strip()
    is_clear = 'no safety incident' in content.lower()
    card_class = 'safety-clear' if is_clear else 'safety-alert'
    icon = '\u2705' if is_clear else '\u26a0\ufe0f'

    return f'''
    <div class="section-card {card_class}" id="{section['id']}">
      <h2>{section['icon']} {section['title']}</h2>
      <div class="safety-status">
        <span class="safety-icon">{icon}</span>
        <span>{_inline(content)}</span>
      </div>
    </div>'''


def render_production(section: dict) -> str:
    """Render production vs target with progress bars."""
    tables = _find_tables_in_content(section['content'])
    notes = _content_after_tables(section['content'])

    html = f'''
    <div class="section-card" id="{section['id']}">
      <h2>{section['icon']} {section['title']}</h2>'''

    if tables:
        rows = tables[0][0]
        html += '<div class="production-grid">'

        for row in rows:
            line = row.get('Line', '')
            wo = row.get('Work Order', '')
            product = row.get('Product', '')
            actual_str = row.get('Actual', '')
            target_str = row.get('Target', '')
            comp_str = row.get('Completion %', '')
            notes_col = row.get('Notes', '')

            actual = _extract_number(actual_str) or 0
            target = _extract_number(target_str) or 1
            comp = _extract_pct(comp_str)
            if comp is None:
                comp = round(actual / target * 100, 1) if target > 0 else 0

            # Color based on completion
            bar_color = '#38a169' if comp >= 90 else ('#d69e2e' if comp >= 50 else '#e53e3e')
            status_class = 'prod-ok' if comp >= 90 else ('prod-warn' if comp >= 50 else 'prod-behind')

            html += f'''
            <div class="production-card {status_class}">
              <div class="prod-header">
                <span class="prod-line">{_inline(line)}</span>
                <span class="prod-wo">{_inline(wo)}</span>
              </div>
              <div class="prod-product">{_inline(product)}</div>
              <div class="prod-progress">
                <div class="progress-bar">
                  <div class="progress-fill" style="width:{min(comp, 100)}%;background:{bar_color}"></div>
                </div>
                <span class="prod-pct">{comp}%</span>
              </div>
              <div class="prod-counts">{_inline(actual_str)} / {_inline(target_str)}</div>
              <div class="prod-notes">{_inline(notes_col)}</div>
            </div>'''

        html += '</div>'

    if notes:
        html += f'<div class="section-notes">{_paragraphs_and_bullets(notes)}</div>'

    html += '</div>'
    return html


def render_oee(section: dict) -> str:
    """Render OEE summary with horizontal bar charts."""
    tables = _find_tables_in_content(section['content'])
    notes = _content_after_tables(section['content'])

    html = f'''
    <div class="section-card" id="{section['id']}">
      <h2>{section['icon']} {section['title']}</h2>'''

    if tables:
        # First table: OEE metrics
        oee_rows = tables[0][0]

        html += '<div class="oee-grid">'
        for row in oee_rows:
            line = row.get('Line', '')
            oee = _extract_pct(row.get('OEE', ''))
            avail = _extract_pct(row.get('Availability', ''))
            perf = _extract_pct(row.get('Performance', ''))
            qual = _extract_pct(row.get('Quality', ''))
            vs_target = row.get('vs. Target (85%)', row.get('vs. Target', ''))

            oee_class = 'oee-ok' if (oee and oee >= 85) else 'oee-warn'

            html += f'''
            <div class="oee-card {oee_class}">
              <div class="oee-header">
                <span class="oee-line">{_inline(line)}</span>
                <span class="oee-value">{oee}%</span>
                <span class="oee-target {_td_status_class(vs_target).replace(" class=", "").replace('"', '')}">{_inline(vs_target)}</span>
              </div>
              <div class="oee-bars">'''

            metrics = [
                ('Availability', avail, '#2b6cb0'),
                ('Performance', perf, '#2563eb'),
                ('Quality', qual, '#38a169'),
            ]
            for label, val, color in metrics:
                if val is not None:
                    bar_w = min(val, 100)
                    val_class = '' if val >= 95 else (' bar-warn' if val >= 90 else ' bar-bad')
                    html += f'''
                <div class="bar-row">
                  <div class="bar-label">{label}</div>
                  <div class="bar-track"><div class="bar-fill{val_class}" style="width:{bar_w}%;background:{color}"></div></div>
                  <div class="bar-value">{val}%</div>
                </div>'''

            html += '''
              </div>
            </div>'''

        html += '</div>'

        # Second table: time utilization (if present)
        if len(tables) > 1:
            time_rows = tables[1][0]
            html += '<h3>Time Utilization</h3><div class="time-util-grid">'

            for row in time_rows:
                line = row.get('Line', '')
                running = _extract_pct(row.get('% Running', ''))
                idle = _extract_pct(row.get('% Idle', ''))
                planned = _extract_pct(row.get('% Planned Down', ''))
                unplanned = _extract_pct(row.get('% Unplanned Down', ''))

                html += f'''
                <div class="time-card">
                  <div class="time-line">{_inline(line)}</div>
                  <div class="time-bars">'''

                segments = [
                    ('Running', running, '#38a169'),
                    ('Idle', idle, '#d69e2e'),
                    ('Planned', planned, '#63b3ed'),
                    ('Unplanned', unplanned, '#e53e3e'),
                ]
                for label, val, color in segments:
                    if val is not None and val > 0:
                        flag = ' bar-flagged' if label == 'Unplanned' and val > 5 else ''
                        html += f'''
                    <div class="bar-row">
                      <div class="bar-label">{label}</div>
                      <div class="bar-track"><div class="bar-fill{flag}" style="width:{min(val, 100)}%;background:{color}"></div></div>
                      <div class="bar-value">{val}%</div>
                    </div>'''

                html += '''
                  </div>
                </div>'''

            html += '</div>'

    if notes:
        html += f'<div class="section-notes">{_paragraphs_and_bullets(notes)}</div>'

    html += '</div>'
    return html


def render_quality(section: dict) -> str:
    """Render quality flags with color-coded cards."""
    content = section['content']
    tables = _find_tables_in_content(content)
    notes = _content_after_tables(content)

    # Determine if quality is clean
    is_clean = ('zero defect' in content.lower() or 'no quality flag' in content.lower()
                or 'no actionable quality' in content.lower())

    card_class = 'quality-clear' if is_clean else 'quality-alert'

    html = f'''
    <div class="section-card {card_class}" id="{section['id']}">
      <h2>{section['icon']} {section['title']}</h2>'''

    # Render content before first table
    lines = content.split('\n')
    pre_table = []
    for line in lines:
        if line.strip().startswith('|'):
            break
        pre_table.append(line)
    pre_text = '\n'.join(pre_table).strip()
    if pre_text:
        html += f'<div class="quality-summary">{_paragraphs_and_bullets(pre_text)}</div>'

    # Render SPC table if present
    if tables:
        html += '<div class="spc-table">'
        html += _render_html_table(tables[0][0])
        html += '</div>'

    if notes:
        assessment = notes
        if is_clean:
            html += f'<div class="quality-assessment clear">{_paragraphs_and_bullets(assessment)}</div>'
        else:
            html += f'<div class="quality-assessment alert">{_paragraphs_and_bullets(assessment)}</div>'

    html += '</div>'
    return html


def render_equipment(section: dict) -> str:
    """Render equipment status with colored badges."""
    content = section['content']
    tables = _find_tables_in_content(content)

    html = f'''
    <div class="section-card" id="{section['id']}">
      <h2>{section['icon']} {section['title']}</h2>'''

    # Split content by sub-headers (### Filling Lines, ### Mixing Vats)
    sub_sections = re.split(r'^###\s+(.+)$', content, flags=re.MULTILINE)

    # sub_sections[0] is content before first ###
    # sub_sections[1] is first sub-header name, [2] is its content, etc.
    if len(sub_sections) > 1:
        for i in range(1, len(sub_sections), 2):
            sub_title = sub_sections[i].strip()
            sub_content = sub_sections[i + 1].strip() if i + 1 < len(sub_sections) else ''

            html += f'<h3>{sub_title}</h3>'

            # Find tables in this sub-section
            sub_tables = _find_tables_in_content(sub_content)
            sub_notes = _content_after_tables(sub_content)

            if sub_tables:
                rows = sub_tables[0][0]
                html += '<div class="equipment-grid">'

                for row in rows:
                    row_html = '<div class="equip-card">'
                    first_key = True
                    for key, val in row.items():
                        if first_key:
                            row_html += f'<div class="equip-name">{_inline(val)}</div><div class="equip-states">'
                            first_key = False
                        else:
                            clean_val = re.sub(r'\*+', '', val).strip()
                            badge_class = _badge_class(clean_val)
                            row_html += f'<div class="equip-state"><span class="state-label">{key}</span><span class="state-badge {badge_class}">{_inline(val)}</span></div>'
                    row_html += '</div></div>'
                    html += row_html

                html += '</div>'

            if sub_notes:
                html += f'<div class="section-notes">{_paragraphs_and_bullets(sub_notes)}</div>'
    else:
        # No sub-headers, render generically
        html += _paragraphs_and_bullets(content)

    html += '</div>'
    return html


def _badge_class(val: str) -> str:
    """Determine badge CSS class from equipment state value."""
    # Strip markdown bold and get the primary state (before any dash/description)
    clean = re.sub(r'\*+', '', val).strip()
    # Extract the first word/phrase before a dash or long description
    primary = clean.split('—')[0].split(' - ')[0].strip().lower()

    # Exact or prefix matches on the primary state word
    ok_states = ('running', 'active', 'fill', 'filling', 'transfer', 'completed')
    warn_states = ('idle', 'unknown', 'cleaning', 'planned downtime', 'cool',
                   'cooling', 'offline', 'in progress')
    bad_states = ('down', 'fault', 'stopped', 'unplanned')

    for w in ok_states:
        if primary == w or primary.startswith(w):
            return 'badge-ok'
    for w in warn_states:
        if primary == w or primary.startswith(w):
            return 'badge-warn'
    for w in bad_states:
        if primary == w or primary.startswith(w):
            return 'badge-bad'
    return 'badge-neutral'


def render_work_orders(section: dict) -> str:
    """Render work orders with progress indicators."""
    tables = _find_tables_in_content(section['content'])
    notes = _content_after_tables(section['content'])

    html = f'''
    <div class="section-card" id="{section['id']}">
      <h2>{section['icon']} {section['title']}</h2>'''

    if tables:
        rows = tables[0][0]
        html += '<div class="wo-grid">'

        for row in rows:
            line = row.get('Line', '')
            wo_num = row.get('WO Number', '')
            product = row.get('Product', '')
            status = row.get('Status', '')
            comp_str = row.get('Completion %', '')
            wo_notes = row.get('Notes', '')

            comp = _extract_pct(comp_str) or 0

            clean_status = re.sub(r'\*+', '', status).strip()
            is_complete = 'completed' in clean_status.lower() or comp >= 100
            bar_color = '#38a169' if is_complete else ('#d69e2e' if comp >= 50 else '#2563eb')
            card_border = 'wo-complete' if is_complete else ''

            html += f'''
            <div class="wo-card {card_border}">
              <div class="wo-header">
                <span class="wo-line">{_inline(line)}</span>
                <span class="wo-number">{_inline(wo_num)}</span>
                <span class="wo-status {_badge_class(clean_status)}">{_inline(status)}</span>
              </div>
              <div class="wo-product">{_inline(product)}</div>
              <div class="wo-progress">
                <div class="progress-bar">
                  <div class="progress-fill" style="width:{min(comp, 100)}%;background:{bar_color}"></div>
                </div>
                <span class="wo-pct">{comp}%</span>
              </div>
              <div class="wo-notes">{_inline(wo_notes)}</div>
            </div>'''

        html += '</div>'

    if notes:
        html += f'<div class="section-notes priority-note">{_paragraphs_and_bullets(notes)}</div>'

    html += '</div>'
    return html


def render_generic(section: dict) -> str:
    """Generic section renderer for Upcoming, Notes, or any fallback."""
    html = f'''
    <div class="section-card" id="{section['id']}">
      <h2>{section['icon']} {section['title']}</h2>
      {_paragraphs_and_bullets(section['content'])}
    </div>'''
    return html


# ---------------------------------------------------------------------------
# Section dispatch
# ---------------------------------------------------------------------------

SECTION_RENDERERS = {
    '1': render_at_a_glance,
    '2': render_safety,
    '3': render_production,
    '4': render_oee,
    '5': render_quality,
    '6': render_equipment,
    '7': render_work_orders,
    '8': render_generic,
    '9': render_generic,
}


# ---------------------------------------------------------------------------
# HTML template
# ---------------------------------------------------------------------------

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@200;300;400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root {{
    --primary: #1e1e1e;
    --primary-light: #2d2d2d;
    --accent: #0bb6ff;
    --accent-dim: rgba(11, 182, 255, 0.15);
    --accent-border: rgba(11, 182, 255, 0.3);
    --bg: #1b1b1f;
    --card-bg: #272727;
    --card-bg-alt: #2d2d30;
    --text: #d4d4d4;
    --text-light: #9a9a9a;
    --text-dark: #ffffff;
    --border: #3b3b3f;
    --border-light: #333336;
    --shadow: 0 2px 8px rgba(0,0,0,0.3);
    --ok: #0db14b;
    --ok-bg: rgba(13, 177, 75, 0.12);
    --ok-border: rgba(13, 177, 75, 0.3);
    --warn: #fcb711;
    --warn-bg: rgba(252, 183, 17, 0.12);
    --warn-border: rgba(252, 183, 17, 0.3);
    --bad: #ff337f;
    --bad-bg: rgba(255, 51, 127, 0.12);
    --bad-border: rgba(255, 51, 127, 0.3);
    --blue-bg: rgba(11, 182, 255, 0.08);
    --blue-border: rgba(11, 182, 255, 0.25);
  }}

  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  body {{
    font-family: 'Poppins', "Segoe UI Variable", "Segoe UI", sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.65;
    padding: 0;
  }}

  /* --- Header --- */
  .report-header {{
    background: var(--primary);
    border-bottom: 1px solid var(--border);
    color: var(--text-dark);
    padding: 2rem 2rem 1.75rem;
  }}
  .report-header .container {{
    max-width: 960px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    gap: 16px;
  }}
  .header-icon {{
    width: 36px;
    height: 36px;
    flex-shrink: 0;
  }}
  .header-icon svg {{
    fill: var(--accent);
    width: 100%;
    height: 100%;
  }}
  .header-text {{
    flex: 1;
  }}
  .report-header h1 {{
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: 0.35rem;
    color: var(--text-dark);
    letter-spacing: -0.01em;
  }}
  .report-header h1 span {{
    font-weight: 200;
    color: var(--text-light);
    margin: 0 6px;
  }}
  .report-header .meta {{
    font-size: 0.8rem;
    font-weight: 300;
    color: var(--text-light);
    display: flex;
    gap: 1.5rem;
    flex-wrap: wrap;
  }}
  .report-header .meta strong {{
    font-weight: 500;
    color: var(--text);
  }}

  /* --- Container --- */
  .container {{
    max-width: 960px;
    margin: 0 auto;
    padding: 0 1.5rem;
  }}
  .content {{
    padding: 2rem 0 3rem;
  }}

  /* --- Navigation TOC --- */
  .nav-toc {{
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin: 0 0 2rem 0;
    padding: 14px 16px;
    background: var(--card-bg);
    border-radius: 6px;
    border: 1px solid var(--border);
  }}
  .nav-toc a {{
    font-size: 11px;
    font-weight: 400;
    color: var(--text-light);
    text-decoration: none;
    padding: 5px 12px;
    border-radius: 4px;
    background: var(--card-bg-alt);
    border: 1px solid var(--border-light);
    transition: all 0.15s;
    white-space: nowrap;
  }}
  .nav-toc a:hover {{
    background: var(--accent-dim);
    border-color: var(--accent-border);
    color: var(--accent);
  }}

  /* --- Stats Row --- */
  .stats-row {{
    display: flex;
    gap: 24px;
    margin-bottom: 2rem;
    padding: 20px 0;
    border-top: 1px solid var(--border);
    border-bottom: 1px solid var(--border);
    flex-wrap: wrap;
    justify-content: center;
  }}
  .stat {{
    text-align: center;
    min-width: 100px;
  }}
  .stat-value {{
    font-size: 28px;
    font-weight: 600;
    color: var(--text-dark);
  }}
  .stat-label {{
    font-size: 10px;
    font-weight: 400;
    color: var(--text-light);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 2px;
  }}
  .stat-ok {{ color: var(--ok); }}
  .stat-warn {{ color: var(--warn); }}
  .stat-bad {{ color: var(--bad); }}

  /* --- At a Glance --- */
  .at-a-glance {{
    background: var(--card-bg);
    border: 1px solid var(--accent-border);
    border-left: 4px solid var(--accent);
    border-radius: 6px;
    padding: 20px 24px;
    margin-bottom: 2rem;
  }}
  .glance-header {{
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 14px;
  }}
  .glance-icon {{
    font-size: 18px;
  }}
  .glance-title {{
    font-size: 16px;
    font-weight: 600;
    color: var(--accent);
  }}
  .glance-body {{
    display: flex;
    flex-direction: column;
    gap: 8px;
  }}
  .glance-item {{
    font-size: 13px;
    font-weight: 300;
    color: var(--text);
    line-height: 1.65;
  }}
  .glance-item strong {{
    color: var(--text-dark);
    font-weight: 500;
  }}
  .glance-nav {{
    margin-top: 14px;
    padding-top: 10px;
    border-top: 1px solid var(--border);
    font-size: 12px;
    color: var(--text-light);
  }}
  .glance-nav a {{
    color: var(--accent);
    text-decoration: none;
    font-weight: 500;
  }}
  .glance-nav a:hover {{
    text-decoration: underline;
  }}

  /* --- Section Cards --- */
  .section-card {{
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 24px;
    margin-bottom: 1.5rem;
    box-shadow: var(--shadow);
  }}
  .section-card h2 {{
    font-size: 1.05rem;
    font-weight: 600;
    color: var(--text-dark);
    margin: 0 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid var(--accent);
  }}
  .section-card h3 {{
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--accent);
    margin: 1.25rem 0 0.75rem;
  }}
  .section-card p {{
    margin: 0.5rem 0;
    font-size: 13px;
    font-weight: 300;
    line-height: 1.7;
    color: var(--text);
  }}
  .section-card ul, .section-card ol {{
    margin: 0.5rem 0 0.5rem 1.5rem;
    font-size: 13px;
    font-weight: 300;
  }}
  .section-card li {{
    margin: 0.4rem 0;
    line-height: 1.6;
  }}

  /* --- Safety --- */
  .safety-clear {{
    background: var(--ok-bg);
    border-color: var(--ok-border);
  }}
  .safety-clear h2 {{
    border-color: var(--ok);
  }}
  .safety-alert {{
    background: var(--bad-bg);
    border-color: var(--bad-border);
  }}
  .safety-alert h2 {{
    border-color: var(--bad);
  }}
  .safety-status {{
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 14px;
    font-weight: 400;
  }}
  .safety-icon {{
    font-size: 18px;
  }}

  /* --- Production Grid --- */
  .production-grid {{
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-bottom: 1rem;
  }}
  .production-card {{
    background: var(--card-bg-alt);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 16px;
    border-left: 3px solid var(--accent);
  }}
  .prod-ok {{ border-left-color: var(--ok); }}
  .prod-warn {{ border-left-color: var(--warn); }}
  .prod-behind {{ border-left-color: var(--bad); }}
  .prod-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 4px;
  }}
  .prod-line {{
    font-weight: 600;
    font-size: 14px;
    color: var(--text-dark);
  }}
  .prod-wo {{
    font-size: 11px;
    font-family: 'Consolas', 'Liberation Mono', monospace;
    color: var(--text-light);
    background: var(--card-bg);
    padding: 2px 8px;
    border-radius: 3px;
    border: 1px solid var(--border-light);
  }}
  .prod-product {{
    font-size: 13px;
    font-weight: 300;
    color: var(--text);
    margin-bottom: 10px;
  }}
  .prod-progress {{
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 6px;
  }}
  .progress-bar {{
    flex: 1;
    height: 6px;
    background: var(--border);
    border-radius: 3px;
    overflow: hidden;
  }}
  .progress-fill {{
    height: 100%;
    border-radius: 3px;
    transition: width 0.3s;
  }}
  .prod-pct, .wo-pct {{
    font-size: 13px;
    font-weight: 600;
    color: var(--text-dark);
    min-width: 50px;
    text-align: right;
  }}
  .prod-counts {{
    font-size: 12px;
    font-weight: 300;
    color: var(--text-light);
  }}
  .prod-notes {{
    font-size: 12px;
    font-weight: 300;
    color: var(--text-light);
    margin-top: 4px;
  }}

  /* --- OEE Grid --- */
  .oee-grid {{
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-bottom: 1rem;
  }}
  .oee-card {{
    background: var(--card-bg-alt);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 16px;
    border-left: 3px solid var(--ok);
  }}
  .oee-warn {{
    border-left-color: var(--warn);
  }}
  .oee-header {{
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;
  }}
  .oee-line {{
    font-weight: 600;
    font-size: 14px;
    color: var(--text-dark);
  }}
  .oee-value {{
    font-size: 22px;
    font-weight: 600;
    color: var(--text-dark);
    margin-left: auto;
  }}
  .oee-target {{
    font-size: 11px;
    padding: 2px 8px;
    border-radius: 3px;
    font-weight: 500;
  }}
  .oee-bars {{
    display: flex;
    flex-direction: column;
    gap: 6px;
  }}

  /* --- Bar Charts --- */
  .bar-row {{
    display: flex;
    align-items: center;
  }}
  .bar-label {{
    width: 100px;
    font-size: 11px;
    font-weight: 400;
    color: var(--text-light);
    flex-shrink: 0;
  }}
  .bar-track {{
    flex: 1;
    height: 5px;
    background: var(--border);
    border-radius: 3px;
    margin: 0 10px;
    overflow: hidden;
  }}
  .bar-fill {{
    height: 100%;
    border-radius: 3px;
    background: var(--accent);
  }}
  .bar-warn {{ background: var(--warn) !important; }}
  .bar-bad {{ background: var(--bad) !important; }}
  .bar-flagged {{ background: var(--bad) !important; }}
  .bar-value {{
    width: 48px;
    font-size: 11px;
    font-weight: 400;
    color: var(--text-light);
    text-align: right;
    font-family: 'Consolas', 'Liberation Mono', monospace;
  }}

  /* --- Time Utilization --- */
  .time-util-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 10px;
    margin-bottom: 1rem;
  }}
  .time-card {{
    background: var(--card-bg-alt);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 14px;
  }}
  .time-line {{
    font-weight: 600;
    font-size: 13px;
    color: var(--text-dark);
    margin-bottom: 10px;
  }}
  .time-bars {{
    display: flex;
    flex-direction: column;
    gap: 5px;
  }}

  /* --- Quality --- */
  .quality-clear {{
    border-left: 3px solid var(--ok);
  }}
  .quality-alert {{
    border-left: 3px solid var(--bad);
  }}
  .quality-summary {{
    margin-bottom: 1rem;
  }}
  .quality-assessment {{
    margin-top: 1rem;
    padding: 12px 16px;
    border-radius: 4px;
    font-size: 13px;
  }}
  .quality-assessment.clear {{
    background: var(--ok-bg);
    border: 1px solid var(--ok-border);
    color: var(--ok);
  }}
  .quality-assessment.alert {{
    background: var(--bad-bg);
    border: 1px solid var(--bad-border);
    color: var(--bad);
  }}
  .spc-table {{
    margin: 1rem 0;
    overflow-x: auto;
  }}

  /* --- Equipment --- */
  .equipment-grid {{
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-bottom: 1rem;
  }}
  .equip-card {{
    background: var(--card-bg-alt);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 12px 14px;
    display: flex;
    align-items: center;
    gap: 16px;
    flex-wrap: wrap;
  }}
  .equip-name {{
    font-weight: 600;
    font-size: 13px;
    color: var(--text-dark);
    min-width: 120px;
  }}
  .equip-states {{
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    flex: 1;
  }}
  .equip-state {{
    display: flex;
    align-items: center;
    gap: 6px;
  }}
  .state-label {{
    font-size: 10px;
    font-weight: 400;
    color: var(--text-light);
    text-transform: uppercase;
    letter-spacing: 0.04em;
  }}
  .state-badge {{
    font-size: 11px;
    padding: 2px 10px;
    border-radius: 3px;
    font-weight: 500;
  }}
  .badge-ok {{
    background: var(--ok-bg);
    color: var(--ok);
    border: 1px solid var(--ok-border);
  }}
  .badge-warn {{
    background: var(--warn-bg);
    color: var(--warn);
    border: 1px solid var(--warn-border);
  }}
  .badge-bad {{
    background: var(--bad-bg);
    color: var(--bad);
    border: 1px solid var(--bad-border);
  }}
  .badge-neutral {{
    background: var(--card-bg);
    color: var(--text-light);
    border: 1px solid var(--border);
  }}

  /* --- Work Orders --- */
  .wo-grid {{
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-bottom: 1rem;
  }}
  .wo-card {{
    background: var(--card-bg-alt);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 16px;
  }}
  .wo-complete {{
    border-left: 3px solid var(--ok);
    background: var(--ok-bg);
  }}
  .wo-header {{
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 4px;
    flex-wrap: wrap;
  }}
  .wo-line {{
    font-weight: 600;
    font-size: 13px;
    color: var(--text-dark);
  }}
  .wo-number {{
    font-size: 11px;
    color: var(--text-light);
    background: var(--card-bg);
    padding: 2px 8px;
    border-radius: 3px;
    font-family: 'Consolas', 'Liberation Mono', monospace;
    border: 1px solid var(--border-light);
  }}
  .wo-status {{
    font-size: 11px;
    padding: 2px 10px;
    border-radius: 3px;
    font-weight: 500;
    margin-left: auto;
  }}
  .wo-product {{
    font-size: 13px;
    font-weight: 300;
    color: var(--text);
    margin-bottom: 10px;
  }}
  .wo-progress {{
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 6px;
  }}
  .wo-notes {{
    font-size: 12px;
    font-weight: 300;
    color: var(--text-light);
  }}

  /* --- Notes --- */
  .section-notes {{
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid var(--border);
    font-size: 13px;
  }}
  .priority-note {{
    background: var(--blue-bg);
    border: 1px solid var(--blue-border);
    border-radius: 4px;
    padding: 12px 16px;
    margin-top: 1rem;
    border-top: none;
  }}

  /* --- Tables (generic) --- */
  table {{
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    margin: 1rem 0;
    font-size: 0.8rem;
    background: var(--card-bg-alt);
    border-radius: 5px;
    overflow: hidden;
    border: 1px solid var(--border);
  }}
  thead {{
    background: var(--primary);
  }}
  th {{
    padding: 0.6rem 0.75rem;
    text-align: left;
    font-weight: 500;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--text-light);
    border-bottom: 1px solid var(--border);
  }}
  td {{
    padding: 0.5rem 0.75rem;
    border-bottom: 1px solid var(--border-light);
    font-weight: 300;
    color: var(--text);
  }}
  tbody tr:nth-child(even) {{ background: var(--card-bg); }}
  tbody tr:hover {{ background: var(--accent-dim); }}

  .status-ok {{ color: var(--ok); font-weight: 500; }}
  .status-warn {{ color: var(--warn); font-weight: 500; }}
  .status-bad {{ color: var(--bad); font-weight: 500; background: var(--bad-bg); }}

  /* --- Misc --- */
  hr {{ border: none; border-top: 1px solid var(--border); margin: 1.5rem 0; }}

  code {{
    background: var(--card-bg-alt);
    border: 1px solid var(--border-light);
    padding: 0.15rem 0.35rem;
    border-radius: 3px;
    font-size: 0.85em;
    font-family: 'Consolas', 'Liberation Mono', monospace;
    color: var(--text);
  }}

  strong {{ font-weight: 600; }}

  blockquote {{
    border-left: 3px solid var(--accent);
    padding: 0.5rem 1rem;
    margin: 1rem 0;
    color: var(--text-light);
    font-size: 12px;
    background: var(--card-bg-alt);
    border-radius: 0 4px 4px 0;
  }}

  .footer {{
    text-align: center;
    color: var(--text-light);
    font-size: 0.7rem;
    font-weight: 300;
    margin-top: 3rem;
    padding-top: 1rem;
    border-top: 1px solid var(--border);
  }}

  /* --- Print --- */
  @media print {{
    body {{ background: #1b1b1f; padding: 0; color: var(--text); }}
    .report-header {{
      background: var(--primary) !important;
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }}
    .container {{ max-width: 100%; padding: 0 1rem; }}
    .nav-toc {{ display: none; }}
    .section-card {{ box-shadow: none; page-break-inside: avoid; }}
    table {{ box-shadow: none; page-break-inside: avoid; }}
    h2 {{ page-break-after: avoid; }}
    .status-ok, .status-warn, .status-bad,
    .badge-ok, .badge-warn, .badge-bad,
    .safety-clear, .quality-clear, .at-a-glance {{
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }}
  }}

  /* --- Responsive --- */
  @media (max-width: 640px) {{
    .stats-row {{ gap: 16px; }}
    .stat {{ min-width: 80px; }}
    .stat-value {{ font-size: 22px; }}
    .equip-card {{ flex-direction: column; align-items: flex-start; }}
    .oee-header {{ flex-wrap: wrap; }}
    .time-util-grid {{ grid-template-columns: 1fr; }}
  }}
</style>
</head>
<body>

<div class="report-header">
  <div class="container">
    <div class="header-icon">
      <svg viewBox="0 0 511.8 660.7" xmlns="http://www.w3.org/2000/svg">
        <path d="M511.8,340.7l0-21.1l-141.9-27.1L337.8,0l-21.1,0.1L291.5,244L105,98.3l-14.7,15.2l149.3,180.8L0,320.2l0,21.1
          L242.1,367L96.2,553.7l15.2,14.7L292.3,419l26.5,241.7l21.1-0.1l30.2-292.5L511.8,340.7L511.8,340.7z"/>
      </svg>
    </div>
    <div class="header-text">
      <h1>Shift Handoff Report <span>|</span> Enterprise B</h1>
      <div class="meta">
        <span><strong>{site_label}</strong></span>
        <span><strong>{shift_label}</strong></span>
        <span>Generated {timestamp}</span>
      </div>
    </div>
  </div>
</div>

<div class="container">
  <div class="content">
{body}

    <div class="footer">
      Generated by Enterprise B Shift Report System &bull; Powered by Timebase &bull; {timestamp}
    </div>
  </div>
</div>

</body>
</html>
"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description='Convert a shift report markdown file to styled HTML.')
    parser.add_argument('--input', required=True, help='Path to markdown report')
    parser.add_argument('--output', required=True, help='Path for HTML output')
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(json.dumps({
            'status': 'error',
            'error': f'Input file not found: {args.input}'
        }))
        sys.exit(1)

    md_content = input_path.read_text(encoding='utf-8')

    # Parse the report
    report = parse_report(md_content)
    metadata = report['metadata']

    # Extract hero stats
    stats = extract_hero_stats(report['sections'])

    # Build body HTML
    body_parts = []

    # Navigation TOC
    body_parts.append(render_nav_toc(report['sections']))

    # Stats row
    body_parts.append(render_stats_row(stats))

    # Render each section with its tailored renderer
    for section in report['sections']:
        renderer = SECTION_RENDERERS.get(section['num'], render_generic)
        body_parts.append(renderer(section))

    body_html = '\n'.join(body_parts)

    # Template variables
    title = metadata.get('title', 'Shift Handoff Report')
    site = metadata.get('site', 'Enterprise B')
    shift = metadata.get('shift', '')
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')

    full_html = HTML_TEMPLATE.format(
        title=title,
        site_label=site,
        shift_label=shift,
        timestamp=timestamp,
        body=body_html,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(full_html, encoding='utf-8')

    result = {
        'status': 'ok',
        'output': str(output_path),
        'title': title,
        'site': site,
    }
    print(json.dumps(result))


if __name__ == '__main__':
    main()
