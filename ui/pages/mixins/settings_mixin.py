import json
import os

import pygame
import tkinter as tk


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
            """Carrega settings do JSON e preenche SOMENTE chaves ausentes com defaults."""
            defaults = {
                "msg_follow": "Obrigado pelo follow, @{user}! Seja bem-vindo(a)! <3",
                "msg_sub": "WOAH! Muito obrigado pelo Sub (Tier {tier}), @{user}! Você é incrível! <3",
                "msg_gift_sub": "WOAH! @{user} ganhou um Sub de presente! Muito obrigado! <3",
                "msg_raid": "RAID! Sejam todos muito bem-vindos, time do @{raider}! Mandem seus emotes!",
                "reward_actions": {},
                "counts": {},
                "tts_enabled": False,
                "tts_reward_name": "",
                "tts_voice_lang": "pt-br",
                "tts_volume": 50,
                "msg_cheer_alert": "{user} enviou {bits}x bits!",
                "msg_cheer_alert_enabled": True,
                "tts_cheer_format": "{user} enviou {bits}x e disse: {message}",
                "tts_cheer_enabled": False,
                "tts_cheer_min_bits": 100,
                # "last_channel": "",
                # "last_token": "",
            }

            if os.path.exists(self.settings_file):
                try:
                    with open(self.settings_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    if not isinstance(data, dict):
                        data = {}
                    updated = False
                    for k, v in defaults.items():
                        if k not in data:
                            data[k] = v
                            updated = True

                    self.settings = data
                    self.reward_actions = self.settings.get('reward_actions', {})
                    if updated:
                        self.save_settings(quiet=True)

                except Exception as e:
                    self.log_message(f"❌ Erro ao carregar {self.settings_file}: {e}", "error")
                    self.settings = defaults.copy()
                    self.reward_actions = {}
                    self.save_settings(quiet=True)
            else:
                self.settings = defaults.copy()
                self.reward_actions = {}
                self.save_settings(quiet=True)
                
            self.mixer_volume = float(self.settings.get('tts_volume', 50)) / 100.0
            try:
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                pygame.mixer.music.set_volume(self.mixer_volume)
            except Exception as e:
                print(f"Erro ao definir volume inicial do pygame: {e}")


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

            mod = self.settings.setdefault('moderation', {})
            if hasattr(self, 'moderation_page'):
                mp = self.moderation_page
                try:
                    mod['enabled'] = bool(mp.mod_enabled.get())
                    mod['anti_link_spam'] = bool(mp.anti_link.get())
                    mod['blacklist_enabled'] = bool(mp.blacklist_enabled.get())

                    if hasattr(mp, 'blacklist_text'):
                        try:
                            words = [w.strip() for w in mp.blacklist_text.get('1.0', tk.END).splitlines() if w.strip()]
                        except Exception as e:
                            self.log_message(f"⚠️ Erro ao ler blacklist_text: {e}", "error")
                            words = mod.get('blacklist_words', [])
                    else:
                        words = mod.get('blacklist_words', [])
                    mod['blacklist_words'] = words


                    permit = mod.setdefault('permit', {})
                    permit['command_name'] = (mp.permit_name.get().strip() or '!permit')
                    try:
                        permit['duration_seconds'] = int(mp.permit_secs.get().strip() or '60')
                    except ValueError:
                        permit['duration_seconds'] = 60
                    permit['message_enabled'] = bool(mp.permit_msg_enabled.get())
                    permit['message_template'] = (mp.permit_msg_template.get().strip() or '@{target} pode postar 1 link por {seconds}s.')

                    try:
                        mod['timeout_seconds'] = int(mp.timeout_secs.get().strip() or '10')
                    except ValueError:
                        mod['timeout_seconds'] = 10

                    if hasattr(mp, 'punish_msg_enabled'):
                        mod['punish_message_enabled'] = bool(mp.punish_msg_enabled.get())

                    if hasattr(mp, 'punish_msg'):
                        new_msg = mp.punish_msg.get().strip()
                        old_msg = mod.get('punish_message', '')
                        if new_msg or not old_msg:
                            mod['punish_message'] = new_msg

                except Exception as e:
                    self.log_message(f"⚠️ Erro ao coletar UI de moderação: {e}", "error")

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
                        if hasattr(self.bot, 'moderation'):
                            self.bot.moderation.config = self.bot.config

            except Exception as e:
                log_func = getattr(self, 'log_message', print)
                log_func(f"❌ Erro save {self.settings_file}: {e}", "error")

