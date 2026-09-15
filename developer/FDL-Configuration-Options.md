# Force Directed Layout — Configuration Options

## Current Configuration (Baseline)

```ini
[Arrange]
damping = 0.6
springLength = 275
maxIterations = 480
attractionForce = 0.1
repulsionForce = 1100

[Randomize]
minMaxX = 100,1000
minMaxY = -100,1000

[EarlyExit]
minimumTotalDisplacement = 10
stopCount = 15
```

| Metric | Value |
|--------|-------|
| Overlaps | **95** |
| Min distance between nodes | 40.2px |
| Avg edge length | 146.4px |
| Bounding box | 315 × 310px |
| Aspect ratio | 1.02 |

---

## Option A — Best Overall (Widest Spread)

```ini
[Arrange]
damping = 0.6
springLength = 500
maxIterations = 500
attractionForce = 0.05
repulsionForce = 15000

[Randomize]
minMaxX = 100,1000
minMaxY = -100,1000

[EarlyExit]
minimumTotalDisplacement = 10
stopCount = 15
```

| Metric | Value |
|--------|-------|
| Overlaps | **2** (down from 95) |
| Min distance between nodes | 117.7px |
| Avg edge length | 384.2px |
| Edge length std dev | 124.3px |
| Bounding box | 1036 × 893px |
| Aspect ratio | 1.16 (near-square, landscape-leaning) |

---

## Option B — Tighter, Most Uniform Edges

```ini
[Arrange]
damping = 0.6
springLength = 300
maxIterations = 500
attractionForce = 0.1
repulsionForce = 12000

[Randomize]
minMaxX = 100,1000
minMaxY = -100,1000

[EarlyExit]
minimumTotalDisplacement = 10
stopCount = 15
```

| Metric | Value |
|--------|-------|
| Overlaps | **6** |
| Min distance between nodes | 106.2px |
| Avg edge length | 270.7px |
| Edge length std dev | **48.9px** (most uniform!) |
| Bounding box | 816 × 989px |
| Aspect ratio | 0.83 (slightly portrait) |

---

## Option C — Balanced Landscape

```ini
[Arrange]
damping = 0.6
springLength = 500
maxIterations = 500
attractionForce = 0.1
repulsionForce = 15000

[Randomize]
minMaxX = 100,1000
minMaxY = -100,1000

[EarlyExit]
minimumTotalDisplacement = 10
stopCount = 15
```

| Metric | Value |
|--------|-------|
| Overlaps | **3** |
| Min distance between nodes | 113.4px |
| Avg edge length | 376.3px |
| Edge length std dev | 126.5px |
| Bounding box | 1053 × 943px |
| Aspect ratio | 1.12 |

---

## Parameter Reference

| Parameter | Range | Description |
|-----------|-------|-------------|
| `damping` | 0.1–1.0 | Velocity multiplier per iteration. Lower = slower but more stable convergence. |
| `springLength` | 100–500 | Natural rest length of edges (Hooke's Law). Longer = more spread between connected nodes. |
| `maxIterations` | 100–1000 | Hard cap on algorithm iterations. 500 is typically sufficient. |
| `attractionForce` | 0.1–1.0 | Hooke spring constant. Higher = connected nodes pull together more strongly. |
| `repulsionForce` | 500–15000 | Coulomb constant (`F = -k/r²`). Higher = nodes push apart more aggressively. |
| `minimumTotalDisplacement` | — | Early exit threshold: stop if total displacement falls below this value. |
| `stopCount` | — | Number of consecutive low-displacement iterations before early exit. |
| `minMaxX` | — | Min/max range for initial random X coordinates. **Currently not used — see note below.** |
| `minMaxY` | — | Min/max range for initial random Y coordinates. **Currently not used — see note below.** |

---

## Key Findings

### Root Cause

The `repulsionForce` of **1100** is the primary problem. With 24 nodes (each 150×75px),
the Coulomb repulsion `F = -k/r²` cannot push nodes far enough apart to prevent stacking.
Increasing to **15,000** (the UI slider maximum) is the single most impactful change.

### Hardcoded Initial Randomization

The `minMaxX`/`minMaxY` configuration values in `[Randomize]` are **not currently used**
by the library. In `ForceDirectedLayout.py` line 257, the initial coordinates are hardcoded:

```python
diagramNode.location = Point(x=randint(-50, 50), y=randint(-50, 50))
```

This means all 24 nodes start in a tiny 100×100px area regardless of configured ranges.
Consider uncommenting the configurable range code (lines 251–256) for better initial spread.

---

## Test Diagram

All simulations were run against `FDLTestDiagram.xml` containing:

* **24** UML class nodes (each 150 × 75px)
* **20** inheritance edges
* Deterministic seed: 42

---

## Recommendation

Start with **Option A**. If the layout feels too spread out, try **Option C** (same but
with `attractionForce = 0.1` instead of `0.05`). If you prefer tighter, more uniform edge
lengths at the cost of a few more overlaps, try **Option B**.
