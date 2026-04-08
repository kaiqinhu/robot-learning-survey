#!/usr/bin/env python3
"""Extract paper cards, timeline items, and citation edges from HTML files into papers.json."""
import re, json, os, html as htmlmod

BASE = os.path.dirname(os.path.abspath(__file__))

def read(f):
    with open(os.path.join(BASE, f), encoding='utf-8') as fh:
        return fh.read()

def extract_cards(page_id, htm):
    """Extract all <div class="card"> blocks from HTML."""
    cards = []
    # Split by card divs - find each card block
    # Use regex to find card blocks
    pattern = r'<div class="card"[^>]*>(.*?)</div>\s*\n\s*(?=<div class="card"|</div>\s*\n|</?(?:section|h[23]|p ))'
    # Actually, let's use a simpler approach - find balanced div tags for cards

    # Find all card start positions
    card_starts = [m.start() for m in re.finditer(r'<div class="card"', htm)]

    for start in card_starts:
        # Find the balanced end of this div
        depth = 0
        pos = start
        end = start
        while pos < len(htm):
            if htm[pos:pos+4] == '<div':
                depth += 1
            elif htm[pos:pos+6] == '</div>':
                depth -= 1
                if depth == 0:
                    end = pos + 6
                    break
            pos += 1

        block = htm[start:end]
        card = parse_card(block, page_id)
        if card:
            cards.append(card)

    return cards

def parse_card(block, page_id):
    """Parse a single card HTML block into a dict."""
    card = {'pages': [page_id]}

    # Tags
    tags = re.findall(r'<span class="tag"[^>]*>(.*?)</span>', block)
    card['tags'] = [htmlmod.unescape(t.strip()) for t in tags]

    # Title (h4)
    m = re.search(r'<h4>(.*?)</h4>', block, re.DOTALL)
    card['title'] = htmlmod.unescape(m.group(1).strip()) if m else ''

    # Meta
    m = re.search(r'<div class="meta">(.*?)</div>', block, re.DOTALL)
    card['meta'] = htmlmod.unescape(re.sub(r'<[^>]+>', '', m.group(1)).strip()) if m else ''

    # Extract arXiv ID from meta or paper-link
    arxiv_m = re.search(r'arXiv[:\s]*(\d{4}\.\d{4,5})', block)
    card['id'] = arxiv_m.group(1) if arxiv_m else ''

    # If no arxiv ID, check for other IDs
    if not card['id']:
        link_m = re.search(r'arxiv\.org/abs/(\d{4}\.\d{4,5})', block)
        card['id'] = link_m.group(1) if link_m else ''

    # Description (first <p> after meta)
    # Get all <p> content (excluding those inside mini-diagram or insight)
    desc_m = re.search(r'</div>\s*<p>(.*?)</p>', block, re.DOTALL)
    card['description'] = htmlmod.unescape(re.sub(r'<[^>]+>', '', desc_m.group(1)).strip()) if desc_m else ''

    # Mini diagram
    diag_m = re.search(r'<div class="mini-diagram">(.*?)</div>', block, re.DOTALL)
    card['diagram'] = diag_m.group(1).strip() if diag_m else ''

    # Insight
    ins_m = re.search(r'<div class="insight">(.*?)</div>', block, re.DOTALL)
    card['insight'] = htmlmod.unescape(re.sub(r'<[^>]+>', '', ins_m.group(1)).strip()) if ins_m else ''

    # Paper link URL
    link_m = re.search(r'<a href="(https://[^"]+)"[^>]*class="paper-link"', block)
    card['url'] = link_m.group(1) if link_m else ''

    # Extract authors and institution from meta
    # Meta format: "Institution | Author et al. | arXiv:XXXX.XXXXX"
    # or "Institution | Author et al."
    meta = card['meta']
    parts = [p.strip() for p in meta.split('|')]
    card['institution'] = parts[0] if len(parts) >= 1 else ''
    card['authors'] = parts[1] if len(parts) >= 2 else ''

    # Determine section context from the nearest h3 before the card
    # (This will be done at a higher level)

    return card

def extract_timelines(page_id, htm):
    """Extract timeline items from HTML."""
    items = []
    # Find timeline-item blocks
    pattern = r'<div class="timeline-item">(.*?)</div>\s*\n\s*(?=<div class="timeline-item"|</div>)'

    item_starts = [m.start() for m in re.finditer(r'<div class="timeline-item">', htm)]

    for start in item_starts:
        depth = 0
        pos = start
        end = start
        while pos < len(htm):
            if htm[pos:pos+4] == '<div':
                depth += 1
            elif htm[pos:pos+6] == '</div>':
                depth -= 1
                if depth == 0:
                    end = pos + 6
                    break
            pos += 1

        block = htm[start:end]

        year_m = re.search(r'<span class="year"[^>]*>(.*?)</span>', block)
        title_m = re.search(r'<h4>(.*?)</h4>', block, re.DOTALL)
        desc_m = re.search(r'<p>(.*?)</p>', block, re.DOTALL)

        item = {
            'page': page_id,
            'year': htmlmod.unescape(year_m.group(1).strip()) if year_m else '',
            'title': htmlmod.unescape(title_m.group(1).strip()) if title_m else '',
            'description': htmlmod.unescape(re.sub(r'<[^>]+>', '', desc_m.group(1)).strip()) if desc_m else ''
        }
        items.append(item)

    return items

def extract_sections(page_id, htm):
    """Extract section structure: h2/h3 headings and which cards belong to each."""
    sections = []
    # Find all h2 and h3 headings
    headings = list(re.finditer(r'<(h[23])>(.*?)</\1>', htm, re.DOTALL))

    for i, m in enumerate(headings):
        level = m.group(1)
        title = htmlmod.unescape(re.sub(r'<[^>]+>', '', m.group(2)).strip())
        start = m.end()
        end = headings[i+1].start() if i+1 < len(headings) else len(htm)

        section_html = htm[start:end]

        # Check if this section has card-grid
        has_cards = '<div class="card-grid">' in section_html or '<div class="card-grid' in section_html
        has_timeline = '<div class="timeline">' in section_html

        # Generate section id from title
        section_id = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff]+', '-', title).strip('-').lower()

        sections.append({
            'page': page_id,
            'level': level,
            'title': title,
            'id': section_id,
            'has_cards': has_cards,
            'has_timeline': has_timeline
        })

    return sections

def extract_citations_from_p7(htm):
    """Extract citation edges from p7's E[] array."""
    # Find the E array
    e_m = re.search(r'const E=\[(.*?)\];', htm, re.DOTALL)
    if not e_m:
        return []

    edges_str = e_m.group(1)
    # Parse ['source','target'] pairs
    pairs = re.findall(r"\['([^']+)','([^']+)'\]", edges_str)
    return [{'source': s, 'target': t} for s, t in pairs]

def extract_p7_nodes(htm):
    """Extract paper nodes from p7's P[] array for foundation papers."""
    nodes = []
    # Find each node definition
    pattern = r"\{id:'([^']+)',s:'([^']*)',t:'([^']*)',a:'([^']*)',o:'([^']*)',y:(\d+),d:'([^']*)'(?:,f:1)?(?:,l:'([^']*)')?\}"
    for m in re.finditer(pattern, htm):
        node = {
            'id': m.group(1),
            'shortTitle': m.group(2),
            'topic': m.group(3),
            'authors': m.group(4),
            'institution': m.group(5),
            'year': int(m.group(6)),
            'description': m.group(7),
            'foundation': bool(re.search(r",f:1", m.group(0))),
            'arxivLink': m.group(8) or ''
        }
        nodes.append(node)
    return nodes

def assign_sections_to_cards(page_id, htm, cards):
    """Assign section IDs to cards based on their position in the HTML."""
    # Build a list of (position, section_id) from h2/h3 headings
    headings = []
    for m in re.finditer(r'<(h[23])>(.*?)</\1>', htm, re.DOTALL):
        title = htmlmod.unescape(re.sub(r'<[^>]+>', '', m.group(2)).strip())
        section_id = re.sub(r'[^a-zA-Z0-9]+', '-', title).strip('-').lower()
        headings.append((m.start(), section_id))

    for card in cards:
        if not card.get('title'):
            continue
        # Find card position in HTML
        card_pos = htm.find(card['title'][:30])
        if card_pos < 0:
            card['section'] = 'unknown'
            continue

        # Find the most recent heading before this card
        section = 'default'
        for pos, sid in headings:
            if pos < card_pos:
                section = sid
            else:
                break
        card['section'] = section

def main():
    pages = {
        'p1': 'p1-vla.html',
        'p2': 'p2-wam.html',
        'p3': 'p3-rl-sim2real.html',
        'p4': 'p4-diffusion.html',
        'p5': 'p5-hybrid.html',
        'p6': 'p6-unitree.html'
    }

    all_cards = []
    all_timelines = []
    all_sections = []
    seen_ids = set()

    for page_id, filename in pages.items():
        htm = read(filename)

        cards = extract_cards(page_id, htm)
        assign_sections_to_cards(page_id, htm, cards)

        # Deduplicate cards by ID (some appear on multiple pages)
        for card in cards:
            cid = card.get('id', '')
            if cid and cid in seen_ids:
                # Add this page to existing card
                for existing in all_cards:
                    if existing.get('id') == cid:
                        if page_id not in existing['pages']:
                            existing['pages'].append(page_id)
                        break
            else:
                if cid:
                    seen_ids.add(cid)
                all_cards.append(card)

        timelines = extract_timelines(page_id, htm)
        all_timelines.extend(timelines)

        sections = extract_sections(page_id, htm)
        all_sections.extend(sections)

    # Extract citations from p7
    p7_htm = read('p7-citation-graph.html')
    citations = extract_citations_from_p7(p7_htm)
    p7_nodes = extract_p7_nodes(p7_htm)

    # Build p7 node lookup by shortTitle (lowercase) for matching no-ID cards
    p7_by_short = {}
    for n in p7_nodes:
        key = n['shortTitle'].lower().replace(' ', '')
        p7_by_short[key] = n

    # Match no-ID HTML cards to p7 nodes by title prefix
    for card in all_cards:
        if not card.get('id'):
            # Try matching card title prefix to p7 shortTitle
            title_prefix = card['title'].split(':')[0].strip() if ':' in card['title'] else card['title'].split('—')[0].strip()
            key = title_prefix.lower().replace(' ', '').replace('₀', '0').replace('π', 'pi')
            # Also try with unicode normalization
            for p7key, node in p7_by_short.items():
                norm_p7 = p7key.replace('₀', '0')
                if key == norm_p7 or key == p7key:
                    card['id'] = node['id']
                    break

    # Merge p7 node data into cards (for foundation papers that don't have cards)
    card_ids = {c.get('id', '') for c in all_cards if c.get('id')}
    foundation_papers = []
    for node in p7_nodes:
        if node['id'] not in card_ids:
            foundation_papers.append({
                'id': node['id'],
                'title': node['shortTitle'],
                'shortTitle': node['shortTitle'],
                'meta': f"{node['institution']} | {node['authors']}",
                'institution': node['institution'],
                'authors': node['authors'],
                'description': node['description'],
                'topic': node['topic'],
                'year': node['year'],
                'foundation': True,
                'tags': [],
                'diagram': '',
                'insight': '',
                'url': f"https://arxiv.org/abs/{node['arxivLink']}" if node['arxivLink'] else '',
                'pages': [],
                'section': 'foundation'
            })

    # Add topic info to cards from p7 nodes
    p7_node_map = {n['id']: n for n in p7_nodes}
    for card in all_cards:
        cid = card.get('id', '')
        if cid in p7_node_map:
            node = p7_node_map[cid]
            card['topic'] = node['topic']
            card['shortTitle'] = node['shortTitle']
        else:
            # Infer topic from page
            page = card['pages'][0] if card['pages'] else ''
            topic_map = {'p1':'vla','p2':'wam','p3':'rl','p4':'diff','p5':'hybrid','p6':'unitree'}
            card['topic'] = topic_map.get(page, 'unknown')
            # Generate short title from full title
            card['shortTitle'] = card['title'].split(':')[0].strip() if ':' in card['title'] else card['title'][:20]

    # Build final JSON
    result = {
        'papers': all_cards + foundation_papers,
        'sections': all_sections,
        'timeline': all_timelines,
        'citations': citations
    }

    out_path = os.environ.get('OUTPUT_PATH', os.path.join(BASE, 'papers.json'))
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # Also generate papers.js for file:// protocol compatibility
    js_path = os.path.join(BASE, 'papers.js')
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write('window.SURVEY_DATA = ')
        json.dump(result, f, ensure_ascii=False, indent=2)
        f.write(';\n')

    # Print stats
    print(f"Cards extracted: {len(all_cards)}")
    print(f"Foundation papers: {len(foundation_papers)}")
    print(f"Timeline items: {len(all_timelines)}")
    print(f"Sections: {len(all_sections)}")
    print(f"Citations: {len(citations)}")
    print(f"Total papers: {len(all_cards) + len(foundation_papers)}")
    print(f"Written to: {out_path}")

if __name__ == '__main__':
    main()
