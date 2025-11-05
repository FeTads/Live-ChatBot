import tkinter as tk
import customtkinter as ctk

class TTSPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=app.colors['background'])
        self.app = app
        self.grid(row=0, column=0, sticky="nsew")
        self.voice_map = {
            "Português (Brasil)": "pt-br",
            "Português (Portugal)": "pt",
            "Inglês (EUA)": "en-us",
            "Inglês (Reino Unido)": "en-uk",
            "Espanhol (Espanha)": "es-es",
            "Espanhol (México)": "es-mx",
            "Japonês": "ja"
        }

        self.reverse_voice_map = {v: k for k, v in self.voice_map.items()}

        main_page_frame = ctk.CTkFrame(self, fg_color=self.app.colors['surface'])
        main_page_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tts_frame = ctk.CTkFrame(main_page_frame, fg_color=self.app.colors['surface'])
        tts_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)

        frame_title = ctk.CTkLabel(
            tts_frame, text="🗣️ TEXT-TO-SPEECH (TTS)",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.app.colors['twitch_purple_light']
        )
        frame_title.pack(anchor=tk.W, padx=15, pady=(10, 5))
        
        info_label = ctk.CTkLabel(
            tts_frame, text="Permite que viewers resgatem uma recompensa de pontos para ter sua mensagem lida em voz alta.",
            font=ctk.CTkFont(size=12), text_color=self.app.colors['text_secondary']
        )
        info_label.pack(anchor=tk.W, padx=15, pady=(0, 20))

        config_frame = ctk.CTkFrame(tts_frame, fg_color=self.app.colors['surface_light'])
        config_frame.pack(fill=tk.X, padx=15, pady=10)
        config_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(config_frame, text="Ativar TTS:", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=15, pady=15)

        self.tts_enabled_var = tk.BooleanVar(value=self.app.settings.get('tts_enabled', False))
        ctk.CTkSwitch(
            config_frame, variable=self.tts_enabled_var, text="",
            onvalue=True, offvalue=False,
            progress_color=self.app.colors['success']
        ).grid(row=0, column=1, sticky="w", padx=15, pady=15)

        ctk.CTkLabel(config_frame, text="Nome da Recompensa:", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=1, column=0, sticky="w", padx=15, pady=15)
        
        self.tts_reward_name_var = tk.StringVar(value=self.app.settings.get('tts_reward_name', ''))
        ctk.CTkEntry(
            config_frame, textvariable=self.tts_reward_name_var,
            placeholder_text="Nome exato da recompensa que ativa o TTS...",
            fg_color=self.app.colors['surface_lighter'], border_color=self.app.colors['twitch_purple']
        ).grid(row=1, column=1, sticky="ew", padx=15, pady=15)

        ctk.CTkLabel(config_frame, text="Voz (Idioma):", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=2, column=0, sticky="w", padx=15, pady=15)
        
        ctk.CTkLabel(config_frame, text="Volume:", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=3, column=0, sticky="w", padx=15, pady=15)

        saved_volume_percent = self.app.settings.get('tts_volume', 50)
        self.app.mixer_volume = saved_volume_percent / 100.0
        self.tts_volume_var = tk.IntVar(value=saved_volume_percent)
        
        self.tts_volume_label = ctk.CTkLabel(
            config_frame, text=f"{saved_volume_percent}%",
            font=ctk.CTkFont(size=12), width=40
        )
        self.tts_volume_label.grid(row=3, column=2, sticky="w", padx=(5, 15))

        tts_volume_slider = ctk.CTkSlider(
            config_frame,
            from_=0, to=100, number_of_steps=100,
            variable=self.tts_volume_var,
            command=self.app.update_tts_volume 
        )
        tts_volume_slider.grid(row=3, column=1, sticky="ew", padx=15, pady=15)
        
        saved_lang_code = self.app.settings.get('tts_voice_lang', 'pt-br')
        default_voice_name = self.reverse_voice_map.get(saved_lang_code, "Português (Brasil)")
        
        self.tts_voice_var = tk.StringVar(value=default_voice_name)
        ctk.CTkOptionMenu(
            config_frame,
            variable=self.tts_voice_var,
            values=list(self.voice_map.keys()),
            fg_color=self.app.colors['surface_lighter'],
            button_color=self.app.colors['twitch_purple'],
            button_hover_color=self.app.colors['twitch_purple_dark']
        ).grid(row=2, column=1, sticky="w", padx=15, pady=15)

        save_button = ctk.CTkButton(
            tts_frame, text="💾 SALVAR CONFIGURAÇÕES",
            command=self.app.save_settings,
            fg_color=self.app.colors['success'], hover_color='#00cc6a',
            font=ctk.CTkFont(size=12, weight="bold"), height=35
        )
        save_button.pack(anchor="e", padx=15, pady=(10, 10))