import tkinter as tk
import customtkinter as ctk

class RewardsPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=app.colors['background'])
        self.app = app
        self.grid(row=0, column=0, sticky="nsew")

        main_page_frame = ctk.CTkFrame(self, fg_color=self.app.colors['surface'])
        main_page_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        rewards_conf_frame = ctk.CTkFrame(main_page_frame, fg_color=self.app.colors['surface'])
        rewards_conf_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)

        frame_title = ctk.CTkLabel(
            rewards_conf_frame, text="🎁 RECOMPENSAS E SONS",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.app.colors['twitch_purple_light']
        )
        frame_title.pack(anchor=tk.W, padx=15, pady=(10, 5))

        info_label = ctk.CTkLabel(
            rewards_conf_frame, text="Associe o nome exato da recompensa a uma mensagem e/ou um som (.wav ou .mp3).",
            font=ctk.CTkFont(size=12), text_color=self.app.colors['text_secondary']
        )
        info_label.pack(anchor=tk.W, padx=15, pady=(0, 10))

        add_reward_frame = ctk.CTkFrame(rewards_conf_frame, fg_color=self.app.colors['surface'])
        add_reward_frame.pack(fill=tk.X, padx=15, pady=10)
        add_reward_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(add_reward_frame, text="Nome Recompensa:", font=ctk.CTkFont(size=12)).grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=5)
        self.new_reward_name_var = tk.StringVar()
        ctk.CTkEntry(
            add_reward_frame, textvariable=self.new_reward_name_var,
            placeholder_text="Nome exato da recompensa...", fg_color=self.app.colors['surface_light'],
            border_color=self.app.colors['twitch_purple']
        ).grid(row=0, column=1, columnspan=2, sticky="ew", pady=5)

        ctk.CTkLabel(add_reward_frame, text="Mensagem (Opc.):", font=ctk.CTkFont(size=12)).grid(
            row=1, column=0, sticky="w", padx=(0, 10), pady=5)
        self.new_reward_msg_var = tk.StringVar()
        ctk.CTkEntry(
            add_reward_frame, textvariable=self.new_reward_msg_var,
            placeholder_text="Mensagem chat (use {user}, {input})...", fg_color=self.app.colors['surface_light'],
            border_color=self.app.colors['twitch_purple']
        ).grid(row=1, column=1, columnspan=2, sticky="ew", pady=5)

        ctk.CTkLabel(add_reward_frame, text="Som (Opcional):", font=ctk.CTkFont(size=12)).grid(
            row=2, column=0, sticky="w", padx=(0, 10), pady=5)
        self.new_reward_sound_var = tk.StringVar()
        sound_entry = ctk.CTkEntry(
            add_reward_frame, textvariable=self.new_reward_sound_var,
            placeholder_text="Caminho para .wav ou .mp3...", fg_color=self.app.colors['surface_light'],
            border_color=self.app.colors['twitch_purple']
        )
        sound_entry.grid(row=2, column=1, sticky="ew", pady=5)

        browse_button = ctk.CTkButton(
            add_reward_frame, text="Procurar...", command=self.app.browse_sound_file,
            font=ctk.CTkFont(size=11), width=80, height=30
        )
        browse_button.grid(row=2, column=2, sticky="w", padx=(5, 0), pady=5)

        add_button = ctk.CTkButton(
            add_reward_frame, text="➕ ADICIONAR RECOMPENSA", command=self.app.add_reward_action,
            fg_color=self.app.colors['success'], hover_color='#00cc6a',
            font=ctk.CTkFont(size=12, weight="bold"), height=35
        )
        add_button.grid(row=3, column=0, columnspan=3, pady=10)

        list_frame = ctk.CTkFrame(rewards_conf_frame, fg_color=self.app.colors['surface'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 10))

        ctk.CTkLabel(list_frame, text="📋 Recompensas Configuradas:",
                       font=ctk.CTkFont(size=14, weight="bold")).pack(anchor=tk.W, pady=(0, 5))

        list_container = ctk.CTkFrame(list_frame, fg_color=self.app.colors['surface'])
        list_container.pack(fill=tk.BOTH, expand=True)

        self.rewards_scroll_frame = ctk.CTkScrollableFrame(
            list_container,
            fg_color=self.app.colors['surface_light'],
            border_width=1,
            border_color=self.app.colors['surface_lighter']
        )
        self.rewards_scroll_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10), pady=5)
        self.rewards_scroll_frame.grid_columnconfigure(0, weight=1)

        remove_button_container = ctk.CTkFrame(list_container, fg_color=self.app.colors['surface'])
        remove_button_container.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        edit_button = ctk.CTkButton(
            remove_button_container, text="✏️ EDITAR", command=self.app.edit_reward,
            fg_color=self.app.colors['accent'], hover_color='#0099cc',
            font=ctk.CTkFont(size=12, weight="bold"), width=120, height=35
        )
        edit_button.pack(pady=5, padx=5, anchor="n")

        remove_button = ctk.CTkButton(
            remove_button_container, text="🗑️ REMOVER", command=self.app.remove_reward_action,
            fg_color=self.app.colors['error'], hover_color='#cc4444',
            font=ctk.CTkFont(size=12, weight="bold"), width=120, height=35
        )
        remove_button.pack(pady=5, padx=5, anchor="n")