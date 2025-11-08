import tkinter as tk
import customtkinter as ctk

class NavigationFrame(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master, width=200, fg_color=controller.colors['surface'], corner_radius=0)
        self.controller = controller
        self.colors = controller.colors

        self.grid_rowconfigure(20, weight=1)

        title_label = ctk.CTkLabel(
            self, text="🎮 CHAT BOT",
            font=ctk.CTkFont(size=20, weight="bold"), text_color=self.colors['text_primary']
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 20))

        self.nav_btn_connect = ctk.CTkButton(
            self, text="Conexão", command=lambda: self.controller.select_frame_by_name("connect"),
            font=ctk.CTkFont(size=14, weight="bold"), height=40, corner_radius=8,
            fg_color=self.colors['twitch_purple'], hover_color=self.colors['twitch_purple_dark']
        )
        self.nav_btn_connect.grid(row=1, column=0, sticky="ew", padx=15, pady=5)

        self.nav_btn_commands = ctk.CTkButton(
            self, text="Comandos", command=lambda: self.controller.select_frame_by_name("commands"),
            font=ctk.CTkFont(size=14, weight="bold"), height=40, corner_radius=8,
            fg_color=self.colors['surface_dark'], hover_color=self.colors['surface_light']
        )
        self.nav_btn_commands.grid(row=2, column=0, sticky="ew", padx=15, pady=5)

        self.nav_btn_timers = ctk.CTkButton(
            self, text="Timers", command=lambda: self.controller.select_frame_by_name("timers"),
            font=ctk.CTkFont(size=14, weight="bold"), height=40, corner_radius=8,
            fg_color=self.colors['surface_dark'], hover_color=self.colors['surface_light']
        )
        self.nav_btn_timers.grid(row=3, column=0, sticky="ew", padx=15, pady=5)

        self.nav_btn_messages = ctk.CTkButton(
            self, text="Eventos", command=lambda: self.controller.select_frame_by_name("messages"),
            font=ctk.CTkFont(size=14, weight="bold"), height=40, corner_radius=8,
            fg_color=self.colors['surface_dark'], hover_color=self.colors['surface_light']
        )
        self.nav_btn_messages.grid(row=4, column=0, sticky="ew", padx=15, pady=5)

        self.nav_btn_chat = ctk.CTkButton(
            self, text="Chat", command=lambda: self.controller.select_frame_by_name("chat"),
            font=ctk.CTkFont(size=14, weight="bold"), height=40, corner_radius=8,
            fg_color=self.colors['surface_dark'], hover_color=self.colors['surface_light']
        )
        self.nav_btn_chat.grid(row=5, column=0, sticky="ew", padx=15, pady=5)

        self.nav_btn_rewards = ctk.CTkButton(
            self, text="Recompensas", command=lambda: self.controller.select_frame_by_name("rewards"),
            font=ctk.CTkFont(size=14, weight="bold"), height=40, corner_radius=8,
            fg_color=self.colors['surface_dark'], hover_color=self.colors['surface_light']
        )
        self.nav_btn_rewards.grid(row=6, column=0, sticky="ew", padx=15, pady=5)

        self.nav_btn_moderation = ctk.CTkButton(
            self, text="Moderação", command=lambda: self.controller.select_frame_by_name("moderação"),
            font=ctk.CTkFont(size=14, weight="bold"), height=40, corner_radius=8,
            fg_color=self.colors['surface_dark'], hover_color=self.colors['surface_light']
        )
        self.nav_btn_moderation.grid(row=7, column=0, sticky="ew", padx=15, pady=5)

        self.nav_btn_activity = ctk.CTkButton(
            self, text="Atividade", command=lambda: self.controller.select_frame_by_name("activity"),
            font=ctk.CTkFont(size=14, weight="bold"), height=40, corner_radius=8,
            fg_color=self.colors['surface_dark'], hover_color=self.colors['surface_light']
        )
        self.nav_btn_activity.grid(row=8, column=0, sticky="ew", padx=15, pady=5)

        self.nav_btn_tts = ctk.CTkButton(
            self, text="TTS (text-to-speech)",
            command=lambda: self.controller.select_frame_by_name("tts"),
            font=ctk.CTkFont(size=14, weight="bold"), height=40, corner_radius=8,
            fg_color=self.colors['surface_dark'], hover_color=self.colors['surface_light']
        )
        self.nav_btn_tts.grid(row=9, column=0, sticky="ew", padx=15, pady=5)

        self.nav_btn_points = ctk.CTkButton(
            self, text="Pontos",
            command=lambda: self.controller.select_frame_by_name("pontos"),
            font=ctk.CTkFont(size=14, weight="bold"), height=40, corner_radius=8,
            fg_color=self.colors['surface_dark'], hover_color=self.colors['surface_light']
        )
        self.nav_btn_points.grid(row=10, column=0, sticky="ew", padx=15, pady=5)

        self.status_label = ctk.CTkLabel(
            self, text="● OFFLINE", text_color=self.colors['error'],
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.status_label.grid(row=21, column=0, padx=20, pady=20, sticky="s")

    def update_button_colors(self, selected_name):
        """Atualiza a cor de fundo dos botões de navegação."""
        buttons = {
            "connect": self.nav_btn_connect,
            "commands": self.nav_btn_commands,
            "timers": self.nav_btn_timers,
            "messages": self.nav_btn_messages,
            "chat": self.nav_btn_chat,
            "rewards": self.nav_btn_rewards,
            "moderação": self.nav_btn_moderation,
            "activity": self.nav_btn_activity,
            "tts": self.nav_btn_tts,
            "pontos": self.nav_btn_points,
        }
        for name, button in buttons.items():
            if name == selected_name:
                button.configure(fg_color=self.colors['twitch_purple'])
            else:
                button.configure(fg_color=self.colors['surface_dark'])

    def update_status(self, text, color_key):
        """Atualiza o texto e a cor do label de status."""
        self.status_label.configure(text=text, text_color=self.colors.get(color_key, self.colors['error']))
