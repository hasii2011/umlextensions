# Sugiyama Step-by-Step Recording Option (Future Enhancement)

## Context

`umlextensions` already has a `sugiyamaStepByStep` boolean preference (`src/umlextensions/ExtensionsPreferences.py`) and a `SugiyamaGlobals.waitKey()` helper (`src/umlextensions/tools/sugiyama/SugiyamaGlobals.py`). Currently, when `sugiyamaStepByStep` is `True`, `Sugiyama._fixNodesPositions()` pauses after initial left-packed placement and after each `node.balance()` move by popping up a modal `wx.MessageBox` and calling `extensionsFacade.refreshFrame()`.

While this works for basic debugging inside `umldiagrammer`, a modal `MessageBox` blocks forward/backward scrubbing and does not capture intermediate states from earlier phases (such as `levelFind()`, `addVirtualNodes()`, or individual `barycenter()` sweeps).

## Proposed Design: Optional `StepRecorder` / Snapshot Callback

Instead of replacing `SugiyamaGlobals.waitKey()` right away, we can add an optional step-recording callback to `Sugiyama` (e.g., `onStep: Optional[Callable[[SugiyamaStep], None]] = None`) that defaults to `None` so `ToolSugiyama` behaves identically when not recording.

### What `SugiyamaStep` Would Capture

Mirroring `DcelStep` in the `orthogonal` project, each immutable `SugiyamaStep` snapshot would record:

- **Phase / Operation Name**: e.g. `initial`, `levelFind`, `addVirtualNodes`, `barycenter_down`, `barycenter_up`, `addNonHierarchicalNodes`, `packLeft`, `balanceMove`, `fixLinksPositions`.
- **Description**: Human-readable summary of what changed in that step (e.g., which level was swept or which node moved).
- **Levels Snapshot**: Ordered node IDs/names per level (`RealSugiyamaNode` and `VirtualSugiyamaNode`), including each node's `index`, `level`, and `barycenter`.
- **Node Positions & Sizes**: `(x, y)` and `(width, height)` for every real and virtual node at that instant.
- **Link Control Points**: Anchor coordinates and intermediate virtual-node control points for each `SugiyamaLink`.
- **Metrics**: Hierarchical edge-crossing count (`_getNbIntersectAll()`), total virtual nodes, and number of nodes moved.

### Emission Points in `Sugiyama`

1. After `createInterfaceUmlShapeLayout()` (initial state).
2. After `levelFind()` (initial level assignments).
3. After `addVirtualNodes()` (virtual nodes inserted for multi-level links).
4. Inside `barycenter()` after each `_downBarycenterLevel()` / `_upBarycenterLevel()` pass (showing crossing count changes).
5. After `addNonHierarchicalNodes()`.
6. Inside `_fixNodesPositions()` after left-packing and after each `node.balance()` move (as a non-blocking alternative to `SugiyamaGlobals.waitKey()`).
7. After `_fixLinksPositions()` (final anchor and control-point placement).

## Benefits for the Sugiyama Visualizer

- Enables **Prev / Next / Reset** scrubbing and a step-history slider in the visualizer without re-running the algorithm.
- Decouples algorithm execution from `wx.MessageBox` UI blocking.
- Preserves 100% backward compatibility with `ToolSugiyama` and `ExtensionsPreferences.sugiyamaStepByStep`.
