import tkinter as tk
import customtkinter as ctk
import json
import textwrap

from ui.custom_dialog import CustomDialog

class EditCommandDialog(ctk.CTkToplevel):
    def __init__(self, master, app, item_name, item_config, type):
        super().__init__(master)
        self.app = app
        self.original_item_name = item_name
        self.item_config = item_config 
        self.colors = app.colors

        self.json_editor_visible = False
        self.json_content_visible = False
        self.advanced_mode_active = tk.BooleanVar(value=False)
        self.is_reward = type == "reward"

        self.title(f"✏️ Editando: {item_name}")
        self.geometry("650x700")
        self.transient(master)
        self.grab_set()
        self.focus_force()
        self.resizable(False, True)
        self.configure(fg_color=self.colors['surface'])

        master.update_idletasks()
        dialog_width, dialog_height = 650, 700
        master_x, master_y = master.winfo_rootx(), master.winfo_rooty()
        master_width, master_height = master.winfo_width(), master.winfo_height()
        x = master_x + (master_width - dialog_width) // 2
        y = master_y + (master_height - dialog_height) // 2
        self.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        ctk.CTkLabel(
            self, text=f"EDITAR: {item_name}",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.colors['twitch_purple_light']
        ).pack(pady=(20, 10))

        main_edit_frame = ctk.CTkFrame(self, fg_color=self.colors['surface_dark'])
        main_edit_frame.pack(fill=tk.X, padx=20, pady=10)
        main_edit_frame.grid_columnconfigure(1, weight=1)
        
        current_row = 0
        
        name_label_text = "Nome da Recompensa:" if self.is_reward else "Nome do Comando (Ex: !cmd):"
        ctk.CTkLabel(main_edit_frame, text=name_label_text, font=ctk.CTkFont(size=14, weight="bold")).grid(
             row=current_row, column=0, sticky="w", padx=10, pady=(10, 0))
        self.new_item_name_var = tk.StringVar(value=item_name)
        ctk.CTkEntry(
            main_edit_frame, textvariable=self.new_item_name_var,
            placeholder_text="Novo Nome...", fg_color=self.colors['surface_light'],
            border_color=self.colors['error'] if self.is_reward else self.colors['twitch_purple']
        ).grid(row=current_row + 1, column=0, columnspan=2, sticky="ew", padx=10, pady=(5, 10))
        current_row += 2

        self.input_widgets = []
        if self.is_reward:
            self.msg_var = tk.StringVar(value=item_config.get("message", ""))
            self.msg_entry = ctk.CTkEntry(
                main_edit_frame, textvariable=self.msg_var,
                placeholder_text="Mensagem chat (use {user}, {input})...", fg_color=self.colors['surface_light'],
                border_color=self.colors['twitch_purple']
            )
            self.msg_entry.grid(row=current_row + 1, column=0, columnspan=2, sticky="ew", padx=10, pady=(5, 10))
            self.input_widgets.append(self.msg_entry)
            current_row += 2

            ctk.CTkLabel(main_edit_frame, text="Som (Opcional):", font=ctk.CTkFont(size=14, weight="bold")).grid(
             row=current_row, column=0, sticky="w", padx=10, pady=(10, 0))
            current_row += 1

            sound_input_container = ctk.CTkFrame(main_edit_frame, fg_color="transparent")
            sound_input_container.grid(row=current_row, column=0, columnspan=2, sticky="ew", padx=10, pady=(5, 10))

            sound_input_container.grid_columnconfigure(0, weight=1)
            sound_input_container.grid_columnconfigure(1, weight=0)

            self.sound_var = tk.StringVar(value=item_config.get("sound", ""))
            self.sound_entry = ctk.CTkEntry(
                sound_input_container,
                textvariable=self.sound_var,
                placeholder_text="Caminho para .wav ou .mp3...", fg_color=self.colors['surface_light'],
                border_color=self.colors['twitch_purple']
            )
            self.sound_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5)) 
            self.input_widgets.append(self.sound_entry)
            
            ctk.CTkButton(
                sound_input_container,
                text="Procurar...", 
                command=lambda: self.app.browse_sound_file_for_edit(self.sound_var),
                font=ctk.CTkFont(size=11), width=80, height=30
            ).grid(row=0, column=1, sticky="w", padx=(5, 0))
            current_row += 1
            
        else:
            ctk.CTkLabel(main_edit_frame, text="Resposta:", font=ctk.CTkFont(size=14, weight="bold")).grid(
                 row=current_row, column=0, sticky="w", padx=10, pady=(10, 0))
            self.response_text = tk.StringVar(value=item_config.get("response", ""))
            self.response_entry = ctk.CTkEntry(
                main_edit_frame, textvariable=self.response_text,
                placeholder_text="Nova resposta...", fg_color=self.colors['surface_light'],
                border_color=self.colors['twitch_purple']
            )
            self.response_entry.grid(row=current_row + 1, column=0, columnspan=2, sticky="ew", padx=10, pady=(5, 10))
            self.input_widgets.append(self.response_entry)
            current_row += 2

            ctk.CTkLabel(main_edit_frame, text="Som (Opcional):", font=ctk.CTkFont(size=14, weight="bold")).grid(
                row=current_row, column=0, sticky="w", padx=10, pady=(10, 0))
            current_row += 1

            sound_input_container = ctk.CTkFrame(main_edit_frame, fg_color="transparent")
            sound_input_container.grid(row=current_row, column=0, columnspan=2, sticky="ew", padx=10, pady=(5, 10))
            sound_input_container.grid_columnconfigure(0, weight=1)
            sound_input_container.grid_columnconfigure(1, weight=0)

            self.sound_var = tk.StringVar(value=item_config.get("sound", ""))
            self.sound_entry = ctk.CTkEntry(
                sound_input_container,
                textvariable=self.sound_var,
                placeholder_text="Caminho para .wav ou .mp3...", fg_color=self.colors['surface_light'],
                border_color=self.colors['twitch_purple']
            )
            self.sound_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
            self.input_widgets.append(self.sound_entry)

            ctk.CTkButton(
                sound_input_container,
                text="Procurar...",
                command=lambda: self.app.browse_sound_file_for_edit(self.sound_var),
                font=ctk.CTkFont(size=11), width=80, height=30
            ).grid(row=0, column=1, sticky="w", padx=(5, 0))
            current_row += 1

            ctk.CTkLabel(main_edit_frame, text="Permissão:", font=ctk.CTkFont(size=14, weight="bold")).grid(
                 row=current_row, column=0, sticky="w", padx=10, pady=(10, 0))

            permission_levels = ["Everyone", "Vip", "Mod", "Broadcaster"]
            current_perm_str = item_config.get('permission', 'everyone').capitalize()
            if current_perm_str not in permission_levels:
                current_perm_str = "Everyone"
            
            self.permission_var = tk.StringVar(value=current_perm_str)
            
            self.permission_menu = ctk.CTkOptionMenu(
                main_edit_frame,
                variable=self.permission_var,
                values=permission_levels,
                fg_color=self.colors['surface_light'],
                button_color=self.colors['twitch_purple'],
                button_hover_color=self.colors['twitch_purple_dark'],
                dropdown_fg_color=self.colors['surface_light'],
                width=150,
                height=30
            )
            self.permission_menu.grid(row=current_row + 1, column=0, columnspan=2, sticky="w", padx=10, pady=(5, 10))
            self.input_widgets.append(self.permission_menu)
            current_row += 2

            ctk.CTkLabel(main_edit_frame, text="Cooldown global (s):", font=ctk.CTkFont(size=14, weight="bold")).grid(
                row=current_row, column=0, sticky="w", padx=10, pady=(10, 0))
            ctk.CTkLabel(main_edit_frame, text="Cooldown por usuário (s):", font=ctk.CTkFont(size=14, weight="bold")).grid(
                row=current_row, column=1, sticky="w", padx=10, pady=(10, 0))
            current_row += 1

            self.cd_global_var = tk.StringVar(value=str(item_config.get("cooldown_global", 3)))
            self.cd_user_var = tk.StringVar(value=str(item_config.get("cooldown_user", 10)))

            self.cd_global_entry = ctk.CTkEntry(
                main_edit_frame, textvariable=self.cd_global_var, width=120,
                placeholder_text="3", fg_color=self.colors['surface_light'],
                border_color=self.colors['twitch_purple']
            )
            self.cd_user_entry = ctk.CTkEntry(
                main_edit_frame, textvariable=self.cd_user_var, width=140,
                placeholder_text="10", fg_color=self.colors['surface_light'],
                border_color=self.colors['twitch_purple']
            )
            self.cd_global_entry.grid(row=current_row, column=0, sticky="w", padx=10, pady=(5, 10))
            self.cd_user_entry.grid(row=current_row, column=1, sticky="w", padx=10, pady=(5, 10))
            self.input_widgets.extend([self.cd_global_entry, self.cd_user_entry])
            current_row += 1

            self.cd_bypass_mods_var = tk.BooleanVar(value=bool(item_config.get("cooldown_bypass_mods", True)))
            self.cd_bypass_switch = ctk.CTkSwitch(
                main_edit_frame, text="Bypass mods/streamer",
                variable=self.cd_bypass_mods_var,
                fg_color=self.colors['surface_light'],
                button_color=self.colors['twitch_purple'],
                button_hover_color=self.colors['twitch_purple_dark']
            )
            self.cd_bypass_switch.grid(row=current_row, column=0, columnspan=2, sticky="w", padx=10, pady=(0, 10))
            self.input_widgets.append(self.cd_bypass_switch)
            current_row += 1

        self.json_toggle_button = ctk.CTkButton(
            self, text="🛠️ JSON AVANÇADO (Modo de Edição)",
            command=self._toggle_json_editor,
            fg_color=self.colors['surface_dark'], hover_color=self.colors['surface_light'],
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.json_toggle_button.pack(pady=(15, 5), padx=20, fill=tk.X)
        self.json_container_frame = ctk.CTkFrame(self, fg_color=self.colors['background'])
        
        json_dump = json.dumps(item_config, indent=2, ensure_ascii=False)
        self.json_content = ctk.CTkTextbox(
            self.json_container_frame,
            height=250,
            fg_color=self.colors['surface_light'],
            text_color=self.colors['text_primary'],
            font=('Consolas', 12)
        )
        self.json_content.insert(tk.END, json_dump)
        self.json_content.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=(0, 20))

        ctk.CTkButton(
            button_frame, text="✅ SALVAR", command=self.save_changes,
            fg_color=self.colors['success'], hover_color='#00cc6a',
            font=ctk.CTkFont(size=12, weight="bold"), width=120
        ).pack(side=tk.LEFT, padx=10)

        ctk.CTkButton(
            button_frame, text="❌ CANCELAR", command=self.destroy,
            fg_color=self.colors['error'], hover_color='#cc4444',
            font=ctk.CTkFont(size=12, weight="bold"), width=120
        ).pack(side=tk.LEFT, padx=10)

        self.transient(master)
        try:
            self.grab_set()
        except tk.TclError:
            pass

        self.after(10, lambda: self.focus_set() if self.winfo_exists() else None)
        self.bind("<Destroy>", lambda e: self.after(1, self._safe_unbind_focus))

    def _toggle_json_editor(self):
        """Mostra/oculta o editor JSON completo e desabilita/habilita inputs simples."""
        new_state = tk.DISABLED if not self.json_editor_visible else tk.NORMAL
        
        if not self.json_editor_visible:
            self.json_container_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))
            self.json_toggle_button.configure(text="❌ FECHAR JSON")
            self.json_editor_visible = True
            self.advanced_mode_active.set(True)

        else:
            self.json_container_frame.pack_forget()
            self.json_toggle_button.configure(text="🛠️ JSON AVANÇADO (Modo de Edição)")
            self.json_editor_visible = False
            self.advanced_mode_active.set(False)
            
        for widget in self.input_widgets:
            widget.configure(state=new_state)

        if hasattr(self, 'sound_button'):
             self.sound_button.configure(state=new_state)

        self.update_idletasks()

    def save_changes(self):
        """
        Lê o JSON como fonte de verdade para a estrutura interna,
        e aplica os campos simples (Nome, Mensagem/Som) por cima.
        """
        try:
            raw_json = self.json_content.get("1.0", tk.END).strip()
            new_config = json.loads(raw_json)
            
            new_name = self.new_item_name_var.get().strip()
            if not new_name:
                self.app.log_message("❌ ERRO: O nome não pode ser vazio.", "error")
                return

            if not self.advanced_mode_active.get():
                if self.is_reward:
                    new_message = self.msg_var.get().strip()
                    new_sound = self.sound_var.get().strip()

                    new_config['message'] = new_message if new_message else None
                    new_config['sound'] = new_sound if new_sound else None
                    
                else: 
                    new_config['response'] = self.response_text.get().strip() if self.response_text.get().strip() else None
                    new_config['sound'] = self.sound_var.get().strip() if self.sound_var.get().strip() else None
                    new_config['permission'] = self.permission_var.get().lower() if self.permission_var.get().lower() else 'everyone'
            
            try:
                cdg = int(self.cd_global_var.get().strip() or "3")
            except ValueError:
                cdg = 3
            try:
                cdu = int(self.cd_user_var.get().strip() or "10")
            except ValueError:
                cdu = 10
            new_config['cooldown_global'] = max(0, cdg)
            new_config['cooldown_user']   = max(0, cdu)
            new_config['cooldown_bypass_mods'] = bool(self.cd_bypass_mods_var.get())

            new_config = {k: v for k, v in new_config.items() if v is not None}
            
            if self.is_reward:
                target_dict, save_func, refresh_func = self.app.reward_actions, self.app.save_settings, self.app.refresh_rewards_list
            else:
                target_dict, save_func, refresh_func = self.app.default_commands, self.app.save_commands, self.app.refresh_commands_list

            if new_name != self.original_item_name:
                if new_name in target_dict:
                    self.app.log_message(f"❌ ERRO: O novo nome '{new_name}' já existe.", "error")
                    return
                del target_dict[self.original_item_name]

            target_dict[new_name] = new_config

            save_func()
            refresh_func()
            
            self.app.log_message(f"✏️ '{new_name}' editado e salvo!", "success")
            self.after(0, self._safe_destroy)
            
        except json.JSONDecodeError as e:
            self.app.log_message(f"❌ ERRO JSON: O JSON de edição está mal formatado. {e}", "error")
            CustomDialog(self.master, "ERRO JSON", f"O JSON de edição está mal formatado. Corrija o JSON para salvar. Detalhe: {e}", self.colors, 'error').wait_window()
        except Exception as e:
            self.app.log_message(f"❌ Erro ao salvar edição: {e}", "error")
            self.after(0, self._safe_destroy)

    def _safe_unbind_focus(self):
        """Remove callbacks de foco pendentes quando a janela é destruída."""
        try:
            self.tk.call('focus', '')
        except tk.TclError:
            pass

    def _safe_destroy(self):
        """Destrói a janela apenas se ainda existir (evita TclError)."""
        if self.winfo_exists():
            try:
                self.destroy()
            except tk.TclError:
                pass
