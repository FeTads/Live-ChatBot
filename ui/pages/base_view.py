from collections import deque
import queue
import textwrap
from tkinter import messagebox
import customtkinter as ctk
import tkinter as tk

from ui.activity_page import ActivityPage
from ui.chat_page import ChatPage
from ui.commands_page import CommandsPage
from ui.connection_page import ConnectionPage
from ui.custom_dialog import CustomDialog
from ui.messages_page import MessagesPage
from ui.navigation_frame import NavigationFrame
from ui.reward_page import RewardsPage
from ui.moderation_page import ModerationPage
from ui.timers_page import TimersPage
from ui.tts_page import TTSPage
from ui.points_page import PointsPage
from ui.giveaways_page import GiveawaysPage

class ModernTwitchBaseView(ctk.CTk):
        def __init__(self, root=None, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.root = root or self
            self.root.title("Twitch Chat Bot v1.0.1")
            self.root.geometry("1100x750")
            self.root.minsize(900, 600)

            self.setup_custom_theme()

            self.bot = None
            self.eventsub = None
            self.is_running = False
            self.thread = None
            self.eventsub_thread = None
            self._update_timestamps_after_id = None
            self.mixer_volume = 0.5
            self.timer_tick_count = 0
            self.tts_queue = queue.Queue()


            self.commands_file = "commands.json"
            self.settings_file = "settings.json"
            self.activity_log_file = "activity_log.json"
            self.timers_file = "timers.json"

            self.timers = {}
            self.reward_actions = {}
            self.settings = {}
            self.default_commands = {}
            self.activity_log = deque(maxlen=100)

            self._load_activity_log_from_file()
            self.load_settings()
            self.load_commands_from_json()
            self.load_timers_from_file()

            self.setup_ui()

            self.refresh_commands_list()
            self.refresh_rewards_list()
            self.refresh_timers_list()

            self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

            saved_channel = self.channel_var.get()
            saved_token = self.token_var.get()

            if saved_channel and saved_token:
                self.root.after(100, self.start_bot)


        def _on_closing(self):
            """Handles window close event."""
            if self.is_running:
                 if messagebox.askyesno("Sair?", "O bot está conectado. Deseja parar e sair?"):
                     self.stop_bot()
                     self.root.destroy()
            else:
                 self._save_activity_log_to_file()
                 self.root.destroy()


        def setup_custom_theme(self):
            """Sets up the color theme."""
            self.colors = {
                'twitch_purple': '#9146FF', 'twitch_purple_dark': '#772ce8',
                'twitch_purple_light': '#a970ff', 'background': '#0e0e10',
                'surface': '#18181b', 'surface_dark': '#141417',
                'surface_light': '#1f1f23', 'surface_lighter': '#26262c',
                'text_primary': '#ffffff', 'text_secondary': '#adadb8',
                'success': '#00ff7f', 'error': '#ff5555', 'warning': '#ffaa00',
                'accent': '#00b8ff', 'disabled_bg': '#3a3a3a', 'disabled_text': '#aaaaaa'
            }


        def setup_ui(self):
            """Configures the main layout and instantiates UI components."""
            self.root.grid_columnconfigure(0, weight=0)
            self.root.grid_columnconfigure(1, weight=1)
            self.root.grid_rowconfigure(0, weight=1)
            self.root.configure(fg_color=self.colors['background'])

            self.navigation_frame = NavigationFrame(self.root, controller=self)
            self.navigation_frame.grid(row=0, column=0, sticky="nsew")

            self.content_frame = ctk.CTkFrame(self.root, fg_color=self.colors['background'], corner_radius=0)
            self.content_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
            self.content_frame.grid_columnconfigure(0, weight=1)
            self.content_frame.grid_rowconfigure(0, weight=1)

            self.connection_page = ConnectionPage(self.content_frame, app=self)
            self.commands_page = CommandsPage(self.content_frame, app=self)
            self.timers_page = TimersPage(self.content_frame, app=self)
            self.messages_page = MessagesPage(self.content_frame, app=self)
            self.chat_page = ChatPage(self.content_frame, app=self)
            self.rewards_page = RewardsPage(self.content_frame, app=self)
            self.moderation_page = ModerationPage(self.content_frame, app=self)
            self.activity_page = ActivityPage(self.content_frame, app=self)
            self.tts_page = TTSPage(self.content_frame, app=self)
            self.points_page = PointsPage(self.content_frame, app=self)
            self.moderation_page = ModerationPage(self.content_frame, app=self)
            self.giveaways_page = GiveawaysPage(self.content_frame, app=self)

            for page in (self.connection_page, self.commands_page, self.timers_page, self.messages_page,
                         self.chat_page, self.rewards_page, self.activity_page, self.tts_page, self.points_page, self.moderation_page,
                         self.giveaways_page):
                page.grid(row=0, column=0, sticky="nsew")

            if not hasattr(self, "pages") or not isinstance(self.pages, dict):
                self.pages = {}
            self.pages["sorteios"] = self.giveaways_page
            self.pages["giveaways"] = self.giveaways_page
            self.giveaways = self.giveaways_page

            self.select_frame_by_name("connect")

        def create_activity_frame(self):
            """Criar a página do Feed de Atividades usando um ScrollableFrame"""
            main_page_frame = ctk.CTkFrame(self.activity_frame, fg_color=self.colors['surface'])
            main_page_frame.pack(fill=tk.BOTH, expand=True)

            activity_display_frame = ctk.CTkFrame(main_page_frame, fg_color=self.colors['surface'])
            activity_display_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)

            activity_display_frame.grid_rowconfigure(1, weight=1)
            activity_display_frame.grid_columnconfigure(0, weight=1)

            frame_title = ctk.CTkLabel(
                activity_display_frame, text="📊 FEED DE ATIVIDADES",
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color=self.colors['twitch_purple_light']
            )
            frame_title.grid(row=0, column=0, sticky="w", padx=15, pady=(10, 15))

            self.activity_scroll_frame = ctk.CTkScrollableFrame(
                activity_display_frame,
                fg_color=self.colors['surface_light'],
                border_width=1,
                border_color=self.colors['surface_lighter']
            )
            self.activity_scroll_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
            self.activity_scroll_frame.grid_columnconfigure(0, weight=1)

        def _create_activity_item_widget(self, parent_frame, event_data):
            """
            Cria e retorna um widget CTkFrame estilizado para um item de atividade,
            COM TAGS E USUÁRIO NA MESMA LINHA.
            """
            raw_event_type = event_data['raw_event_type']
            user_name = event_data['user']
            details = event_data['details']
            timestamp_obj = event_data['timestamp_obj']
            time_ago_str = self._get_time_ago_string(timestamp_obj)

            item_frame = ctk.CTkFrame(
                parent_frame,
                fg_color=self.colors['surface_dark'],
                corner_radius=8
            )

            item_frame.timestamp_obj = timestamp_obj

            item_frame.grid_columnconfigure(0, weight=0)
            item_frame.grid_columnconfigure(1, weight=1)
            item_frame.grid_columnconfigure(2, weight=0)
            item_frame.grid_rowconfigure(0, weight=1)

            icon_char = "❓"
            icon_color = self.colors['text_secondary']
            if raw_event_type == 'channel.follow':
                 icon_char = "✨"; icon_color = self.colors['accent']
            elif raw_event_type == 'channel.subscribe':
                 icon_char = "⭐"; icon_color = self.colors['warning']
            elif raw_event_type == 'channel.raid':
                 icon_char = "⚔️"; icon_color = self.colors['error']
            elif raw_event_type == 'channel.channel_points_custom_reward_redemption.add':
                 icon_char = "🎁"; icon_color = self.colors['twitch_purple_light']
            elif raw_event_type == 'tts.redemption':
                 icon_char = "🗣️"; icon_color = self.colors['twitch_purple_light']

            ctk.CTkLabel(
                item_frame, text=icon_char, font=ctk.CTkFont(size=18), text_color=icon_color
            ).grid(row=0, column=0, padx=(10, 5), pady=5, sticky="ew")

            content_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            content_frame.grid(row=0, column=1, sticky="w", pady=5, padx=5)

            badge_type_text = ""
            badge_type_color = ""
            badge_text_color = self.colors['text_primary']
            if raw_event_type in ('channel.follow', 'channel.subscribe'):
                 badge_type_text = "New"; badge_type_color = self.colors['accent']
            elif raw_event_type in ('channel.channel_points_custom_reward_redemption.add', 'tts.redemption'):
                 badge_type_text = "Points"; badge_type_color = self.colors['twitch_purple']

            if badge_type_text:
                badge_type_label = ctk.CTkLabel(
                    content_frame,
                    text=badge_type_text, fg_color=badge_type_color, text_color=badge_text_color,
                    font=ctk.CTkFont(size=10, weight="bold"), corner_radius=5, padx=6, pady=2
                )
                badge_type_label.pack(side=tk.LEFT, padx=(0, 5))

            event_name_text = ""
            event_name_color = self.colors['surface_lighter']

            if raw_event_type == 'channel.follow':
                 event_name_text = "Follow"
            elif raw_event_type == 'channel.subscribe':
                 event_name_text = f"Sub {details}"
            elif raw_event_type == 'channel.raid':
                 event_name_text = "Raid"
            elif raw_event_type == 'channel.channel_points_custom_reward_redemption.add':
                 event_name_text = details
            elif raw_event_type == 'tts.redemption':
                 event_name_text = "TTS"

            if event_name_text:
                event_name_label = ctk.CTkLabel(
                    content_frame,
                    text=event_name_text, fg_color=event_name_color, text_color=self.colors['text_primary'],
                    font=ctk.CTkFont(size=10, weight="bold"), corner_radius=5, padx=6, pady=2
                )
                event_name_label.pack(side=tk.LEFT, padx=(0, 5))

            user_label = ctk.CTkLabel(
                content_frame,
                text=user_name, font=ctk.CTkFont(size=12, weight="bold"),
                text_color=self.colors['text_primary'],
                anchor="w"
            )
            user_label.pack(side=tk.LEFT, padx=(5, 0))

            if raw_event_type == 'tts.redemption':
                tts_message = details
                truncated_message = tts_message[:60] + "..." if len(tts_message) > 40 else tts_message

                message_label = ctk.CTkLabel(
                    content_frame,
                    text=f"Mensagem: \"{truncated_message}\"",
                    font=ctk.CTkFont(size=11),
                    text_color=self.colors['text_secondary'],
                    anchor="w"
                )
                message_label.pack(side=tk.LEFT, padx=(5, 0))

            time_label = ctk.CTkLabel(
                item_frame, text=time_ago_str, font=ctk.CTkFont(size=12),
                text_color=self.colors['text_secondary']
            )
            time_label.grid(row=0, column=2, padx=(0, 10), pady=5, sticky="e")
            item_frame.time_label_widget = time_label

            return item_frame

        def show_help(self):
            """Mostrar ajuda sobre comandos, incluindo a nova sintaxe avançada."""
            help_text = f"""
            🤖 COMANDOS & CONFIGURAÇÕES:

            ✨ PELA INTERFACE:
            • Conexão: O bot tentará auto-conectar se Token e Canal estiverem salvos.
            • Editar: Use o botão "✏️ EDITAR" na aba Comandos/Recompensas para mudar o nome ou a estrutura JSON.
            • Adicionar: Crie comandos simples na aba Comandos ou mapeie ações na aba Recompensas.
            • Testar: O botão "Testar ▶" (Recompensas) envia a mensagem e toca o som configurados.

            💬 ADMINISTRAÇÃO (APENAS STREAMER/MOD):
            • Adicionar/Remover Comando:
                !cmdd add !comando resposta
                !cmdd remove !comando
            • Gerenciar Contadores:
                !addcount <nome> <valor>  (Ex: !addcount mortes 1)
                !setcount <nome> <valor>  (Ex: !setcount lives 3)

            📝 VARIÁVEIS DISPONÍVEIS NA RESPOSTA:
            {{user}} - Nome do usuário que usou o comando.
            {{touser}} - Primeiro usuário mencionado (Ex: !cmd @amigo).
            {{rand_user}} - Usuário aleatório no chat (atualizado a cada 60s).
            {{channel}} - Nome do canal atual (Ex: fetads).

            🔢 VARIÁVEIS DINÂMICAS:
            • Contador (Leitura/Incremento): Use a sintaxe $count{{nome +/- valor}}
                Exemplo: $count{{mortes}}            -> Exibe o valor atual de 'mortes'.
                Exemplo: $count{{catapas + 1}}      -> Incrementa 'catapas' em 1 e exibe o novo valor.
                Exemplo: $count{{vidas - 1}}        -> Decrementa 'vidas' em 1 e exibe o novo valor.

            • Dados/Aleatório: Use a sintaxe $rand{{min, max}}
                Exemplo: $rand{{1, 20}}             -> Rola um dado de 20 faces.
                Exemplo: $rand{{15, 80}}%           -> Rola uma porcentagem aleatória.

            • {{value}} / {{size}} / {{reaction}}: Usado apenas para comandos de tipo especializados.

            🎮 COMANDOS ESSENCIAIS:
            !cmdd - Gerencia comandos pelo chat.
            !addcount / !setcount - Gerencia contadores globais.
            """

            clean_text = textwrap.dedent(help_text).strip() 

            CustomDialog(
                master=self.root, 
                title="🎮 Ajuda - Twitch Chat Bot", 
                text=clean_text,
                colors=self.colors,
                dialog_type='help',
                width=1300,
                height=700
            )


        def _create_command_item_widget(self, parent_frame, command_name, command_config):
            """
            Cria um widget CTkFrame estilizado para um item de comando, 
            com Dropdown de Permissão e Switch de Estado.
            """
            is_disabled = command_config.get('disabled', False)

            item_frame = ctk.CTkFrame(
                parent_frame,
                fg_color=self.colors['surface_dark'] if not is_disabled else self.colors['disabled_bg'], 
                border_width=1,
                border_color=self.colors['surface_lighter'],
                corner_radius=8
            )

            item_frame.grid_columnconfigure(0, weight=1)
            item_frame.grid_columnconfigure(1, weight=0)
            item_frame.grid_columnconfigure(2, weight=0)
            item_frame.grid_rowconfigure(0, weight=1)

            item_frame.command_name = command_name 
            item_frame._is_selected = False
            item_frame.command_config = command_config

            response_preview = command_config.get('response', '??')
            response_preview = response_preview[:60] + "..." if len(response_preview) > 60 else response_preview
            sound_path = command_config.get("sound")
            sound_txt = ""
            if sound_path:
                filename = sound_path.replace("\\", "/").split("/")[-1]
                sound_txt = f"\n - Som: {filename}"

            display_text = f"{command_name} → {response_preview}{sound_txt}"

            item_label = ctk.CTkLabel(
                item_frame, 
                text=display_text,
                #font=ctk.CTkFont(size=12, weight="bold") if not is_disabled else ctk.CTkFont(size=12),
                text_color=self.colors['text_primary'] if not is_disabled else self.colors['disabled_text'],
                anchor="w", justify="left"
            )
            item_label.grid(row=0, column=0, padx=10, pady=8, sticky="ew")

            permission_levels = ["Everyone", "Vip", "Mod", "Broadcaster"]
            current_perm_str = command_config.get('permission', 'everyone').capitalize()

            #self.log_message(f"DEBUG: Criando OptionMenu para '{command_name}' com permissão atual: '{current_perm_str}'", "info")

            if current_perm_str not in permission_levels:
                current_perm_str = "Everyone" 

            perm_var = tk.StringVar(value=current_perm_str)

            perm_menu = ctk.CTkOptionMenu(
                item_frame,
                variable=perm_var,
                values=permission_levels,
                fg_color=self.colors['surface_lighter'],
                button_color=self.colors['twitch_purple'],
                button_hover_color=self.colors['twitch_purple_dark'],
                dropdown_fg_color=self.colors['surface_light'],
                width=100,
                height=24,
                font=ctk.CTkFont(size=10),
                command=lambda new_perm, cn=command_name: self._handle_permission_change(cn, new_perm)
            )
            perm_menu.grid(row=0, column=1, padx=(0, 5), pady=5, sticky="e")
            state_switch = ctk.CTkSwitch(
                item_frame,
                text="",
                command=lambda cn=command_name, f=item_frame: self._handle_command_state_toggle(cn, f),
                variable=tk.BooleanVar(value=not is_disabled), 
                onvalue=True, offvalue=False,
                progress_color=self.colors['success'],
                button_color=self.colors['error'] if is_disabled else self.colors['success']
            )
            state_switch.grid(row=0, column=2, padx=10, pady=5, sticky="e")

            def on_click(event):
                for sibling in parent_frame.winfo_children():
                    if isinstance(sibling, ctk.CTkFrame) and sibling != item_frame:
                        sibling_disabled = sibling.command_config.get('disabled', False)
                        sibling.configure(fg_color=self.colors['surface_dark'] if not sibling_disabled else self.colors['disabled_bg'])
                        sibling._is_selected = False
                item_frame.configure(fg_color=self.colors['twitch_purple'])
                item_frame._is_selected = True

            def on_enter(event):
                if not getattr(item_frame, '_is_selected', False):
                     item_frame.configure(fg_color=self.colors['surface_light'])

            def on_leave(event):
                 if not getattr(item_frame, '_is_selected', False):
                     item_frame.configure(fg_color=self.colors['surface_dark'] if not is_disabled else self.colors['disabled_bg'])
                 else:
                     item_frame.configure(fg_color=self.colors['twitch_purple'])

            item_frame.bind("<Button-1>", on_click)
            item_label.bind("<Button-1>", on_click)
            item_frame.bind("<Enter>", on_enter)
            item_frame.bind("<Leave>", on_leave)
            item_label.bind("<Enter>", on_enter)
            item_label.bind("<Leave>", on_leave)

            def on_double_click(event):
                self.edit_command_by_name(command_name) 

            item_frame.bind("<Double-Button-1>", on_double_click)
            item_label.bind("<Double-Button-1>", on_double_click)

            return item_frame


        def _create_reward_item_widget(self, parent_frame, reward_name, action_config):
            """Cria um widget CTkFrame estilizado para um item de recompensa, incluindo o switch e botão Testar."""

            is_disabled = action_config.get('disabled', False)

            item_frame = ctk.CTkFrame(
                parent_frame,
                fg_color=self.colors['surface_dark'] if not is_disabled else self.colors['disabled_bg'], 
                border_width=1,
                border_color=self.colors['surface_lighter'],
                corner_radius=8
            )

            item_frame.grid_columnconfigure(0, weight=1)
            item_frame.grid_columnconfigure(1, weight=0)
            item_frame.grid_columnconfigure(2, weight=0)
            item_frame.grid_rowconfigure(0, weight=1)

            item_frame.reward_name = reward_name

            details = []
            if 'message' in action_config and action_config['message']:
                msg = action_config['message']
                details.append(f"Msg: {msg[:40]}" + ("..." if len(msg) > 40 else ""))
            if 'sound' in action_config and action_config['sound']:
                details.append("🔊")
            display_text = f"{reward_name} → ({' | '.join(details)})"

            state_switch = ctk.CTkSwitch(
                item_frame,
                text="", 
                variable=tk.BooleanVar(value=not is_disabled), 
                onvalue=True, offvalue=False,
                progress_color=self.colors['success'],
                button_color=self.colors['error'] if is_disabled else self.colors['success']
            )

            state_switch.configure(command=lambda rn=reward_name, f=item_frame, sw=state_switch: self._handle_reward_state_toggle(rn, f, sw))
            state_switch.grid(row=0, column=1, padx=(10, 5), pady=5, sticky="e")

            test_button = ctk.CTkButton(
                item_frame,
                text="Testar ▶",
                font=ctk.CTkFont(size=10, weight="bold"),
                width=60, height=24,
                fg_color=self.colors['surface_light'],
                hover_color=self.colors['accent'],
                command=lambda rn=reward_name: self.test_reward_action(rn),
                state=tk.DISABLED if is_disabled else tk.NORMAL
            )
            item_frame.test_button = test_button

            test_button.grid(row=0, column=2, padx=(5, 10), pady=5, sticky="e") 

            item_label = ctk.CTkLabel(
                item_frame,
                text=display_text,
                #font=ctk.CTkFont(size=12, weight="bold") if not is_disabled else ctk.CTkFont(size=12),
                text_color=self.colors['text_primary'] if not is_disabled else self.colors['disabled_text'],
                anchor="w", justify="left"
            )
            item_label.grid(row=0, column=0, padx=10, pady=8, sticky="ew")

            def on_click(event):
                for sibling in parent_frame.winfo_children():
                    if isinstance(sibling, ctk.CTkFrame) and sibling != item_frame:
                        sibling.configure(fg_color=self.colors['surface_dark'])
                        if hasattr(sibling, '_is_selected'): sibling._is_selected = False

                item_frame.configure(fg_color=self.colors['twitch_purple'])
                item_frame._is_selected = True

            def on_enter(event):
                if not getattr(item_frame, '_is_selected', False):
                     item_frame.configure(fg_color=self.colors['surface_light'])

            def on_leave(event):
                 if not getattr(item_frame, '_is_selected', False):
                     item_frame.configure(fg_color=self.colors['surface_dark'])
                 else:
                     item_frame.configure(fg_color=self.colors['twitch_purple'])

            item_frame.bind("<Button-1>", on_click)
            item_label.bind("<Button-1>", on_click)
            item_frame.bind("<Enter>", on_enter)
            item_frame.bind("<Leave>", on_leave)
            item_label.bind("<Enter>", on_enter)
            item_label.bind("<Leave>", on_leave)

            def on_double_click(event):
                self.edit_reward() 

            item_frame.bind("<Double-Button-1>", on_double_click)
            item_label.bind("<Double-Button-1>", on_double_click)

            return item_frame


        def _create_timer_item_widget(self, parent_frame, timer_name, timer_config):
            """Cria o widget customizado para um item da lista de Timers."""
            is_disabled = not timer_config.get('enabled', True)

            item_frame = ctk.CTkFrame(
                parent_frame,
                fg_color=self.colors['surface_dark'] if not is_disabled else self.colors['disabled_bg'],
                border_width=1, border_color=self.colors['surface_lighter'], corner_radius=8
            )
            item_frame.grid_columnconfigure(1, weight=1)
            item_frame.grid_columnconfigure(0, weight=0)
            item_frame.grid_columnconfigure(2, weight=0)

            item_frame.timer_name = timer_name

            state_switch = ctk.CTkSwitch(
                item_frame, text="", variable=tk.BooleanVar(value=not is_disabled),
                onvalue=True, offvalue=False, progress_color=self.colors['success'],
                button_color=self.colors['success'] if not is_disabled else self.colors['error'],
                width=30
            )
            state_switch.configure(command=lambda n=timer_name, f=item_frame, sw=state_switch: self.toggle_timer_state(n, f, sw))
            state_switch.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="ns")

            name_label = ctk.CTkLabel(
                item_frame, text=timer_name,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=self.colors['text_primary'] if not is_disabled else self.colors['disabled_text'],
                anchor="w"
            )
            name_label.grid(row=0, column=1, padx=10, pady=(5, 0), sticky="ew")

            msg_preview = timer_config.get('message', '...').replace('\n', ' ')
            msg_preview = (msg_preview[:50] + "...") if len(msg_preview) > 50 else msg_preview
            msg_label = ctk.CTkLabel(
                item_frame, text=msg_preview,
                font=ctk.CTkFont(size=11),
                text_color=self.colors['text_secondary'] if not is_disabled else self.colors['disabled_text'],
                anchor="w"
            )
            msg_label.grid(row=1, column=1, padx=10, pady=(0, 5), sticky="ew")

            interval_min = timer_config.get('interval_min', 0)
            min_lines = timer_config.get('min_lines', 0)
            interval_text = f"{interval_min} min / {min_lines} linhas"
            interval_label = ctk.CTkLabel(
                item_frame, text=interval_text,
                font=ctk.CTkFont(size=11),
                text_color=self.colors['text_secondary'] if not is_disabled else self.colors['disabled_text']
            )
            interval_label.grid(row=0, column=2, rowspan=2, padx=15, pady=10, sticky="ns")

            def on_click(event):
                for sibling in parent_frame.winfo_children():
                    if isinstance(sibling, ctk.CTkFrame) and sibling != item_frame:
                        sibling.configure(fg_color=self.colors['surface_dark'] if not sibling.timer_config.get('disabled', False) else self.colors['disabled_bg'])
                        sibling._is_selected = False
                item_frame.configure(fg_color=self.colors['twitch_purple'])
                item_frame._is_selected = True

            item_frame.bind("<Button-1>", on_click)
            name_label.bind("<Button-1>", on_click)
            msg_label.bind("<Button-1>", on_click)
            interval_label.bind("<Button-1>", on_click)

            item_frame.timer_config = timer_config
            item_frame._is_selected = False

            def on_double_click(event):
                self.open_edit_timer_dialog() 

            item_frame.bind("<Double-Button-1>", on_double_click)
            msg_label.bind("<Double-Button-1>", on_double_click)
            name_label.bind("<Double-Button-1>", on_double_click)
            interval_label.bind("<Double-Button-1>", on_double_click)

            return item_frame

