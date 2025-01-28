import tkinter as tk
import tkinter.ttk as ttk

from .base import BaseComponent
from .selecter import KeySelecter, ScaleSelecter


class _Display(BaseComponent):
    _scale: tk.StringVar
    _keyname: tk.StringVar
    _scalename: tk.StringVar
    _scaleinfo: tk.StringVar

    _wrapper: ttk.Frame
    _scaledisplay: ttk.Label
    _scaleinfodisplay: ttk.Label

    def __init__(self, master: tk.Misc):
        super().__init__(master)
        self.master = master
        self.create_widget()

    def create_widget(self):
        self._scale = tk.StringVar()
        self._keyname = tk.StringVar()
        self._scalename = tk.StringVar()
        self._scaleinfo = tk.StringVar()

        def combine(*args):
            self._scale.set(f"{self.keyname} {self.scalename}")

        self._keyname.trace_add("write", combine)
        self._scalename.trace_add("write", combine)

        self._wrapper = ttk.Frame(self, padding=(24, 8), borderwidth=2, relief=tk.SOLID)
        self._scaledisplay = ttk.Label(
            self._wrapper, textvariable=self._scale, font=("Times", 18)
        )
        self._scaleinfodisplay = ttk.Label(
            self._wrapper, textvariable=self._scaleinfo, font=("Times", 10)
        )

        self._wrapper.pack()
        self._scaledisplay.pack(side=tk.TOP, anchor=tk.NW)
        self._scaleinfodisplay.pack(side=tk.TOP, anchor=tk.NW)

    def default(self):
        return

    @property
    def keyname(self):
        return self._keyname.get()

    @keyname.setter
    def keyname(self, value: str):
        return self._keyname.set(value)

    @property
    def scalename(self):
        return self._scalename.get()

    @scalename.setter
    def scalename(self, value: str):
        self._scalename.set(value)

    @property
    def scaleinfo(self):
        return self._scaleinfo.get()

    @scaleinfo.setter
    def scaleinfo(self, value: str):
        self._scaleinfo.set(value)


class ScaleViewer(BaseComponent):
    scaledisplay: _Display
    keyselecter: KeySelecter
    scaleselecter: ScaleSelecter

    def __init__(self, master: tk.Misc):
        super().__init__(master)
        self.master = master
        self.create_widget()
        self.default()

    def create_widget(self):
        self.scaledisplay = _Display(self)
        self.keyselecter = KeySelecter(self)
        self.scaleselecter = ScaleSelecter(self)

        self.keyselecter.set_callback_onClickKeyButton(self.display_scaledisplay)
        self.scaleselecter.set_callback_onClickScaleButton(self.display_scaledisplay)

        self.scaledisplay.pack(side=tk.TOP, anchor=tk.W, expand=True)
        self.keyselecter.pack(side=tk.LEFT, anchor=tk.N)
        self.scaleselecter.pack(side=tk.LEFT, anchor=tk.N)

    def default(self):
        self.keyselecter.default()
        self.scaleselecter.default()

    def display_scaledisplay(self):
        self.scaledisplay.keyname = self.keyselecter.keyname
        self.scaledisplay.scalename = self.scaleselecter.scalename
        self.scaledisplay.scaleinfo = self.scaleselecter.scaleinfo
