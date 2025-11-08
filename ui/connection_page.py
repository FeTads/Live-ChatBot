import tkinter as tk
import customtkinter as ctk
import webbrowser
from PIL import Image 
import os 
import textwrap
import sys

from ui.components.tooltip import attach_tooltip

def resource_path(relative_path):
    """ Retorna o caminho absoluto para o recurso, funcionando em dev e no PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class ConnectionPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=app.colors['background'])
        self.app = app
        self.grid(row=0, column=0, sticky="nsew")

        self.carousel_images = []
        self.current_image_index = 0
        self.carousel_image_label = None

        main_page_frame = ctk.CTkFrame(self, fg_color="transparent") 
        main_page_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        connection_frame = ctk.CTkFrame(main_page_frame, fg_color=self.app.colors['surface'])
        connection_frame.pack(fill=tk.X, pady=(0, 10), anchor="n", side=tk.TOP)
        
        frame_title = ctk.CTkLabel(
            connection_frame, text="🔗 CONEXÃO",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.app.colors['twitch_purple_light']
        )
        frame_title.pack(anchor=tk.W, padx=15, pady=(10, 5))

        input_frame = ctk.CTkFrame(connection_frame, fg_color=self.app.colors['surface'])
        input_frame.pack(fill=tk.X, padx=15, pady=10)

        profiles_frame = ctk.CTkFrame(connection_frame, fg_color=self.app.colors['surface'])
        profiles_frame.pack(fill=tk.X, padx=15, pady=(0,10))
        ctk.CTkLabel(profiles_frame, text="📦 Perfis do Bot", font=ctk.CTkFont(size=13, weight="bold")).grid(row=0, column=0, sticky="w", padx=(8,8), pady=(8,4))
        profiles_frame.grid_columnconfigure(1, weight=1)
        export_btn = ctk.CTkButton(profiles_frame, text="💾 Exportar Perfil", width=160,
                                   command=self.app.export_profile,
                                   fg_color=self.app.colors['accent'], hover_color='#0099cc')
        import_btn = ctk.CTkButton(profiles_frame, text="📂 Importar Perfil", width=160,
                                   command=self.app.import_profile,
                                   fg_color=self.app.colors['accent'], hover_color='#0099cc')
        export_btn.grid(row=1, column=0, padx=8, pady=(0,8), sticky="w")
        import_btn.grid(row=1, column=1, padx=8, pady=(0,8), sticky="w")
    
        input_frame.grid_columnconfigure(1, weight=1)
        input_frame.grid_columnconfigure(2, weight=0)

        ctk.CTkLabel(input_frame, text="📺 Canal:", font=ctk.CTkFont(size=12)).grid(
            row=0, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.app.channel_var = tk.StringVar(value=self.app.settings.get('last_channel', ''))
        self.app.channel_entry = ctk.CTkEntry(
            input_frame, textvariable=self.app.channel_var, width=200,
            placeholder_text="Nome do canal...", fg_color=self.app.colors['surface_light'],
            border_color=self.app.colors['twitch_purple'], text_color=self.app.colors['text_primary']
        )
        self.app.channel_entry.grid(row=0, column=1, columnspan=2, sticky="ew", pady=5)
        attach_tooltip(
            self.app.channel_entry, "Nome do canal bot",
            "Aqui você deve inserir o nome do canal Twitch onde o bot irá operar.\n",
            colors=self.app.colors, delay=350, wraplength=360
        )

        ctk.CTkLabel(input_frame, text="🔑 Token:", font=ctk.CTkFont(size=12)).grid(
            row=1, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.app.token_var = tk.StringVar(value=self.app.settings.get('last_token', ''))
        self.app.token_entry = ctk.CTkEntry(
            input_frame, textvariable=self.app.token_var,
            placeholder_text="Token OAuth...", show="•", fg_color=self.app.colors['surface_light'],
            border_color=self.app.colors['twitch_purple'], text_color=self.app.colors['text_primary']
        )
        self.app.token_entry.grid(row=1, column=1, sticky="ew", pady=5)
        attach_tooltip(
            self.app.token_entry, "Token",
            "O token OAuth é necessário para autenticar o bot na Twitch.\n"
            "ESSE TOKEN É SECRETO! NÃO COMPARTILHE COM NINGUÉM.",
            colors=self.app.colors, delay=350, wraplength=360
        )

        token_button = ctk.CTkButton(
            input_frame, text="Gerar Token 🔑", text_color=self.app.colors['background'],
            command=lambda: webbrowser.open_new_tab("https://twitchtokengenerator.com/"),
            font=ctk.CTkFont(size=11), fg_color=self.app.colors['success'],
            hover_color=self.app.colors['accent'], width=100,
            height=30
        )
        token_button.grid(row=1, column=2, sticky="w", padx=(5, 0), pady=5)

        button_frame = ctk.CTkFrame(connection_frame, fg_color=self.app.colors['surface'])
        button_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        self.app.start_button = ctk.CTkButton(
            button_frame, text="🎮 CONECTAR", command=self.app.start_bot,
            fg_color=self.app.colors['twitch_purple'], hover_color=self.app.colors['twitch_purple_dark'],
            font=ctk.CTkFont(size=12, weight="bold"), width=120, height=35
        )
        self.app.start_button.pack(side=tk.LEFT, padx=(0, 10))
        self.app.stop_button = ctk.CTkButton(
            button_frame, text="⏹️ PARAR", command=self.app.stop_bot, state="disabled",
            fg_color=self.app.colors['error'], hover_color=self.app.colors['twitch_purple'],
            font=ctk.CTkFont(size=12, weight="bold"), width=120, height=35
        )
        self.app.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        self.app.help_button = ctk.CTkButton(
            button_frame, text="📖 AJUDA", command=self.app.show_help,
            fg_color=self.app.colors['surface_light'], hover_color=self.app.colors['accent'],
            font=ctk.CTkFont(size=12, weight="bold"), width=120, height=35
        )
        self.app.help_button.pack(side=tk.LEFT)

        tutorial_frame = ctk.CTkFrame(main_page_frame, fg_color=self.app.colors['surface_dark'])
        tutorial_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0), side=tk.BOTTOM) 

        tutorial_frame.grid_rowconfigure(1, weight=1)
        tutorial_frame.grid_columnconfigure(0, weight=1)
        tutorial_frame.grid_columnconfigure(1, weight=1)

        tutorial_title = ctk.CTkLabel(
            tutorial_frame, text="💡 Tutorial: Como Gerar seu Token",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.app.colors['text_secondary']
        )
        tutorial_title.grid(row=0, column=0, columnspan=2, sticky="w", padx=15, pady=(10, 5))

        instructions_frame = ctk.CTkFrame(tutorial_frame, fg_color="transparent")
        instructions_frame.grid(row=1, column=0, sticky="nsew", padx=(15, 5), pady=(5, 15))
        instructions_frame.grid_rowconfigure(0, weight=1)
        instructions_frame.grid_columnconfigure(0, weight=1)

        instructions = """
            1. Clique no botão "Gerar Token 🔑".
            (Uma nova aba abrirá no seu navegador).

            2. No site, clique em "Bot Chat Token".
                2.1 Faça login com sua conta Twitch, se solicitado.

            3. Desça a pagina e procure por "Available Token Scopes":
                3.1 Marque "Select All" mais abaixo na pagina.

            4. Clique em "Generate Token!" e autorize a conexão.

            5. Copie o token 'Access Token' e cole no campo "Token" acima.

            6. Insira o nome do seu canal no campo "Canal".

            7. Clique em "🎮 CONECTAR" para iniciar o bot!

            8. Divirta-se com seu bot no chat do Twitch!
        """

        tutorial_text = ctk.CTkTextbox(
            instructions_frame,
            font=ctk.CTkFont(family="Consolas", size=13),
            fg_color=self.app.colors['surface_light'],
            text_color=self.app.colors['text_primary'],
            wrap="word",
            corner_radius=8
        )
        tutorial_text.insert("1.0", textwrap.dedent(instructions))
        tutorial_text.configure(state="disabled")
        tutorial_text.grid(row=0, column=0, sticky="nsew")

        carousel_frame = ctk.CTkFrame(tutorial_frame, fg_color="transparent")
        carousel_frame.grid(row=1, column=1, sticky="nsew", padx=(0, 5), pady=(0, 5))
        carousel_frame.grid_rowconfigure(0, weight=1)
        carousel_frame.grid_columnconfigure(0, weight=1)

        self.carousel_image_label = ctk.CTkLabel(
            carousel_frame,
            text="Carregando tutorial..."
        )
        self.carousel_image_label.grid(row=0, column=0, sticky="nsew")

        self._load_carousel_images()
        if self.carousel_images: 
            self._start_carousel_loop()
        else:
            self.carousel_image_label.configure(
                text="[Erro: Nenhuma imagem de tutorial \nencontrada na pasta /assets/]",
                fg_color=self.app.colors['surface'],
                text_color=self.app.colors['text_secondary'],
                corner_radius=8
            )
    
    def _load_carousel_images(self):
        """Carrega as imagens do tutorial em memória."""
        image_names = [
            "images/tut1.png", 
            "images/tut2.png", 
            "images/tut3.png", 
            "images/tut4.png"
        ]

        for img_path in image_names:
            img_path_absolute = resource_path(img_path)
            if os.path.exists(img_path_absolute):
                try:
                    img = ctk.CTkImage(
                        light_image=Image.open(img_path_absolute),
                        size=(450, 350)
                    )
                    self.carousel_images.append(img)
                except Exception as e:
                    print(f"Erro ao carregar imagem {img_path_absolute}: {e}")
            else:
                print(f"Imagem não encontrada: {img_path_absolute}")
        
        if self.carousel_images:
            self.carousel_image_label.configure(text="")
        
    def _start_carousel_loop(self):
        """Inicia o loop 'after' para o carrossel."""
        if not self.carousel_images:
            return 

        try:
            image_to_show = self.carousel_images[self.current_image_index]
            self.carousel_image_label.configure(image=image_to_show)
            self.current_image_index = (self.current_image_index + 1) % len(self.carousel_images)
            self.after(2000, self._start_carousel_loop)
            
        except Exception as e:
            print(f"Erro no loop do carrossel (provavelmente janela fechada): {e}")