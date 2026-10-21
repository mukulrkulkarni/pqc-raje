# Config Module

This document describes the configuration dataclasses in `electre3/config.py`.

## 1. Purpose

The config module defines data structures for ELECTRE III parameters.
It validates inputs before expensive computations begin.

## 2. CriterionConfig

### 2.1 Definition

```python
@dataclass
class CriterionConfig:
    name: str
    weight: float
    q: float  # indifference threshold
    p: float  # preference threshold
    v: float  # veto threshold
    maximize: bool = True
```

### 2.2 Threshold Semantics

| Threshold | Symbol | Meaning |
|-----------|--------|---------|
| Indifference | q | Differences ≤ q are negligible |
| Preference | p | Differences ≥ p show clear preference |
| Veto | v | Differences ≥ v override concordance |

### 2.3 Validation Rules

The thresholds must satisfy:

```
0 ≤ q ≤ p ≤ v
```

- **q ≥ 0**: Indifference cannot be negative
- **p ≥ q**: Preference threshold includes indifference zone
- **v ≥ p**: Veto threshold includes preference zone

### 2.4 Weight Constraint

Weight must be positive:

```
weight > 0
```

Weights are later normalized to sum to 1.0.

## 3. ComputeConfig

### 3.1 Definition

```python
@dataclass
class ComputeConfig:
    block_size: int = 1000
    use_numba: bool = True
    seed: Optional[int] = None
```

### 3.2 Block Size

Controls memory vs. computation trade-off:

| Block Size | Memory per Block | Suitable For |
|------------|------------------|--------------|
| 500 | ~20 MB | Low-RAM systems |
| 1000 | ~80 MB | Default |
| 2000 | ~320 MB | High-RAM systems |

### 3.3 Validation

Block size must be at least 1:

```
block_size ≥ 1
```

## 4. Weight Normalization

### 4.1 Formula

```
w_i^norm = w_i / Σ w_j
```

### 4.2 Function

```python
def normalize_weights(criteria: list[CriterionConfig]) -> list[float]
```

**Input**: List of criterion configurations.
**Output**: List of normalized weights summing to 1.0.

### 4.3 Example

```python
criteria = [
    CriterionConfig("Price", weight=3, q=5, p=10, v=20),
    CriterionConfig("Quality", weight=2, q=3, p=8, v=15),
]
weights = normalize_weights(criteria)
# weights = [0.6, 0.4]
```

## 5. Error Handling

### 5.1 Invalid Threshold Order

```python
CriterionConfig("X", 1, q=10, p=5, v=20)
# ValueError: p must be >= q, got p=5, q=10
```

### 5.2 Zero Weight

```python
CriterionConfig("X", weight=0, q=1, p=2, v=3)
# ValueError: weight must be > 0, got 0
```

### 5.3 Invalid Block Size

```python
ComputeConfig(block_size=0)
# ValueError: block_size must be >= 1, got 0
```

## 6. Determinism Note

Configuration is deterministic. The same inputs always produce the same validated objects. The optional `seed` parameter ensures reproducible tie-breaking in ranking.
