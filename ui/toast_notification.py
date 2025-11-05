import customtkinter as ctk

class ToastNotification(ctk.CTkToplevel):
    def __init__(self, master, message, duration=1750, position="top-right", colors=None, toast_type="success"):
        super().__init__(master)

        self.colors = colors if colors else {
            'success': '#00ff7f', 'error': '#ff5555', 'warning': '#ffaa00',
            'surface_lighter': '#26262c', 'text_primary': '#ffffff', 'background': '#0e0e10'
        }
        
        if toast_type == "success":
            self.bg_color = self.colors.get('success', '#00ff7f')
            self.text_color = self.colors.get('background', '#0e0e10') 
        elif toast_type == "error":
             self.bg_color = self.colors.get('error', '#ff5555')
             self.text_color = self.colors.get('text_primary', '#ffffff')
        elif toast_type == "warning":
             self.bg_color = self.colors.get('warning', '#ffaa00')
             self.text_color = self.colors.get('background', '#0e0e10')
        else:
             self.bg_color = self.colors.get('surface_lighter', '#26262c')
             self.text_color = self.colors.get('text_primary', '#ffffff')

        self.overrideredirect(True) 
        self.wm_attributes("-topmost", True)
        self.attributes("-alpha", 0.0) 
        if hasattr(self, 'wm_attributes'):
             try:
                 self.wm_attributes("-transparentcolor", self._apply_appearance_mode(self.cget("fg_color")))
             except Exception:
                 self.configure(fg_color=self._apply_appearance_mode(self.cget("fg_color"))) 
        
        self.frame = ctk.CTkFrame(
            self,
            fg_color=self.bg_color,
            corner_radius=10,
            border_width=1,
            border_color=self._apply_appearance_mode(ctk.ThemeManager.theme["CTkFrame"]["border_color"])
        )
        self.frame.pack(padx=5, pady=5)

        self.label = ctk.CTkLabel(
            self.frame,
            text=message,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.text_color,
            padx=15,
            pady=8
        )
        self.label.pack()

        self.update_idletasks()
        master_x = master.winfo_rootx()
        master_y = master.winfo_rooty()
        master_width = master.winfo_width()
        toast_width = self.winfo_width()
        toast_height = self.winfo_height()

        x = master_x + master_width - toast_width - 20
        y = master_y + 20
        self.geometry(f"+{x}+{y}")

        self.duration = duration
        self.fade_increment = 0.1
        self.fade_delay = 20
        self.current_alpha = 0.0
        self.fade_in()

    def fade_in(self):
        """Gradually increases the window opacity."""
        if self.current_alpha < 1.0:
            self.current_alpha += self.fade_increment
            if self.current_alpha > 1.0: self.current_alpha = 1.0
            self.attributes("-alpha", self.current_alpha)
            self.after(self.fade_delay, self.fade_in)
        else:
            self.after(self.duration, self.fade_out)

    def fade_out(self):
        """Gradually decreases the window opacity and then destroys it."""
        if self.current_alpha > 0.0:
            self.current_alpha -= self.fade_increment
            if self.current_alpha < 0.0: self.current_alpha = 0.0
            self.attributes("-alpha", self.current_alpha)
            self.after(self.fade_delay, self.fade_out)
        else:
            self.destroy()