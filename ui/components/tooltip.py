import tkinter as tk
import customtkinter as ctk
from typing import Optional

class ToolTip:
    """
    Tooltip com título + descrição para qualquer widget Tk/CTk.
    - Mostra após um delay (padrão: 400ms).
    """
    def __init__(
        self,
        widget: tk.Widget,
        title: str,
        text: str,
        *,
        delay: int = 400,
        wraplength: int = 300,
        colors: Optional[dict] = None
    ):
        self.widget = widget
        self.title = title
        self.text = text
        self.delay = delay
        self.wraplength = wraplength
        self.colors = colors or {}

        self._after_id = None
        self._tip_win: Optional[ctk.CTkToplevel] = None

        self.widget.bind("<Enter>", self._on_enter, add="+")
        self.widget.bind("<Leave>", self._on_leave, add="+")
        self.widget.bind("<Motion>", self._on_motion, add="+")
        self.widget.bind("<FocusOut>", self._on_leave, add="+")

    def _on_enter(self, _event=None):
        self._schedule()

    def _on_leave(self, _event=None):
        self._unschedule()
        self._hide()

    def _on_motion(self, event):
        if self._tip_win:
            self._reposition(event.x_root, event.y_root)

    def _schedule(self):
        self._unschedule()
        self._after_id = self.widget.after(self.delay, self._show)

    def _unschedule(self):
        if self._after_id is not None:
            try:
                self.widget.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None

    def _show(self):
        if self._tip_win or not self.widget.winfo_viewable():
            return
        
        self._tip_win = ctk.CTkToplevel(self.widget)
        self._tip_win.overrideredirect(True)
        self._tip_win.attributes("-topmost", True)
        self._tip_win.configure(fg_color=self.colors.get("surface_dark", "#1e1e1e"))

        outer = ctk.CTkFrame(
            self._tip_win,
            fg_color=self.colors.get("surface_dark", "#1e1e1e"),
            corner_radius=8,
        )
        outer.pack(fill="both", expand=True, padx=1, pady=1)

        title_lbl = ctk.CTkLabel(
            outer,
            text=self.title,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors.get("twitch_purple_light", "#a970ff"),
        )
        title_lbl.pack(anchor="w", padx=10, pady=(8, 0))

        desc_lbl = ctk.CTkLabel(
            outer,
            text=self.text,
            font=ctk.CTkFont(size=11),
            text_color=self.colors.get("text_primary", "#e5e7eb"),
            wraplength=self.wraplength,
            justify="left",
        )
        desc_lbl.pack(anchor="w", padx=10, pady=(4, 10))

        try:
            x = self.widget.winfo_pointerx()
            y = self.widget.winfo_pointery()
        except Exception:
            x = self.widget.winfo_rootx() + 20
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 10

        self._reposition(x, y)

    def _hide(self):
        if self._tip_win and self._tip_win.winfo_exists():
            try:
                self._tip_win.destroy()
            except tk.TclError:
                pass
        self._tip_win = None

    def _reposition(self, x_root: int, y_root: int):
        if not self._tip_win:
            return

        self._tip_win.update_idletasks()
        w = self._tip_win.winfo_width()
        h = self._tip_win.winfo_height()

        screen_w = self._tip_win.winfo_screenwidth()
        screen_h = self._tip_win.winfo_screenheight()

        pad = 12
        x = x_root + pad
        y = y_root + pad

        if x + w > screen_w - 4:
            x = screen_w - w - 4
        if y + h > screen_h - 4:
            y = screen_h - h - 4

        try:
            self._tip_win.geometry(f"+{x}+{y}")
        except Exception:
            pass


def attach_tooltip(widget: tk.Widget, title: str, text: str, **kwargs) -> ToolTip:
    return ToolTip(widget, title, text, **kwargs)
