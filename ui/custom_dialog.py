import tkinter as tk
import customtkinter as ctk

class CustomDialog(ctk.CTkToplevel):
    """
    Uma janela de diálogo personalizada e genérica para 'help', 'error',
    'warning', 'info' ou confirmações ('yes'/'no').
    """
    def __init__(self, master, title, text, colors,
                 dialog_type='info', width=None, height=None,
                 buttons=None,
                 callback=None):
        super().__init__(master)

        self.colors = colors
        self.callback = callback
        self._result = None

        self.title(title)
        self.resizable(False, False)
        self.configure(fg_color=self.colors['surface'])

        if dialog_type == 'help':
            dialog_width = width or 500
            dialog_height = height or 620
            title_color = self.colors['twitch_purple_light']
        elif dialog_type == 'error':
            dialog_width = width or 450
            dialog_height = height or 220
            title_color = self.colors['error']
        elif dialog_type == 'warning':
            dialog_width = width or 450
            dialog_height = height or (220 if buttons else 200)
            title_color = self.colors['warning']
        else:
            dialog_width = width or 450
            dialog_height = height or (220 if buttons else 200)
            title_color = self.colors['accent']

        master.update_idletasks()
        master_x = master.winfo_rootx()
        master_y = master.winfo_rooty()
        master_width = master.winfo_width()
        master_height = master.winfo_height()
        x = master_x + (master_width - dialog_width) // 2
        y = master_y + (master_height - dialog_height) // 2
        pos_str = f"+{x}+{y}"

        title_label = ctk.CTkLabel(
            self, text=title,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=title_color
        )
        title_label.pack(pady=(20, 10))

        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(side=tk.BOTTOM, pady=(10, 20))

        if buttons and self.callback:
            for btn_text, btn_value in reversed(buttons):
                is_confirm_action = btn_value in ["yes", "ok", "confirm", "delete"]
                fg_color = self.colors['twitch_purple'] if is_confirm_action else self.colors['surface_light']
                hover_color = self.colors['twitch_purple_dark'] if is_confirm_action else self.colors['accent']

                btn = ctk.CTkButton(
                    button_frame, text=btn_text,
                    command=lambda val=btn_value: self._button_click(val),
                    font=ctk.CTkFont(size=12, weight="bold"),
                    fg_color=fg_color, hover_color=hover_color,
                    width=100, height=35
                )
                btn.pack(side=tk.LEFT, padx=10)
        else:
            close_button = ctk.CTkButton(
                button_frame, text="FECHAR",
                command=self.destroy,
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color=self.colors['twitch_purple'],
                hover_color=self.colors['twitch_purple_dark'],
                width=140, height=35
            )
            close_button.pack(padx=10)

        if dialog_type == 'help':
            text_frame = ctk.CTkFrame(
                self, fg_color=self.colors['surface_light'],
                border_width=2, border_color=self.colors['twitch_purple']
            )
            text_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
            textbox = ctk.CTkTextbox(
                text_frame, fg_color="transparent",
                text_color=self.colors['text_secondary'],
                font=ctk.CTkFont(family="Consolas", size=13),
                wrap="word", height=dialog_height - 150
            )
            textbox.pack(fill="both", expand=True, padx=5, pady=5)
            textbox.insert("1.0", text)
            textbox.configure(state="disabled")
        else:
            text_frame = ctk.CTkFrame(self, fg_color=self.colors['surface_light'])
            text_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
            content_label = ctk.CTkLabel(
                text_frame, text=text,
                font=ctk.CTkFont(size=13),
                text_color=self.colors['text_secondary'],
                wraplength=dialog_width - 60,
                anchor="center", justify="center"
            )
            content_label.pack(fill="both", expand=True, padx=10, pady=10)

        self.update_idletasks()
        self.geometry(pos_str)
        self.minsize(dialog_width // 2, dialog_height // 2)

        self.transient(master)
        try:
            self.grab_set()
        except tk.TclError:
            pass

        self.after(10, lambda: self.focus_set() if self.winfo_exists() else None)
        self.bind("<Destroy>", lambda e: self.after(1, self._safe_unbind_focus))

    #???? checkar isso dps - GPT :p

    def _safe_unbind_focus(self):
        """Remove callbacks de foco pendentes quando a janela é destruída."""
        try:
            self.tk.call('focus', '')
        except tk.TclError:
            pass

    def _button_click(self, value):
        """Chamado quando um botão é clicado."""
        self._result = value
        if self.callback:
            self.after(10, lambda: self._safe_callback(value))
        else:
            self.after(50, self.destroy)

    def _safe_callback(self, value):
        """Executa o callback com segurança e destrói a janela."""
        try:
            self.callback(value)
        except Exception as e:
            print(f"Error executing dialog callback: {e}")
        self.grab_release()
        self.after(50, self._safe_destroy)

    def _safe_destroy(self):
        """Destrói a janela apenas se ainda existir (evita TclError)."""
        if self.winfo_exists():
            try:
                self.destroy()
            except tk.TclError:
                pass
