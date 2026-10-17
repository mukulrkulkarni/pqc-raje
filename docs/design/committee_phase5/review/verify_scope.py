from pathlib import Path
import subprocess,hashlib,json
root=Path(__file__).resolve().parents[4]
folder=Path(__file__).parent
manifest=json.loads((folder/'manifest.json').read_text())
for name,digest in manifest['files'].items():
    assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest
    assert hashlib.sha256((folder/'snapshot'/name).read_bytes()).hexdigest()==digest
old=subprocess.check_output(['git','show','HEAD:electre3/credibility.py'],cwd=root)
current=(root/'electre3/credibility.py').read_bytes()
assert old.replace(b'\r\n',b'\n')==current.replace(b'\r\n',b'\n')
result={'snapshot_hashes':'PASS; all three match live and manifest',
        'snapshot_files':[p.relative_to(folder).as_posix() for p in (folder/'snapshot').rglob('*') if p.is_file()],
        'credibility_finding_scope':'Pre-existing: credibility.py content unchanged from HEAD, not introduced by N1',
        'gate_results':{'Scientific':'NEEDS WORK','Engineering':'APPROVED','Security':'APPROVED','UI_UX':'APPROVED'},
        'unverified':'Browser interaction, rendered width and exact baseline alignment'}
(folder/'consolidated.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
