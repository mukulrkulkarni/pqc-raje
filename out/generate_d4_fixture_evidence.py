"""Generate deterministic D4 fixture evidence; run from repository root."""
import csv, hashlib, json, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import numpy as np
from electre3.data import load_input
from electre3.shared import compute_validated_ranking, validate_criteria
from electre3.block import compute_block

FIXTURES = ROOT / "examples" / "d4_phase2"
OUT = ROOT / "out"
NAMES = ["Quantum-Vulnerability", "Migration-Complexity", "Business-Criticality", "Data-Sensitivity"]
THRESHOLDS = {"q": 0.03, "p": 0.12, "v": 0.35}
MATRICES = {
    "scenario-3": [("A-001 / 10.0.0.5", [.88,.36,.71,.58]), ("A-002 / 10.0.0.9", [.61,.78,.92,.44]), ("A-003 / 10.0.0.12", [.72,.55,.63,.90])],
    "scenario-5": [("B-001 / 10.0.1.5", [.92,.31,.55,.47]), ("B-002 / 10.0.1.8", [.64,.71,.94,.52]), ("B-003 / 10.0.1.13", [.77,.48,.72,.85]), ("B-004 / 10.0.1.21", [.54,.89,.83,.66]), ("B-005 / 10.0.1.34", [.81,.58,.68,.73])],
    "scenario-8": [("C-001 / 10.0.2.3", [.91,.29,.62,.43]), ("C-002 / 10.0.2.7", [.62,.74,.95,.54]), ("C-003 / 10.0.2.11", [.75,.51,.70,.91]), ("C-004 / 10.0.2.19", [.56,.87,.84,.68]), ("C-005 / 10.0.2.28", [.83,.57,.67,.76]), ("C-006 / 10.0.2.39", [.69,.66,.79,.63]), ("C-007 / 10.0.2.44", [.48,.93,.88,.58]), ("C-008 / 10.0.2.52", [.86,.42,.59,.82])],
    "exact-tie": [("T-001 / 10.0.3.1", [.71,.54,.81,.66]), ("T-002 / 10.0.3.2", [.71,.54,.81,.66]), ("T-003 / 10.0.3.3", [.49,.86,.58,.40])],
    "near-tie": [("N-001 / 10.0.4.1", [.71,.54,.81,.66]), ("N-002 / 10.0.4.2", [.710000000000001,.54,.81,.66]), ("N-003 / 10.0.4.3", [.49,.86,.58,.40])],
}
WEIGHTS = {"balanced": [.25,.25,.25,.25], "business-criticality-priority": [.15,.15,.55,.15], "data-sensitivity-priority": [.15,.15,.15,.55]}
SCENARIO_FILES = {"scenario-3": ["balanced"], "scenario-5": ["balanced", "business-criticality-priority"], "scenario-8": ["balanced", "data-sensitivity-priority"], "exact-tie": ["balanced"], "near-tie": ["balanced"]}
def criteria(weights):
    return [{"name": n, "weight": w, **THRESHOLDS, "maximize": True} for n,w in zip(NAMES,weights)]
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def write_fixture(name, rows):
    directory = FIXTURES / name; directory.mkdir(parents=True, exist_ok=True)
    with (directory / "matrix_headered.csv").open("w", newline="", encoding="utf-8") as f:
        csv.writer(f, lineterminator="\n").writerows([["Asset ID / IP", *NAMES], *[[identifier, *scores] for identifier, scores in rows]])
    for variant in SCENARIO_FILES[name]:
        (directory / f"criteria_{variant}.json").write_text(json.dumps(criteria(WEIGHTS[variant]), indent=2) + "\n", encoding="utf-8")
def run(name, variant):
    directory=FIXTURES/name; cp=directory/f"criteria_{variant}.json"; matrix=directory/"matrix_headered.csv"
    cs=json.loads(cp.read_text(encoding="utf-8")); validated=validate_criteria(cs); data=load_input(matrix, validated)
    result=compute_validated_ranking(data.scores, cs, 2, identifiers=data.identifiers)
    q=np.array([x["q"] for x in cs]); p=np.array([x["p"] for x in cs]); v=np.array([x["v"] for x in cs]); w=np.array([x["weight"] for x in cs]);
    credibility=compute_block(data.scores,data.scores,q,p,v,w,True,np.ones(4))
    command=[sys.executable,"-m","electre3.cli",str(matrix.relative_to(ROOT)),str(cp.relative_to(ROOT)),"-y","-b","2"]
    proc=subprocess.run(command,cwd=ROOT,text=True,capture_output=True,check=False)
    if proc.returncode: raise RuntimeError(proc.stderr)
    return {"matrix":str(matrix.relative_to(ROOT)).replace("\\","/"),"criteria":str(cp.relative_to(ROOT)).replace("\\","/"),"matrix_sha256":sha(matrix),"criteria_sha256":sha(cp),"cli_command":"python -m electre3.cli " + str(matrix.relative_to(ROOT)).replace("\\\\", "\\\\") + " " + str(cp.relative_to(ROOT)).replace("\\\\", "\\\\") + " -y -b 2","cli_exit_code":proc.returncode,"cli_stdout":proc.stdout,"ranking":[data.identifiers[int(i)] for i in result.ranking],"outflow":[float(x).hex() for x in credibility.sum(axis=1)],"inflow":[float(x).hex() for x in credibility.sum(axis=0)],"net_flow":[float(x).hex() for x in result.net_flow],"credibility":[[float(x).hex() for x in row] for row in credibility]}
def main():
    for name, rows in MATRICES.items(): write_fixture(name,rows)
    runs={f"{name}/{variant}":run(name,variant) for name in MATRICES for variant in SCENARIO_FILES[name]}
    tie=runs["exact-tie/balanced"]["net_flow"]; near=runs["near-tie/balanced"]["net_flow"]
    assert tie[0] == tie[1], tie
    assert near[0] != near[1], near
    payload={"schema_version":1,"method":"ELECTRE III credibility with raw net-flow ranking","precision":"binary64 hexadecimal float strings preserve full raw-flow precision","thresholds":THRESHOLDS,"criteria":criteria(WEIGHTS["balanced"]),"runs":runs,"assertions":{"exact_tie":{"indices":[0,1],"equal_net_flow":True},"near_tie":{"indices":[0,1],"unequal_net_flow":True}},"generator":"out/generate_d4_fixture_evidence.py"}
    target=OUT/"d4-fixture-evidence.json"; target.write_text(json.dumps(payload,indent=2)+"\n",encoding="utf-8")
    print(target.relative_to(ROOT)); print("exact-tie", tie); print("near-tie", near)
if __name__ == "__main__": main()
