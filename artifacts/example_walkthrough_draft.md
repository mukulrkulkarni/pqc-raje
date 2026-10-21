## Example Walkthrough

This walkthrough separates current CLI behavior from the approved web target. It uses these criteria: `Quantum-Vulnerability`, `Migration-Complexity`, `Business-Criticality`, and `Data-Sensitivity`.

### 1. Inputs and validation ownership

The performance matrix is `G` with shape `(N, C)`: `N` alternatives and `C` criteria. The criteria file is a top-level JSON list. Each item contains `name`, `weight`, `q`, `p`, `v`, and `maximize`; the approved web target allows at most eight criteria.

Current core validation requires positive finite weights, finite thresholds, and `0 ≤ q ≤ p ≤ v`. The current CLI can supply defaults for missing criterion fields and does not enforce a boolean `maximize`, an eight-criterion limit, weights summing to one, or score bounds `[0,1]`. The approved web target must enforce required fields, boolean `maximize`, at most eight criteria, complete finite matrix values, normalized scores in `[0,1]`, and weights summing to `1`.

Example `criteria.json`:

```json
[
  {"name":"Quantum-Vulnerability","weight":0.25,"q":0.02,"p":0.08,"v":0.25,"maximize":false},
  {"name":"Migration-Complexity","weight":0.25,"q":0.03,"p":0.10,"v":0.30,"maximize":false},
  {"name":"Business-Criticality","weight":0.25,"q":0.02,"p":0.07,"v":0.20,"maximize":true},
  {"name":"Data-Sensitivity","weight":0.25,"q":0.02,"p":0.07,"v":0.20,"maximize":true}
]
```

These example weights sum to `1.0`. The threshold and matrix values are illustrative inputs, not claimed computed outputs.

### 2. CSV and identifier handling

The current CLI accepts numeric-only CSV, `.npy`, `.npz`, and, when the optional dependency is installed, `.parquet`. A direct CLI CSV has no header or identifier column; numeric columns follow the JSON criterion order:

```csv
0.30,0.20,0.80,0.70
0.40,0.10,0.60,0.90
0.20,0.30,0.70,0.60
```

For a headered source containing identifier content such as `A-001 / 10.0.0.5`, convert it first:

```csv
Asset ID / IP,Quantum-Vulnerability,Migration-Complexity,Business-Criticality,Data-Sensitivity
A-001 / 10.0.0.5,0.30,0.20,0.80,0.70
A-002 / 10.0.0.9,0.40,0.10,0.60,0.90
A-003 / 10.0.0.12,0.20,0.30,0.70,0.60
```

```bash
python scripts/convert_matrix_csv.py matrix_with_ids.csv matrix.npy --has-header --id-col "Asset ID / IP"
```

The converter produces the numeric matrix consumed by the CLI. Keep the identifier mapping separately so ranking indices can be mapped back to `Asset ID / IP` values.

For the web target, headerless input uses the display label `Asset ID` for its first column and JSON criterion names for the remaining labels. Headered input uses its identifier header after validation; its identifier values may contain the user-facing form `Asset ID / IP`. Headered criterion names must match the JSON names in order.

### 3. Run the current CLI

```bash
python -m electre3.cli matrix_file criteria_file [-o OUTPUT] [-b BLOCK_SIZE] [-y] [-q]
```

Example:

```bash
python -m electre3.cli matrix.npy criteria.json -b 256 -q -o results.npy
```

Here `-b 256` is an integer block size. Without `-o`, the CLI prints the first 10 ranking indices and reports how many remain. With `-o results.npy`, it uses `numpy.save` and saves ranking indices only; it does not print the ranking or save identifiers or net-flow scores. The current CLI run path does not print or save `accumulator.net_flow()`. The `-q` option suppresses status and save messages but does not suppress prompts; add `-y` for a non-interactive run.

### 4. Blockwise ELECTRE III computation

For alternatives `a` and `b`—objects, not criteria—direction-adjust each criterion before comparison:

\[
g'_j(x)=\begin{cases}g_j(x),&maximize_j=true\\-g_j(x),&maximize_j=false\end{cases},\qquad diff_j(a,b)=g'_j(a)-g'_j(b).
\]

`B1` and `B2` are row and column groups of alternatives in one block pair. Pairwise criterion intermediates have shape `(B1, B2, C)`; the credibility block has shape `(B1, B2)`.

Partial concordance uses inclusive boundaries:

\[
c_j=\begin{cases}1,&diff_j\ge-q_j\\0,&diff_j\le-p_j\\(diff_j+p_j)/(p_j-q_j),&-p_j<diff_j<-q_j\end{cases}.
\]

The implementation checks the full-concordance branch first. Therefore, when `q=p`, an overlapping boundary is classified as `c_j=1` whenever `diff_j ≥ -q_j`.

Discordance uses:

\[
d_j=\begin{cases}1,&diff_j\le-v_j\\0,&diff_j\ge-p_j\\(-diff_j-p_j)/(v_j-p_j),&-v_j<diff_j<-p_j\end{cases}.
\]

The implementation checks the full-veto branch first. Therefore, when `p=v`, an overlapping boundary is classified as `d_j=1` whenever `diff_j ≤ -v_j`.

Global concordance uses normalized weights. If the input weights are `w_j`, the core computes `\hat w_j=w_j/Σ_k w_k` and then:

\[
C_{ab}=\sum_j\hat w_j c_j(a,b).
\]

Credibility starts at `C_ab` and applies the implemented reductions:

\[
S(a,b)=C_{ab}\prod_{j:d_j>C_{ab}}\frac{1-d_j}{1-C_{ab}}.
\]

If any `d_j ≥ 1`, the implementation sets `S(a,b)=0`. If `C_ab=1` and no full veto occurs, it avoids division by zero and retains credibility `1`.

### 5. Net-flow ranking and current versus target behavior

The accumulator computes raw net flow without dividing by `N−1`:

\[
\Phi(a)=\sum_{b\ne a}S(a,b)-\sum_{b\ne a}S(b,a).
\]

The ranking sorts `Φ(a)` descending. Equal scores are ties; their relative order is not guaranteed.

The current CLI performs blockwise computation and outputs ranking indices. The approved web target adds preview validation, the header display policy, normalized `[0,1]` scores, weights summing to `1`, top-10 display with scores, and downloads. CLI/web equivalence is a target contract only after both paths use the same validated inputs, configuration, and canonical serializers. The example values above are not computed ranking outputs.
