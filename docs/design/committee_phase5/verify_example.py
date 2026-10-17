"""Check design example against current implementation; no production changes."""
import json
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from electre3.concordance import partial_concordance, global_concordance
from electre3.discordance import discordance
from electre3.credibility import credibility
A, B = np.array([10., 5., 7.]), np.array([8., 7., 6.])
q, p, v, w = np.ones(3), np.full(3, 3.), np.full(3, 6.), np.array([.5, .3, .2])
report = {}
for label, diff, expected in [('A_to_B', (A-B)[None,None,:], .85), ('B_to_A',(B-A)[None,None,:],.75)]:
    c = partial_concordance(diff, q, p)
    C = global_concordance(c, w)
    d = discordance(diff, p, v)
    S = credibility(C,d)
    assert np.allclose(S,expected)
    report[label] = {'diff':diff.tolist(),'partial':c.tolist(),'global':C.tolist(),'discordance':d.tolist(),'credibility':S.tolist()}
x = np.array([[[-1.]]])
one = np.array([1.])
assert partial_concordance(x,one,one).item() == 1.
assert discordance(x,one,one).item() == 1.
report['boundary_checks'] = 'PASS: q=p at equality gives c=1; p=v at equality gives d=1.'
Path(__file__).with_name('example_results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
