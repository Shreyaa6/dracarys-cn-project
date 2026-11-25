#!/usr/bin/env python3
"""Offline evidence, links, source syntax and secret-boundary validation."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit
import ast, hashlib, json, re, sys
ROOT = Path(__file__).resolve().parents[1]
errors = []
checks = 0

def check(ok, message):
    global checks
    checks += 1
    if not ok:
        errors.append(message)

class Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.links = []
    def handle_starttag(self, tag, attrs):
        self.links.extend(v for k, v in attrs if k in ('href', 'src') and v)

def link_check(source, link):
    link = link.strip('<>')
    parsed = urlsplit(link)
    if parsed.scheme or link.startswith('#') or not parsed.path:
        return
    target = source.parent / unquote(parsed.path)
    check(target.exists(), f'Missing link in {source.relative_to(ROOT)}: {link}')

phase2 = ROOT / 'evidence/phase2'
manifest = json.loads((phase2 / 'manifest.json').read_text())
check({e['id'] for e in manifest} == {f'E{i:03}' for i in range(1, 58)}, 'Evidence ID inventory')
check(len(manifest) == 57, 'Evidence count')
for e in manifest:
    p = phase2 / e['path']
    check(p.is_file(), f'Missing {e["id"]}')
    if p.is_file():
        check(hashlib.sha256(p.read_bytes()).hexdigest() == e['sha256'], f'Hash {e["id"]}')
        check(p.stat().st_size == e['size_bytes'], f'Size {e["id"]}')
    check((phase2 / e['ocr']).is_file(), f'OCR {e["id"]}')
    check(bool(e['original_filename']), f'Original name {e["id"]}')
byid = {e['id']: e for e in manifest}
check(byid['E036']['sha256'] == byid['E037']['sha256'], 'Duplicate mapping')
check(byid['E037']['duplicate_of'] == 'E036', 'Duplicate provenance')
for line in (phase2 / 'SHA256SUMS.txt').read_text().splitlines():
    digest, name = line.split(None, 1)
    p = phase2 / name.lstrip('*')
    check(p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest() == digest, f'Checksum {name}')
for p in ROOT.rglob('*'):
    if not p.is_file() or '.git' in p.parts:
        continue
    if p.suffix == '.md':
        # Ignore shell/code examples, then inspect actual Markdown links/images.
        txt = re.sub(r'```.*?```', '', p.read_text(), flags=re.S)
        for link in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', txt):
            link_check(p, link)
    elif p.suffix == '.html':
        parser = Links(); parser.feed(p.read_text())
        for link in parser.links:
            link_check(p, link)
    if p.suffix == '.py':
        try: ast.parse(p.read_text(), filename=str(p))
        except SyntaxError as exc: errors.append(str(exc))
    check(p.suffix.lower() not in {'.key', '.pem', '.p12', '.pfx', '.keylog'}, f'Private artifact {p.name}')
    if p.suffix.lower() in {'.md', '.txt', '.py', '.conf', '.json', '.html', '.crt', '.rules', '.cnf'}:
        data = p.read_text(errors='replace')
        check(not re.search(r'-----BEGIN (?:RSA |EC |OPENSSH |ENCRYPTED )?PRIVATE KEY-----', data), f'Private key material {p.name}')
check((ROOT/'docs/phase2-report.pdf').is_file(), 'Report PDF')
if errors:
    print('\n'.join(errors)); sys.exit(1)
print(f'PASS: {checks} offline checks; 57 evidence IDs, hashes, links/gallery, Python syntax and private-key boundaries.')
print('No live LAN, host firewall, certificate deployment, challenge or viva result is implied.')
