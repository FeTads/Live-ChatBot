from datetime import datetime
import tkinter as tk
import customtkinter as ctk

from ui.custom_dialog import CustomDialog

class EditTimerDialog(ctk.CTkToplevel):
    def __init__(self, master, app, timer_name, timer_config):
        super().__init__(master)
        self.app = app
        self.original_timer_name = timer_name
        self.timer_config = timer_config
        self.colors = app.colors

        self.title(f"✏️ Editando Timer: {timer_name}")
        self.geometry("600x450")
        self.transient(master)
        self.grab_set()
        self.resizable(False, False)
        self.configure(fg_color=self.colors['surface'])

        master.update_idletasks()
        dialog_width, dialog_height = 600, 450
        master_x, master_y = master.winfo_rootx(), master.winfo_rooty()
        master_width, master_height = master.winfo_width(), master.winfo_height()
        x = master_x + (master_width - dialog_width) // 2
        y = master_y + (master_height - dialog_height) // 2
        self.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

        ctk.CTkLabel(
            self, text=f"EDITAR TIMER",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.colors['twitch_purple_light']
        ).pack(pady=(20, 10))

        main_edit_frame = ctk.CTkFrame(self, fg_color=self.colors['surface_dark'])
        main_edit_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        main_edit_frame.grid_columnconfigure(1, weight=1)
        
        current_row = 0

        ctk.CTkLabel(main_edit_frame, text="Nome:", font=ctk.CTkFont(size=14, weight="bold")).grid(
             row=current_row, column=0, sticky="w", padx=15, pady=(10, 0))
        self.name_var = tk.StringVar(value=timer_name)
        self.name_entry = ctk.CTkEntry(
            main_edit_frame, textvariable=self.name_var,
            fg_color=self.colors['surface_light'], border_color=self.colors['twitch_purple']
        )
        self.name_entry.grid(row=current_row + 1, column=0, columnspan=2, sticky="ew", padx=15, pady=(5, 10))
        current_row += 2
        
        ctk.CTkLabel(main_edit_frame, text="Mensagem:", font=ctk.CTkFont(size=14, weight="bold")).grid(
             row=current_row, column=0, sticky="w", padx=15, pady=(10, 0))
        self.message_var = tk.StringVar(value=timer_config.get("message", ""))
        self.message_entry = ctk.CTkEntry(
            main_edit_frame, textvariable=self.message_var,
            fg_color=self.colors['surface_light'], border_color=self.colors['twitch_purple']
        )
        self.message_entry.grid(row=current_row + 1, column=0, columnspan=2, sticky="ew", padx=15, pady=(5, 10))
        current_row += 2
        
        interval_frame = ctk.CTkFrame(main_edit_frame, fg_color="transparent")
        interval_frame.grid(row=current_row, column=0, columnspan=2, sticky="ew", padx=15, pady=(5, 10))
        interval_frame.grid_columnconfigure(1, weight=1)
        interval_frame.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(interval_frame, text="Intervalo (min):", font=ctk.CTkFont(size=12)).grid(
            row=0, column=0, sticky="w", padx=(0, 10))
        self.interval_var = tk.StringVar(value=str(timer_config.get("interval_min", 15)))
        self.interval_entry = ctk.CTkEntry(
            interval_frame, textvariable=self.interval_var,
            fg_color=self.colors['surface_light'], border_color=self.colors['twitch_purple']
        )
        self.interval_entry.grid(row=0, column=1, sticky="ew")

        ctk.CTkLabel(interval_frame, text="Linhas Mínimas:", font=ctk.CTkFont(size=12)).grid(
            row=0, column=2, sticky="w", padx=(20, 10))
        self.lines_var = tk.StringVar(value=str(timer_config.get("min_lines", 5)))
        self.lines_entry = ctk.CTkEntry(
            interval_frame, textvariable=self.lines_var,
            fg_color=self.colors['surface_light'], border_color=self.colors['twitch_purple']
        )
        self.lines_entry.grid(row=0, column=3, sticky="ew")
        
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=(10, 20))

        ctk.CTkButton(
            button_frame, text="✅ SALVAR", command=self.save_changes,
            fg_color=self.colors['success'], hover_color='#00cc6a',
            font=ctk.CTkFont(size=12, weight="bold"), width=120
        ).pack(side=tk.LEFT, padx=10)

        ctk.CTkButton(
            button_frame, text="❌ CANCELAR", command=self._safe_destroy,
            fg_color=self.colors['error'], hover_color='#cc4444',
            font=ctk.CTkFont(size=12, weight="bold"), width=120
        ).pack(side=tk.LEFT, padx=10)
        
        self.after(10, self.focus_force)
        self.wait_window()

    def _safe_destroy(self):
        try:
            self.grab_release()
        except:
            pass
        self.destroy()

    def save_changes(self):
        """Valida e salva as alterações no timer."""
        
        new_name = self.name_var.get().strip()
        new_message = self.message_var.get().strip()
        
        try:
            new_interval = int(self.interval_var.get())
            new_lines = int(self.lines_var.get())
        except ValueError:
            CustomDialog(self, "Erro", "Intervalo e Linhas Mínimas devem ser números inteiros!", self.app.colors, 'error').wait_window()
            return
            
        if not new_name or not new_message:
            CustomDialog(self, "Erro", "Nome do Timer e Mensagem são obrigatórios!", self.app.colors, 'error').wait_window()
            return
            
        if new_name != self.original_timer_name and new_name in self.app.timers:
            CustomDialog(self, "Erro", f"O nome de timer '{new_name}' já existe!", self.app.colors, 'error').wait_window()
            return
        
        new_config = {
            "message": new_message,
            "interval_min": new_interval,
            "min_lines": new_lines,
            "enabled": self.timer_config.get('enabled', True),
            "last_run": self.timer_config.get('last_run', datetime.now())
        }

        target_dict = self.app.timers
        
        if new_name != self.original_timer_name:
            del target_dict[self.original_timer_name]
            
        target_dict[new_name] = new_config

        self.app.save_timers()
        self.app.refresh_timers_list()
        
        self.app.log_message(f"✏️ Timer '{new_name}' editado e salvo!", "success")
        self.after(0, self._safe_destroy)