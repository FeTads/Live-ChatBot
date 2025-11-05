import json
import os

import pygame

from ui.toast_notification import ToastNotification


class SettingsMixin:
        def load_default_settings(self):
             self.settings = {
                 "msg_follow": "Obrigado pelo follow, @{user}! Seja bem-vindo(a)! <3",
                 "msg_sub": "WOAH! Muito obrigado pelo Sub (Tier {tier}), @{user}! Você é incrível! <3",
                 "msg_gift_sub": "WOAH! @{user} ganhou um Sub de presente! Muito obrigado! <3",
                 "msg_raid": "RAID! Sejam todos muito bem-vindos, time do @{raider}! Mandem seus emotes!",
                 "reward_actions": {},
                 "tts_enabled": False,
                 "tts_reward_name": "",
                 "tts_voice_lang": "pt-br",
                 "tts_volume": 50,
                 "counts": {},
                 "msg_follow_enabled": True,
                 "msg_sub_enabled": True,   
                 "msg_gift_enabled": True,  
                 "msg_raid_enabled": True,  
                 "msg_cheer_alert": "{user} enviou {bits}x bits!",
                 "msg_cheer_alert_enabled": True, 
                 "tts_cheer_format": "{user} enviou {bits}x e disse: {message}",
                 "tts_cheer_enabled": False,
                 "tts_cheer_min_bits": 100,
             }
             self.reward_actions = self.settings.get('reward_actions', {})
             self.log_message("📝 Configs padrão carregadas", "system")


        def load_settings(self):
            """Loads settings and reward actions from JSON."""
            if os.path.exists(self.settings_file):
                try:
                    with open(self.settings_file, 'r', encoding='utf-8') as f:
                        self.settings = json.load(f)
                    self.reward_actions = self.settings.get('reward_actions', {})
                    defaults = {"msg_follow": "", "msg_sub": "", "msg_gift_sub": "", "msg_raid": "", "reward_actions": {},
                                "tts_enabled": False,
                                "tts_reward_name": "",
                                "tts_voice_lang": "pt-br",
                                "tts_volume": 50,
                                "counts": {}
                                }

                    self.mixer_volume = self.settings.get('tts_volume', 50) / 100.0
                    try:
                        pygame.mixer.music.set_volume(self.mixer_volume)
                    except Exception as e:
                        print(f"Erro ao definir volume inicial do pygame: {e}")

                    updated = False
                    for key, value in defaults.items():
                        if key not in self.settings:
                            self.settings[key] = value
                            updated = True
                    if updated: self.save_settings(quiet=True)
                except Exception as e:
                    self.log_message(f"❌ Erro load {self.settings_file}: {e}", "error")
                    self.load_default_settings()
            else:
                self.load_default_settings()
                self.save_settings(quiet=True)


        def save_settings(self, quiet=False):
            """Saves settings and reward actions to JSON."""

            if hasattr(self, 'messages_page') and hasattr(self.messages_page, 'msg_follow_var'):
                self.settings['msg_follow'] = self.messages_page.msg_follow_var.get()
                self.settings['msg_sub'] = self.messages_page.msg_sub_var.get()
                self.settings['msg_gift_sub'] = self.messages_page.msg_gift_sub_var.get()
                self.settings['msg_raid'] = self.messages_page.msg_raid_var.get()
                self.settings['msg_follow_enabled'] = self.messages_page.msg_follow_enabled_var.get()
                self.settings['msg_sub_enabled'] = self.messages_page.msg_sub_enabled_var.get()
                self.settings['msg_gift_enabled'] = self.messages_page.msg_gift_enabled_var.get()
                self.settings['msg_raid_enabled'] = self.messages_page.msg_raid_enabled_var.get()

                self.settings['msg_cheer_alert'] = self.messages_page.msg_cheer_alert_var.get()
                self.settings['msg_cheer_alert_enabled'] = self.messages_page.msg_cheer_alert_enabled_var.get()
                self.settings['tts_cheer_enabled'] = self.messages_page.tts_cheer_enabled_var.get()
                self.settings['tts_cheer_format'] = self.messages_page.tts_cheer_format_var.get()

                try:
                    self.settings['tts_cheer_min_bits'] = int(self.messages_page.tts_cheer_min_bits_var.get())
                except ValueError:
                    self.settings['tts_cheer_min_bits'] = 100

            if hasattr(self, 'tts_page'):
                self.settings['tts_enabled'] = self.tts_page.tts_enabled_var.get()
                self.settings['tts_reward_name'] = self.tts_page.tts_reward_name_var.get().strip()

                selected_voice_name = self.tts_page.tts_voice_var.get()
                lang_code = self.tts_page.voice_map.get(selected_voice_name, "pt-br")
                self.settings['tts_voice_lang'] = lang_code

                self.settings['tts_volume'] = self.tts_page.tts_volume_var.get()

            self.settings['reward_actions'] = self.reward_actions

            if 'counts' not in self.settings:
                 self.settings['counts'] = {}

            try:
                with open(self.settings_file, 'w', encoding='utf-8') as f:
                    json.dump(self.settings, f, indent=2, ensure_ascii=False)

                if not quiet:
                    if hasattr(self, 'messages_page'):
                        self.log_message("💾 Configs salvas!", "success")
                        ToastNotification(self.root, f"Salvo com sucesso!", colors=self.colors, toast_type="success")

                    if self.eventsub or self.bot:
                        if self.eventsub: self.eventsub.config['settings'] = self.settings
                        if self.bot: self.bot.config['settings'] = self.settings

            except Exception as e:
                log_func = getattr(self, 'log_message', print)
                log_func(f"❌ Erro save {self.settings_file}: {e}", "error")

