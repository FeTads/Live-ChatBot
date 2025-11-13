from datetime import datetime
import threading
import requests

from bot import TwitchChatBot
from eventsub import TwitchEventSubClient
from ui.custom_dialog import CustomDialog
from ui.toast_notification import ToastNotification


class UtilsMixin:
        def select_frame_by_name(self, name):
            """Raises the selected page frame and updates navigation button colors."""
            page_map = {
                "connect": self.connection_page,
                "commands": self.commands_page,
                "timers": self.timers_page,
                "messages": self.messages_page,
                "chat": self.chat_page,
                "rewards": self.rewards_page,
                "moderação": self.moderation_page,
                "activity": self.activity_page,
                "tts": self.tts_page,
                "pontos": self.points_page,
                "sorteios": self.giveaways_page
            }
            page_to_raise = page_map.get(name)
            if page_to_raise:
                page_to_raise.tkraise()
                if hasattr(self, 'navigation_frame'):
                    self.navigation_frame.update_button_colors(name)
            else:
                print(f"Error: No page found for name '{name}'")


        def run_verification_thread(self, channel_name, token):
            """Verifies token, permissions via Twitch API in a separate thread."""
            self.log_message(f"🔍 Verificando permissões para #{channel_name}...", "system")
            try:
                api_token = token.replace("oauth:", "")
                headers_validate = {'Authorization': f'OAuth {api_token}'}
                resp_validate = requests.get('https://id.twitch.tv/oauth2/validate', headers=headers_validate)
                if resp_validate.status_code != 200:
                    self.root.after(0, self.on_verification_failed, f"Token inválido/expirado ({resp_validate.status_code})")
                    return

                validate_data = resp_validate.json()
                bot_user_id = validate_data['user_id']
                bot_login = validate_data['login']
                client_id = validate_data['client_id']
                self.log_message(f"ℹ️ Bot: {bot_login} (ID: {bot_user_id})", "info")

                headers_api = {'Authorization': f'Bearer {api_token}', 'Client-Id': client_id}
                try:
                    resp_channel = requests.get(f'https://api.twitch.tv/helix/users?login={channel_name}', headers=headers_api)
                    resp_channel.raise_for_status()
                    channel_data = resp_channel.json().get('data')
                    if not channel_data:
                        self.root.after(0, self.on_verification_failed, f"Canal '{channel_name}' não encontrado.")
                        return
                    target_channel_id = channel_data[0]['id']
                    self.log_message(f"ℹ️ Canal: {channel_name} (ID: {target_channel_id})", "info")
                except requests.RequestException as e:
                    self.root.after(0, self.on_verification_failed, f"Erro busca ID canal: {e}")
                    return

                is_moderator = False
                if bot_login.lower() != channel_name.lower():
                    try:
                        resp_mod = requests.get(
                            f'https://api.twitch.tv/helix/moderation/channels?user_id={bot_user_id}',
                            headers=headers_api
                        )
                        if resp_mod.status_code == 401 or resp_mod.status_code == 403:
                            self.log_message(
                                "Aviso: o token não possui o escopo 'user:read:moderated_channels'. "
                                "Não será possível verificar se o bot é moderador.",
                                "warning"
                            )
                        else:
                            resp_mod.raise_for_status()
                            moderated_channels = resp_mod.json().get('data', [])
                            for ch in moderated_channels:
                                if ch.get('broadcaster_id') == target_channel_id:
                                    is_moderator = True
                                    break

                    except requests.RequestException as e:
                        self.log_message(
                            f"Aviso: erro na checagem de moderação: {e.response.status_code if e.response else e}",
                            "warning"
                        )
                        if e.response is None or e.response.status_code not in [401, 403]:
                            self.root.after(0, self.on_verification_failed, f"Erro API mod check: {e}")
                            return


                #self.log_message(f"DEBUG: {channel_name.lower()} - {bot_login} - {is_moderator}", "error")

                if is_moderator or bot_login.lower() == channel_name.lower():
                    self.settings['last_channel'] = channel_name
                    self.settings['last_token'] = token
                    if 'reward_actions' not in self.settings: self.settings['reward_actions'] = {}
                    self.save_settings(quiet=True)

                    config = {
                        'channel': channel_name, 'token': token, 'commands': self.default_commands,
                        'gui': self, 'bot_user_name': bot_login, 'api_token': api_token,
                        'client_id': client_id, 'bot_user_id': bot_user_id,
                        'target_channel_id': target_channel_id, 'settings': self.settings
                    }
                    self.root.after(0, self.start_main_bot_thread, config)
                else:
                    self.root.after(0, self.on_verification_failed, f"Bot '{bot_login}' não é mod/dono de '{channel_name}'.")
            except Exception as e:
                self.root.after(0, self.on_verification_failed, f"Erro verificação: {e}")


        def on_verification_failed(self, message):
            """Handles verification failure."""
            self.log_message(f"❌ Falha: {message}", "error")
            CustomDialog(master=self.root, title="❌ Erro de Permissão", text=message, colors=self.colors, dialog_type='error')
            self.is_running = False
            if hasattr(self, 'start_button'): self.start_button.configure(state="normal")
            if hasattr(self, 'navigation_frame'): self.navigation_frame.update_status("● OFFLINE", "error")
            if hasattr(self, 'channel_entry'): self.channel_entry.configure(state="normal", fg_color=self.colors['surface_light'], text_color=self.colors['text_primary'])
            if hasattr(self, 'token_entry'): self.token_entry.configure(state="normal", fg_color=self.colors['surface_light'], text_color=self.colors['text_primary'])


        def start_main_bot_thread(self, config):
            """Starts the IRC bot and EventSub client threads."""
            self.log_message(f"✅ Permissão OK. Conectando como '{config['bot_user_name']}'...", "success")
            self.is_running = True
            if hasattr(self, 'navigation_frame'): self.navigation_frame.update_status("● ONLINE", "success")
            if hasattr(self, 'stop_button'): self.stop_button.configure(state="normal")

            ToastNotification(self.root, f"Conectado!", colors=self.colors, toast_type="success")

            self.bot = TwitchChatBot(self, config)
            self.thread = threading.Thread(target=self.bot.run, daemon=True)
            self.thread.start()
            self.log_message("🚀 Conectando ao chat (IRC)...", "system")

            self.eventsub = TwitchEventSubClient(self, config)
            self.eventsub_thread = threading.Thread(target=self.eventsub.run, daemon=True)
            self.eventsub_thread.start()
            self.log_message("🎧 Ouvindo eventos...", "system")

            self.tts_playback_thread = threading.Thread(target=self._tts_playback_loop, daemon=True)
            self.tts_playback_thread.start()

            self.root.after(200, self._load_initial_activity_display)
            self.root.after(300, self._update_reward_test_buttons_state, True)

            self.timer_tick_count = 0
            self.root.after(5000, self._timer_loop_check)

            if self._update_timestamps_after_id: self.root.after_cancel(self._update_timestamps_after_id)
            self._update_timestamps_after_id = self.root.after(60000, self._schedule_timestamp_update)


        def _handle_generic_deletion(self, result, item_name, target_dict, refresh_func, item_type="item"):
            """
            Manipulador genérico para confirmar e executar a remoção de um item.
            """
            if result == "yes":
                name = item_name

                is_essential_command = (item_type == "command" and name in ["!comandos", "!cmdd"])

                if name in target_dict and not is_essential_command:

                    del target_dict[name]
                    refresh_func()

                    if item_type == "command":
                        self.save_commands()
                        if self.bot: self.bot.config['commands'] = self.default_commands
                    elif item_type == "timer":
                        self.save_timers()
                    else: #item_type == "reward"
                        self.save_settings()

                    self.log_message(f"🗑️ {item_type.capitalize()} '{name}' removido!", "success")
                    ToastNotification(self.root, f"{item_type.capitalize()} '{name}' removido!", colors=self.colors, toast_type="success")

                else:
                    msg = "Comando essencial não pode ser removido!" if is_essential_command else f"{item_type.capitalize()} não encontrado para remoção."
                    CustomDialog(master=self.root, title="⚠️ Aviso", text=msg, colors=self.colors, dialog_type='warning')


        def _get_time_ago_string(self, past_datetime):
            """Calcula a string de tempo relativo ('in now', '5m', '2h', '3d')."""
            now = datetime.now()
            diff = now - past_datetime

            seconds = int(diff.total_seconds())
            minutes = seconds // 60
            hours = minutes // 60
            days = hours // 24
            weeks = days // 7
            months = days // 30
            years = days // 365

            if seconds < 60:
                return "in now" if seconds < 10 else f"{seconds}s"
            elif minutes < 60:
                return f"{minutes}m"
            elif hours < 24:
                return f"{hours}h"
            elif days < 7:
                return f"{days}d"
            elif weeks < 4:
                return f"{weeks}w"
            elif months < 12:
                return f"{months}mo"
            else:
                return f"{years}y"


        def _schedule_timestamp_update(self):
            """Chama a atualização e agenda a próxima execução."""
            if not self.is_running:
                 return

            self._update_all_activity_timestamps()
            self._update_timestamps_after_id = self.root.after(60000, self._schedule_timestamp_update)

        def _handle_permission_change(self, command_name, new_permission_str):
            """
            Atualiza o nível de permissão e o estilo do OptionMenu localmente.
            """
            new_permission = new_permission_str.lower().strip()

            if command_name not in self.default_commands:
                self.log_message(f"Erro: Comando '{command_name}' não encontrado para alterar permissão.", "error")
                return

            self.default_commands[command_name]['permission'] = new_permission

            self.save_commands()
            self.log_message(f"🔒 Permissão do '{command_name}' definida para: {new_permission}", "system")

            if self.bot:
                self.bot.config['commands'] = self.default_commands

