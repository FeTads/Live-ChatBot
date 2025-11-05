import tkinter as tk
import customtkinter as ctk

class TimersPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=app.colors['background'])
        self.app = app
        self.grid(row=0, column=0, sticky="nsew")

        main_page_frame = ctk.CTkFrame(self, fg_color=self.app.colors['surface'])
        main_page_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        timers_frame = ctk.CTkFrame(main_page_frame, fg_color=self.app.colors['surface'])
        timers_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)

        frame_title = ctk.CTkLabel(
            timers_frame, text="⏱️ TIMERS (Mensagens Automáticas)",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.app.colors['twitch_purple_light']
        )
        frame_title.pack(anchor=tk.W, padx=15, pady=(10, 5))

        info_label = ctk.CTkLabel(
            timers_frame, text="Envia mensagens em intervalos de tempo e linhas de chat.",
            font=ctk.CTkFont(size=12), text_color=self.app.colors['text_secondary']
        )
        info_label.pack(anchor=tk.W, padx=15, pady=(0, 10))

        add_timer_frame = ctk.CTkFrame(timers_frame, fg_color=self.app.colors['surface_dark'])
        add_timer_frame.pack(fill=tk.X, padx=15, pady=10)
        add_timer_frame.grid_columnconfigure(1, weight=1)
        add_timer_frame.grid_columnconfigure(3, weight=0)
        add_timer_frame.grid_columnconfigure(5, weight=0)

        ctk.CTkLabel(add_timer_frame, text="Nome:", font=ctk.CTkFont(size=12)).grid(
            row=0, column=0, sticky="w", padx=10, pady=5)
        self.new_timer_name_var = tk.StringVar()
        ctk.CTkEntry(
            add_timer_frame, textvariable=self.new_timer_name_var,
            placeholder_text="Nome do timer (ex: !redes)", fg_color=self.app.colors['surface_light'],
            border_color=self.app.colors['twitch_purple']
        ).grid(row=0, column=1, columnspan=5, sticky="ew", padx=10, pady=5)

        ctk.CTkLabel(add_timer_frame, text="Mensagem:", font=ctk.CTkFont(size=12)).grid(
            row=1, column=0, sticky="w", padx=10, pady=5)
        self.new_timer_msg_var = tk.StringVar()
        ctk.CTkEntry(
            add_timer_frame, textvariable=self.new_timer_msg_var,
            placeholder_text="Mensagem a ser enviada no chat...", fg_color=self.app.colors['surface_light'],
            border_color=self.app.colors['twitch_purple']
        ).grid(row=1, column=1, columnspan=5, sticky="ew", padx=10, pady=5)

        ctk.CTkLabel(add_timer_frame, text="Intervalo (min):", font=ctk.CTkFont(size=12)).grid(
            row=2, column=0, sticky="w", padx=10, pady=5)
        self.new_timer_interval_var = tk.StringVar(value="15")
        ctk.CTkEntry(
            add_timer_frame, textvariable=self.new_timer_interval_var,
            fg_color=self.app.colors['surface_light'], width=70
        ).grid(row=2, column=1, sticky="w", padx=10, pady=5)

        ctk.CTkLabel(add_timer_frame, text="Linhas Mínimas:", font=ctk.CTkFont(size=12)).grid(
            row=2, column=2, sticky="w", padx=10, pady=5)
        self.new_timer_lines_var = tk.StringVar(value="5")
        ctk.CTkEntry(
            add_timer_frame, textvariable=self.new_timer_lines_var,
            fg_color=self.app.colors['surface_light'], width=70
        ).grid(row=2, column=3, sticky="w", padx=10, pady=5)

        add_button = ctk.CTkButton(
            add_timer_frame, text="➕ ADICIONAR TIMER", command=self.app.add_new_timer,
            fg_color=self.app.colors['success'], hover_color='#00cc6a',
            font=ctk.CTkFont(size=12, weight="bold"), height=35
        )
        add_button.grid(row=2, column=4, columnspan=2, sticky="e", padx=10, pady=5)

        list_frame = ctk.CTkFrame(timers_frame, fg_color=self.app.colors['surface'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 10))

        search_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        search_frame.pack(fill=tk.X, padx=0, pady=(5, 10))
        search_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            search_frame,
            text="🔎 Procurar:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=(0, 10))

        self.search_var = tk.StringVar()
        search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            placeholder_text="Filtrar por nome ou mensagem...",
            fg_color=self.app.colors['surface_light']
        )
        search_entry.grid(row=0, column=1, sticky="ew")
        search_entry.bind("<KeyRelease>", lambda e: self.app.refresh_timers_list()) 

        list_container = ctk.CTkFrame(list_frame, fg_color=self.app.colors['surface'])
        list_container.pack(fill=tk.BOTH, expand=True)

        self.timers_scroll_frame = ctk.CTkScrollableFrame(
            list_container,
            fg_color=self.app.colors['surface_light'],
            border_width=1,
            border_color=self.app.colors['surface_lighter']
        )
        self.timers_scroll_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10), pady=5)
        self.timers_scroll_frame.grid_columnconfigure(0, weight=1)

        button_container = ctk.CTkFrame(list_container, fg_color=self.app.colors['surface'])
        button_container.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        edit_button = ctk.CTkButton(
            button_container, text="✏️ EDITAR", command=self.app.open_edit_timer_dialog,
            fg_color=self.app.colors['accent'], hover_color='#0099cc',
            font=ctk.CTkFont(size=12, weight="bold"), width=120, height=35
        )
        edit_button.pack(pady=5, padx=5, anchor="n")

        remove_button = ctk.CTkButton(
            button_container, text="🗑️ REMOVER", command=self.app.remove_timer,
            fg_color=self.app.colors['error'], hover_color='#cc4444',
            font=ctk.CTkFont(size=12, weight="bold"), width=120, height=35
        )
        remove_button.pack(pady=5, padx=5, anchor="n")
        
        reload_button = ctk.CTkButton(
            button_container, text="🔄 RECARREGAR", command=self.app.reload_timers,
            fg_color=self.app.colors['accent'], hover_color='#0099cc',
            font=ctk.CTkFont(size=12, weight="bold"), width=120, height=35
        )
        reload_button.pack(pady=5, padx=5, anchor="n")

        save_button = ctk.CTkButton(
            button_container, text="💾 SALVAR", command=self.app.save_timers,
            fg_color=self.app.colors['success'], hover_color='#00cc6a',
            font=ctk.CTkFont(size=12, weight="bold"), width=120, height=35
        )
        save_button.pack(pady=5, padx=5, anchor="n")