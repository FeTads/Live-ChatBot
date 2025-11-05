import tkinter as tk
import customtkinter as ctk

class MessagesPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=app.colors['background'])
        self.app = app
        self.grid(row=0, column=0, sticky="nsew")

        main_page_frame = ctk.CTkFrame(self, fg_color=self.app.colors['surface'])
        main_page_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        messages_frame = ctk.CTkFrame(main_page_frame, fg_color=self.app.colors['surface'])
        messages_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)

        frame_title = ctk.CTkLabel(
            messages_frame, text="💬 MENSAGENS DE EVENTOS",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.app.colors['twitch_purple_light']
        )
        frame_title.pack(anchor=tk.W, padx=15, pady=(10, 5))

        info_label = ctk.CTkLabel(
            messages_frame, text="Use {user}, {tier}, {raider}, {viewers}, {bits}, {message}, {input}.",
            font=ctk.CTkFont(size=12), text_color=self.app.colors['text_secondary']
        )
        info_label.pack(anchor=tk.W, padx=15, pady=(0, 10))

        scroll_frame = ctk.CTkScrollableFrame(messages_frame, fg_color=self.app.colors['surface_light'])
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        scroll_frame.grid_columnconfigure(2, weight=1)
        
        current_row = 0

        self.msg_follow_enabled_var = tk.BooleanVar(value=self.app.settings.get('msg_follow_enabled', True))
        ctk.CTkLabel(scroll_frame, text="✨ Novo Follow:", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=current_row, column=0, sticky="w", padx=10, pady=(10, 5))
        ctk.CTkSwitch(scroll_frame, variable=self.msg_follow_enabled_var, text="").grid(
            row=current_row, column=1, sticky="w", padx=5, pady=(10, 5))
        self.msg_follow_var = tk.StringVar(value=self.app.settings.get('msg_follow', 'Obrigado pelo follow, @{user}! <3'))
        ctk.CTkEntry(scroll_frame, textvariable=self.msg_follow_var, fg_color=self.app.colors['surface_lighter'], border_color=self.app.colors['twitch_purple']).grid(
            row=current_row + 1, column=0, columnspan=3, sticky="ew", padx=10, pady=(0, 10))
        current_row += 2

        self.msg_sub_enabled_var = tk.BooleanVar(value=self.app.settings.get('msg_sub_enabled', True))
        ctk.CTkLabel(scroll_frame, text="⭐ Novo Sub:", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=current_row, column=0, sticky="w", padx=10, pady=(10, 5))
        ctk.CTkSwitch(scroll_frame, variable=self.msg_sub_enabled_var, text="").grid(
            row=current_row, column=1, sticky="w", padx=5, pady=(10, 5))
        self.msg_sub_var = tk.StringVar(value=self.app.settings.get('msg_sub', 'WOAH! Muito obrigado pelo Sub (Tier {tier}), @{user}!'))
        ctk.CTkEntry(scroll_frame, textvariable=self.msg_sub_var, fg_color=self.app.colors['surface_lighter'], border_color=self.app.colors['twitch_purple']).grid(
            row=current_row + 1, column=0, columnspan=3, sticky="ew", padx=10, pady=(0, 10))
        current_row += 2

        self.msg_gift_enabled_var = tk.BooleanVar(value=self.app.settings.get('msg_gift_enabled', True))
        ctk.CTkLabel(scroll_frame, text="🎁 Sub de Presente:", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=current_row, column=0, sticky="w", padx=10, pady=(10, 5))
        ctk.CTkSwitch(scroll_frame, variable=self.msg_gift_enabled_var, text="").grid(
            row=current_row, column=1, sticky="w", padx=5, pady=(10, 5))
        self.msg_gift_sub_var = tk.StringVar(value=self.app.settings.get('msg_gift_sub', 'WOAH! @{user} ganhou um Sub de presente! <3'))
        ctk.CTkEntry(scroll_frame, textvariable=self.msg_gift_sub_var, fg_color=self.app.colors['surface_lighter'], border_color=self.app.colors['twitch_purple']).grid(
            row=current_row + 1, column=0, columnspan=3, sticky="ew", padx=10, pady=(0, 10))
        current_row += 2

        self.msg_raid_enabled_var = tk.BooleanVar(value=self.app.settings.get('msg_raid_enabled', True))
        ctk.CTkLabel(scroll_frame, text="⚔️ Nova Raid:", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=current_row, column=0, sticky="w", padx=10, pady=(10, 5))
        ctk.CTkSwitch(scroll_frame, variable=self.msg_raid_enabled_var, text="").grid(
            row=current_row, column=1, sticky="w", padx=5, pady=(10, 5))
        self.msg_raid_var = tk.StringVar(value=self.app.settings.get('msg_raid', 'RAID! Bem-vindos, time do @{raider}!'))
        ctk.CTkEntry(scroll_frame, textvariable=self.msg_raid_var, fg_color=self.app.colors['surface_lighter'], border_color=self.app.colors['twitch_purple']).grid(
            row=current_row + 1, column=0, columnspan=3, sticky="ew", padx=10, pady=(0, 10))
        current_row += 2
        
        ctk.CTkFrame(scroll_frame, height=2, fg_color=self.app.colors['surface_dark']).grid(
            row=current_row, column=0, columnspan=3, sticky="ew", padx=10, pady=(15, 10))
        current_row += 1

        ctk.CTkLabel(scroll_frame, text="💎 Alerta de Bits (Chat):", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=current_row, column=0, sticky="w", padx=10, pady=(10, 5))
        self.msg_cheer_alert_enabled_var = tk.BooleanVar(value=self.app.settings.get('msg_cheer_alert_enabled', False))
        ctk.CTkSwitch(scroll_frame, variable=self.msg_cheer_alert_enabled_var, text="").grid(
            row=current_row, column=1, sticky="w", padx=5, pady=(10, 5))
        
        self.msg_cheer_alert_var = tk.StringVar(value=self.app.settings.get('msg_cheer_alert', '{user} cheerou {bits} bits!'))
        ctk.CTkEntry(scroll_frame, textvariable=self.msg_cheer_alert_var, fg_color=self.app.colors['surface_lighter'], border_color=self.app.colors['twitch_purple']).grid(
            row=current_row + 1, column=0, columnspan=3, sticky="ew", padx=10, pady=(0, 10))
        current_row += 2

        ctk.CTkLabel(scroll_frame, text="🗣️ TTS de Bits:", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=current_row, column=0, sticky="w", padx=10, pady=(10, 5))
        self.tts_cheer_enabled_var = tk.BooleanVar(value=self.app.settings.get('tts_cheer_enabled', False))
        ctk.CTkSwitch(scroll_frame, variable=self.tts_cheer_enabled_var, text="").grid(
            row=current_row, column=1, sticky="w", padx=5, pady=(10, 5))
        
        self.tts_cheer_format_var = tk.StringVar(value=self.app.settings.get('tts_cheer_format', '{user} disse: {message}'))
        ctk.CTkEntry(scroll_frame, textvariable=self.tts_cheer_format_var, fg_color=self.app.colors['surface_lighter'], border_color=self.app.colors['twitch_purple']).grid(
            row=current_row + 1, column=0, columnspan=3, sticky="ew", padx=10, pady=(0, 10))
        current_row += 2
        
        ctk.CTkLabel(scroll_frame, text="Bits Mínimos para TTS:", font=ctk.CTkFont(size=12)).grid(
            row=current_row, column=0, sticky="w", padx=10, pady=5)
        self.tts_cheer_min_bits_var = tk.StringVar(value=str(self.app.settings.get('tts_cheer_min_bits', 100)))
        ctk.CTkEntry(
            scroll_frame, textvariable=self.tts_cheer_min_bits_var,
            fg_color=self.app.colors['surface_lighter'], width=80
        ).grid(row=current_row, column=1, sticky="w", padx=5, pady=5)
        current_row += 1


        save_button = ctk.CTkButton(
            messages_frame, text="💾 SALVAR MENSAGENS",
            command=self.app.save_settings,
            fg_color=self.app.colors['success'], hover_color='#00cc6a',
            font=ctk.CTkFont(size=12, weight="bold"), height=35
        )
        save_button.pack(anchor="e", padx=15, pady=(0, 10))