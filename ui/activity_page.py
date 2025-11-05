import tkinter as tk
import customtkinter as ctk

class ActivityPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=app.colors['background'])
        self.app = app
        self.grid(row=0, column=0, sticky="nsew")

        main_page_frame = ctk.CTkFrame(self, fg_color=self.app.colors['surface'])
        main_page_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        activity_display_frame = ctk.CTkFrame(main_page_frame, fg_color=self.app.colors['surface'])
        activity_display_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)
        activity_display_frame.grid_rowconfigure(1, weight=1)
        activity_display_frame.grid_columnconfigure(0, weight=1)

        frame_title = ctk.CTkLabel(
            activity_display_frame, text="📊 FEED DE ATIVIDADES",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.app.colors['twitch_purple_light']
        )
        frame_title.grid(row=0, column=0, sticky="w", padx=15, pady=(10, 15))

        self.activity_scroll_frame = ctk.CTkScrollableFrame(
            activity_display_frame,
            fg_color=self.app.colors['surface_light'],
            border_width=1,
            border_color=self.app.colors['surface_lighter']
        )
        self.activity_scroll_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        self.activity_scroll_frame.grid_columnconfigure(0, weight=1)