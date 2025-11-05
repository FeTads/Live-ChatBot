import tkinter as tk
import customtkinter as ctk

from ui.components.tooltip import attach_tooltip

class CommandsPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=app.colors['background'])
        self.app = app
        self.grid(row=0, column=0, sticky="nsew")

        main_page_frame = ctk.CTkFrame(self, fg_color=self.app.colors['surface'])
        main_page_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        commands_frame = ctk.CTkFrame(main_page_frame, fg_color=self.app.colors['surface'])
        commands_frame.pack(fill=tk.BOTH, expand=True)

        frame_title = ctk.CTkLabel(
            commands_frame, text="⚙️ COMANDOS",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.app.colors['twitch_purple_light']
        )
        frame_title.pack(anchor=tk.W, padx=15, pady=(10, 15))

        add_cmd_frame = ctk.CTkFrame(commands_frame, fg_color=self.app.colors['surface'])
        add_cmd_frame.pack(fill=tk.X, padx=15, pady=10)
        add_cmd_frame.grid_columnconfigure(1, weight=0)
        add_cmd_frame.grid_columnconfigure(3, weight=1)
        add_cmd_frame.grid_columnconfigure(4, weight=0)
        add_cmd_frame.grid_columnconfigure(5, weight=0)


        ctk.CTkLabel(add_cmd_frame, text="Comando:", font=ctk.CTkFont(size=12)).grid(
            row=0, column=0, columnspan=2, sticky="sw", pady=(5, 0), padx=(0, 10))
        ctk.CTkLabel(add_cmd_frame, text="Resposta:", font=ctk.CTkFont(size=12)).grid(
            row=0, column=3, sticky="sw", pady=(5, 0), padx=(0, 10))
        ctk.CTkLabel(add_cmd_frame, text="Quem pode usar:", font=ctk.CTkFont(size=12)).grid(
            row=0, column=4, sticky="sw", pady=(5, 0), padx=(25, 10))

        self.app.new_cmd_var = tk.StringVar(value="")
        self.app.new_cmd_entry = ctk.CTkEntry(
            add_cmd_frame, textvariable=self.app.new_cmd_var, width=150,
            placeholder_text="!comando", 
            fg_color=self.app.colors['surface_light'],
            border_color=self.app.colors['twitch_purple'],
            placeholder_text_color=self.app.colors['text_secondary']
        )
        self.app.new_cmd_entry.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 5), padx=(0, 10))

        ctk.CTkLabel(add_cmd_frame, text="➡️", font=ctk.CTkFont(size=14)).grid(
             row=1, column=2, pady=(0, 5), padx=(0, 0))
        
        if self.app.new_cmd_var.get() == "":
            self.app.new_cmd_var.set("!comando")

        self.app.new_response_var = tk.StringVar(value="")
        self.app.new_response_entry = ctk.CTkEntry(
            add_cmd_frame, textvariable=self.app.new_response_var,
            placeholder_text="O que o bot deve responder...", 
            fg_color=self.app.colors['surface_light'],
            border_color=self.app.colors['twitch_purple'],
            placeholder_text_color=self.app.colors['text_secondary']
        )
        self.app.new_response_entry.grid(row=1, column=3, sticky="ew", pady=(0, 5), padx=(0, 10))
        if self.app.new_response_var.get() == "":
            self.app.new_response_var.set("resposta do bot")

        permission_levels = ["Everyone", "VIP", "Mod", "Broadcaster"]
        self.app.new_cmd_permission_var = tk.StringVar(value="Everyone")
        self.app.new_cmd_permission_menu = ctk.CTkOptionMenu(
            add_cmd_frame,
            variable=self.app.new_cmd_permission_var,
            values=permission_levels,
            fg_color=self.app.colors['surface_light'],
            button_color=self.app.colors['twitch_purple'],
            button_hover_color=self.app.colors['twitch_purple_dark'],
            dropdown_fg_color=self.app.colors['surface_light'],
            width=120,
            height=30
        )
        self.app.new_cmd_permission_menu.grid(row=1, column=4, pady=(0, 5), padx=(5, 10))

        self.app.add_cmd_button = ctk.CTkButton(
            add_cmd_frame, text="➕ ADICIONAR", command=self.app.add_command,
            fg_color=self.app.colors['success'], hover_color='#00cc6a',
            font=ctk.CTkFont(size=12, weight="bold"), width=100, height=30
        )
        self.app.add_cmd_button.grid(row=1, column=8, pady=(0, 5), padx=(5,0))


        ctk.CTkLabel(add_cmd_frame, text="Cooldown (usuário):", font=ctk.CTkFont(size=12)).grid(
            row=2, column=0, sticky="sw", pady=(2, 0), padx=(0, 4))
        ctk.CTkLabel(add_cmd_frame, text="Cooldown global:", font=ctk.CTkFont(size=12)).grid(
            row=2, column=2, sticky="sw", pady=(2, 0), padx=(2, 4))
        
        self.app.new_cmd_cd_user_var = tk.StringVar(value="10")
        self.app.new_cmd_cd_user_entry = ctk.CTkEntry(
            add_cmd_frame, textvariable=self.app.new_cmd_cd_user_var,
            placeholder_text="10",
            fg_color=self.app.colors['surface_light'],
            border_color=self.app.colors['twitch_purple'],
            placeholder_text_color=self.app.colors['text_secondary']
        )
        self.app.new_cmd_cd_user_entry.grid(row=3, column=0, sticky="ew", pady=(2, 0), padx=(0, 28))

        self.app.new_cmd_cd_global_var = tk.StringVar(value="3")
        self.app.new_cmd_cd_global_entry = ctk.CTkEntry(
            add_cmd_frame, textvariable=self.app.new_cmd_cd_global_var,
            placeholder_text="3",
            fg_color=self.app.colors['surface_light'],
            border_color=self.app.colors['twitch_purple'],
            placeholder_text_color=self.app.colors['text_secondary']
        )
        self.app.new_cmd_cd_global_entry.grid(row=3, column=2, sticky="ew", pady=(2, 0), padx=(0, 2))

        self.app.new_cmd_bypass_mods_var = tk.BooleanVar(value=False)
        self.app.new_cmd_bypass_mods_switch = ctk.CTkSwitch(
            add_cmd_frame, text="Bypass mods/streamer",
            variable=self.app.new_cmd_bypass_mods_var,
            fg_color=self.app.colors['surface_light'],
            button_color=self.app.colors['twitch_purple'],
            button_hover_color=self.app.colors['twitch_purple_dark']
        )
        self.app.new_cmd_bypass_mods_switch.grid(row=4, column=0, sticky="w", pady=(10, 2), padx=(2, 3))
        attach_tooltip(
            self.app.new_cmd_bypass_mods_switch,
            "Bypass",
            "Quando ativado, Moderadores e o Streamer ignoram o cooldown.\n"
            "Obs: o cooldown ainda é setado, para o resto do chat.",
            colors=self.app.colors,
            delay=350,
            wraplength=320
        )

        list_frame = ctk.CTkFrame(commands_frame, fg_color=self.app.colors['surface'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 10))

        ctk.CTkLabel(list_frame, text="📋 Comandos Configurados:",
                       font=ctk.CTkFont(size=14, weight="bold")).pack(anchor=tk.W, pady=(0, 5))

        list_container = ctk.CTkFrame(list_frame, fg_color=self.app.colors['surface'])
        list_container.pack(fill=tk.BOTH, expand=True)

        self.commands_scroll_frame = ctk.CTkScrollableFrame(
            list_container,
            fg_color=self.app.colors['surface_light'],
            border_width=1,
            border_color=self.app.colors['surface_lighter']
        )
        self.commands_scroll_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10), pady=5)
        self.commands_scroll_frame.grid_columnconfigure(0, weight=1)

        button_container = ctk.CTkFrame(list_container, fg_color=self.app.colors['surface'])
        button_container.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        self.app.edit_button = ctk.CTkButton(
            button_container, text="✏️ EDITAR", command=self.app.edit_command,
            fg_color=self.app.colors['accent'], hover_color='#0099cc',
            font=ctk.CTkFont(size=12, weight="bold"), width=120, height=35
        )
        self.app.edit_button.pack(pady=5, padx=5)

        self.app.remove_button = ctk.CTkButton(
            button_container, text="🗑️ REMOVER", command=self.app.remove_command,
            fg_color=self.app.colors['error'], hover_color='#cc4444',
            font=ctk.CTkFont(size=12, weight="bold"), width=120, height=35
        )
        self.app.remove_button.pack(pady=5, padx=5)

        self.app.reload_button = ctk.CTkButton(
            button_container, text="🔄 RECARREGAR", command=self.app.reload_commands,
            fg_color=self.app.colors['accent'], hover_color='#0099cc',
            font=ctk.CTkFont(size=12, weight="bold"), width=120, height=35
        )
        self.app.reload_button.pack(pady=5, padx=5)

        self.app.save_button = ctk.CTkButton(
            button_container, text="💾 SALVAR", command=self.app.save_commands,
            fg_color=self.app.colors['success'], hover_color='#00cc6a',
            font=ctk.CTkFont(size=12, weight="bold"), width=120, height=35
        )
        self.app.save_button.pack(pady=5, padx=5)