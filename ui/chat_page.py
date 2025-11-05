import tkinter as tk
from tkinter import scrolledtext
import customtkinter as ctk

class ChatPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=app.colors['background'])
        self.app = app
        self.grid(row=0, column=0, sticky="nsew")

        main_page_frame = ctk.CTkFrame(self, fg_color=self.app.colors['surface'])
        main_page_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        chat_frame = ctk.CTkFrame(main_page_frame, fg_color=self.app.colors['surface'])
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)
        chat_frame.grid_rowconfigure(1, weight=1)
        chat_frame.grid_columnconfigure(0, weight=1)
        chat_frame.grid_columnconfigure(1, weight=0)

        frame_title = ctk.CTkLabel(
            chat_frame, text="🗨️ CHAT EM TEMPO REAL",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.app.colors['twitch_purple_light']
        )
        frame_title.grid(row=0, column=0, sticky="w", padx=15, pady=(10, 5))

        clear_button = ctk.CTkButton(
            chat_frame,
            text="🧹 LIMPAR CHAT",
            command=self.app.clear_chat_display,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=self.app.colors['error'],
            hover_color='#cc4444',
            text_color=self.app.colors['text_primary'],
            width=120,
            height=35
        )
        clear_button.grid(row=0, column=1, sticky="e", padx=(0, 15), pady=(10, 5))

        text_container = ctk.CTkFrame(chat_frame, fg_color=self.app.colors['surface_light'])
        text_container.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=15, pady=(0, 10))

        self.chat_text = scrolledtext.ScrolledText(
            text_container, bg=self.app.colors['surface_light'], fg=self.app.colors['text_primary'],
            insertbackground=self.app.colors['text_primary'], font=('Consolas', 11),
            relief='flat', borderwidth=0, padx=10, pady=10,
            state=tk.DISABLED, cursor="arrow"
        )
        self.chat_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        input_frame = ctk.CTkFrame(chat_frame, fg_color=self.app.colors['surface'])
        input_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=15, pady=(0, 10))

        self.message_var = tk.StringVar()
        self.message_entry = ctk.CTkEntry(
            input_frame, textvariable=self.message_var,
            placeholder_text="Digite sua mensagem...", fg_color=self.app.colors['surface_light'],
            border_color=self.app.colors['twitch_purple'], text_color=self.app.colors['text_primary'],
            height=35
        )
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.message_entry.bind('<Return>', self.app.send_message)

        self.send_button = ctk.CTkButton(
            input_frame, text="📤 ENVIAR", command=self.app.send_message,
            fg_color=self.app.colors['twitch_purple'], hover_color=self.app.colors['twitch_purple_dark'],
            font=ctk.CTkFont(size=12, weight="bold"),
            width=100, height=35
        )
        self.send_button.pack(side=tk.RIGHT)