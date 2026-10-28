import json
from pathlib import Path
p=json.loads(Path('out/w1-link-inventory.json').read_text(encoding='utf-8'))
lines=['BROKEN']
for x in p['references']:
    if x['classification']=='broken': lines.append(f"{x['source']} | served={x['served']} | target={x['target']} | {x['evidence']}")
lines += ['', 'PLANNED/HISTORICAL']
for x in p['references']:
    if x['classification'] in {'planned','historical'}: lines.append(f"{x['classification']} | {x['source']} | {x['target']} | {x['evidence']}")
lines += ['', 'PROBES'] + [json.dumps(x, sort_keys=True) for x in p['probes']]
Path('out/w1-link-summary.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('\n'.join(lines))
