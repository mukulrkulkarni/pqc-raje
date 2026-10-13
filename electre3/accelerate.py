"""Optional Numba acceleration for ELECTRE III."""
try:
    from numba import jit
    HAS_NUMBA = True
except ImportError:
    HAS_NUMBA = False
    jit = None

if HAS_NUMBA:
    @jit(nopython=True, cache=True)
    def _concordance_numba(diff, q, p, out):
        B1, B2, C = diff.shape
        for i in range(B1):
            for j in range(B2):
                for k in range(C):
                    d = diff[i, j, k]
                    if d >= -q[k]: out[i, j, k] = 1.0
                    elif d <= -p[k]: out[i, j, k] = 0.0
                    else:
                        denom = p[k] - q[k]
                        out[i, j, k] = 1.0 if denom == 0 else (d + p[k]) / denom

    @jit(nopython=True, cache=True)
    def _discordance_numba(diff, p, v, out):
        B1, B2, C = diff.shape
        for i in range(B1):
            for j in range(B2):
                for k in range(C):
                    d = diff[i, j, k]
                    if d >= -p[k]: out[i, j, k] = 0.0
                    elif d <= -v[k]: out[i, j, k] = 1.0
                    else:
                        denom = v[k] - p[k]
                        out[i, j, k] = 1.0 if denom == 0 else (-d - p[k]) / denom
else:
    _concordance_numba = None
    _discordance_numba = None
