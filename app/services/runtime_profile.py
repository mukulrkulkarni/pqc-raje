"""Conservative local runtime profile for the approved /app feasibility gate."""
from electre3.runtime import BenchmarkSample, RuntimeModel

# Baseline records represent complete adapter work on the supported process profile.
# The model uses the slowest normalized p95 coefficient and a 1.25 safety factor.
APP_RUNTIME_MODEL = RuntimeModel((
    BenchmarkSample(100, 2, 1000, 0.25, 0.02),
    BenchmarkSample(1000, 8, 1000, 2.0, 0.05),
))
