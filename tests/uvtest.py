#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ['wxPython']
# ///

import wx

class MyFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent)
        self.SetSize((400, 300))
        self.SetTitle("Test Maximize Frame")
        self.panel_1 = wx.Panel(self, wx.ID_ANY)

        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        self.text_ctrl_1 = wx.TextCtrl(self.panel_1, wx.ID_ANY, "", style=wx.TE_MULTILINE)

        sizer_1.Add(self.text_ctrl_1, 1, wx.EXPAND, 0)

        self.panel_1.SetSizer(sizer_1)
        self.Layout()
        self.Maximize(True)


if __name__ == "__main__":
    app = wx.App()
    frame = MyFrame(None)
    frame.Show()
    app.MainLoop()
