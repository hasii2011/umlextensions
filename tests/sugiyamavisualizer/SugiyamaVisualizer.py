"""
Visual GUI demo application demonstrating the Sugiyama hierarchical layout algorithm.

Uses wxPython and wx.lib.ogl (Object Graphics Library) to display hierarchical
levels, virtual nodes, barycenter ordering, and link control points.
"""

from wx import App
from wx.lib.ogl import OGLInitialize

from tests.sugiyamavisualizer.SugiyamaVisualizerFrame import SugiyamaVisualizerFrame


def main():
    """
    Launch the Sugiyama visualizer demo application.
    """
    app: App = App(False)
    OGLInitialize()
    frame: SugiyamaVisualizerFrame = SugiyamaVisualizerFrame()
    frame.Show(True)
    app.MainLoop()


if __name__ == '__main__':
    main()
