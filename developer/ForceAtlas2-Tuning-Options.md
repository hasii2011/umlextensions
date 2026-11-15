# 0.5 ForceAtlas2 Layout Tuning Options

Reference notes for configuring the Diagrammer Arranger **ForceAtlas2** layout (`networkx.forceatlas2_layout`) for diagrams such as `FDLTestDiagram.xml` (24 classes at `150x75`).

## Key Behavioral Notes (`LayoutAlgorithms.py`)

1. **`Prevent Shape Crowding` collapses layouts:**
   `applyForceAtlas2Layout` passes `max(shape.size.width, shape.size.height)` (`150` px) as `node_size` into `networkx.forceatlas2_layout`. Because NetworkX runs the simulation in a unit-scale coordinate space before `frameScale=50` is applied, pixel-scale `node_size` values overwhelm unit distances and collapse all shapes into a ~`10–30 px` pile. **Uncheck `Prevent Shape Crowding`** and control spacing with **Scaling Ratio** and **Gravity**.
2. **Center (`X`, `Y`) shifts the layout:**
   `_repositionTheShapes` computes:
   - `newX = layoutCenter.x + int(coordinates[0] * 50)`
   - `newY = layoutCenter.y + int(coordinates[1] * 50)`

   Lower `X` and `Y` values (e.g. `500–750` and `400–600`) favor the upper-left portion of the diagram frame while leaving enough margin so negative offsets do not clip past `(0, 0)`.
3. **`Jitter Tolerance`:**
   Values around `0.50–1.00` let the layout settle cleanly instead of oscillating (compared to `3.00`).

---

## Preset 1: Compact (Upper-Left)

Keeps the diagram tight in the upper-left corner. *(If boxes overlap too much, increase `Scaling Ratio` to `1.50`.)*

| Option | Value |
| :--- | :--- |
| **Center X / Y** | `500` / `400` |
| **Maximum Iterations** | `250` |
| **Jitter Tolerance** | `1.00` |
| **Scaling Ratio** | `1.00` |
| **Gravity** | `1.00` |
| **Distributed Action** | Unchecked |
| **Strong Gravity** | Checked |
| **Logarithmic Attraction** | Unchecked |
| **Prevent Shape Crowding** | Unchecked |

---

## Preset 2: Spread Out (Upper-Left, Minimal Overlap)

Gives `150x75` class boxes room to breathe (~`1300x1300 px` span; `X/Y` slightly higher so left/top edges do not clip past `0`). *(Increase `Scaling Ratio` to `2.50–3.00` for even more spacing.)*

| Option | Value |
| :--- | :--- |
| **Center X / Y** | `750` / `600` |
| **Maximum Iterations** | `300` |
| **Jitter Tolerance** | `1.00` |
| **Scaling Ratio** | `2.00` |
| **Gravity** | `0.50` |
| **Distributed Action** | Unchecked |
| **Strong Gravity** | Checked |
| **Logarithmic Attraction** | Unchecked |
| **Prevent Shape Crowding** | Unchecked |

---

## Preset 3: Clustered / Sub-Group Separation (LinLog + Distributed Action)

Highlights distinct inheritance/association groups without pulling high-degree hubs into a single knot:
- **Distributed Action** prevents high-degree classes from dominating the center.
- **Strong Gravity (checked)** keeps disconnected or loosely linked components from flying off-screen (`x < 0` / `y < 0`) when **Logarithmic Attraction (LinLog)** is enabled.
- **Logarithmic Attraction (LinLog)** tightens intra-cluster grouping *(note: NetworkX prints a harmless `invalid value encountered in divide` RuntimeWarning on the diagonal when this is checked; uncheck it if you want a clean console).*

| Option | Value |
| :--- | :--- |
| **Center X / Y** | `600` / `550` |
| **Maximum Iterations** | `300` |
| **Jitter Tolerance** | `1.00` |
| **Scaling Ratio** | `0.80` |
| **Gravity** | `0.50` |
| **Distributed Action** | Checked |
| **Strong Gravity** | Checked |
| **Logarithmic Attraction** | Checked |
| **Prevent Shape Crowding** | Unchecked |
