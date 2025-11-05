import time
import os
from tkinter import filedialog

import tkinter as tk
import customtkinter as ctk
from gtts import gTTS
import pygame
from ui.custom_dialog import CustomDialog
from ui.edit_command_dialog import EditCommandDialog
from ui.toast_notification import ToastNotification


class RewardsTtsMixin:
        def browse_sound_file(self):
            """Abre uma janela para selecionar um arquivo de som."""
            file_path = filedialog.askopenfilename(
                title="Selecionar Arquivo de Som",
                filetypes=[("Arquivos de Áudio", "*.wav *.mp3"), ("Todos os Arquivos", "*.*")]
            )
            if file_path and hasattr(self, 'rewards_page'):
                self.rewards_page.new_reward_sound_var.set(file_path)


        def browse_sound_file_for_edit(self, target_var: tk.StringVar):
            """Helper para o modal de edição que sabe qual StringVar atualizar."""
            file_path = filedialog.askopenfilename(
                title="Selecionar Arquivo de Som",
                filetypes=[("Arquivos de Áudio", "*.wav *.mp3"), ("Todos os Arquivos", "*.*")]
            )
            if file_path:
                target_var.set(file_path)


        def add_reward_action(self):
            """Adiciona uma nova ação de recompensa ao mapeamento."""
            if not hasattr(self, 'rewards_page') or \
               not hasattr(self.rewards_page, 'new_reward_name_var') or \
               not hasattr(self.rewards_page, 'new_reward_msg_var') or \
               not hasattr(self.rewards_page, 'new_reward_sound_var'):
                self.log_message("Erro: Página de recompensas ou seus elementos não inicializados.", "error")
                return

            page = self.rewards_page
            reward_name = page.new_reward_name_var.get().strip()
            message = page.new_reward_msg_var.get().strip()
            sound_path = page.new_reward_sound_var.get().strip()

            if not reward_name:
                CustomDialog(master=self.root, title="⚠️ Aviso", text="Digite o nome exato da recompensa!", colors=self.colors, dialog_type='warning')
                return

            if not message and not sound_path:
                CustomDialog(master=self.root, title="⚠️ Aviso", text="Você precisa definir uma mensagem ou um som!", colors=self.colors, dialog_type='warning')
                return

            if sound_path and not os.path.exists(sound_path):
                 CustomDialog(master=self.root, title="❌ Erro", text=f"Arquivo de som não encontrado:\n{sound_path}", colors=self.colors, dialog_type='error')
                 return

            action = {}
            if message:
                action['message'] = message
            if sound_path:
                action['sound'] = sound_path

            self.reward_actions[reward_name] = action
            page.new_reward_name_var.set("")
            page.new_reward_msg_var.set("")
            page.new_reward_sound_var.set("")


            self.refresh_rewards_list()
            self.save_settings()
            self.log_message(f"🎁 Ação para recompensa '{reward_name}' adicionada!", "success")


        def remove_reward_action(self):
            """Removes the visually selected reward action."""
            if not hasattr(self, 'rewards_page') or not hasattr(self.rewards_page, 'rewards_scroll_frame'): return
            frame = self.rewards_page.rewards_scroll_frame

            selected_reward_name = None
            for item_widget in frame.winfo_children():
                if isinstance(item_widget, ctk.CTkFrame) and getattr(item_widget, '_is_selected', False):
                    selected_reward_name = item_widget.reward_name
                    break

            if selected_reward_name:
                reward = selected_reward_name
                CustomDialog(
                    master=self.root,
                    title="🗑️ Confirmar Remoção",
                    text=f"Você tem certeza que deseja remover a recompensa:\n\n{reward}?",
                    colors=self.colors,
                    dialog_type='warning',
                    buttons=[("Sim, Remover", "yes"), ("Não", "no")],
                    callback=lambda result: self._handle_generic_deletion(
                        result,
                        reward,
                        self.reward_actions,
                        self.refresh_rewards_list,
                        "reward"
                    )
                )
            else:
                CustomDialog(master=self.root, title="⚠️ Aviso", text="Selecione uma recompensa para remover!", colors=self.colors, dialog_type='warning')


        def refresh_rewards_list(self):
            """Updates the rewards display area using custom widgets."""
            if hasattr(self, 'rewards_page') and hasattr(self.rewards_page, 'rewards_scroll_frame'):
                frame = self.rewards_page.rewards_scroll_frame

                for widget in frame.winfo_children():
                    widget.destroy()

                if hasattr(self.rewards_page, 'toggle_button_ref'):
                    pass

                row_index = 0
                for name, action_config in self.reward_actions.items():
                    item_widget = self._create_reward_item_widget(frame, name, action_config)
                    item_widget.grid(row=row_index, column=0, sticky="ew", padx=5, pady=(5, 0))
                    row_index += 1

                self._update_reward_test_buttons_state(self.is_running)


        def _handle_reward_state_toggle(self, reward_name, item_widget, switch_widget):
            """
            Manipula o clique no switch de recompensa, salva, e ATUALIZA O WIDGET LOCALMENTE.
            """
            if reward_name not in self.reward_actions:
                self.log_message(f"Erro: Recompensa '{reward_name}' não encontrada.", "error")
                return

            current_state_in_memory = self.reward_actions[reward_name].get('disabled', False)
            new_state = not current_state_in_memory

            self.reward_actions[reward_name]['disabled'] = new_state
            self.save_settings(quiet=True)

            new_fg_color = self.colors['disabled_bg'] if new_state else self.colors['surface_dark']
            item_label = item_widget.grid_slaves(row=0, column=0)[0]
            new_text_color = self.colors['disabled_text'] if new_state else self.colors['text_primary']
            new_font_weight = "normal" if new_state else "bold"
            # n usar new_text/color

            item_widget.configure(fg_color=new_fg_color)

            new_button_color = self.colors['error'] if new_state else self.colors['success']
            switch_widget.configure(button_color=new_button_color)

            test_button_widget = item_widget.test_button
            test_button_widget.configure(state=tk.DISABLED if new_state else tk.NORMAL)

            status = "DESABILITADA" if new_state else "HABILITADA"
            self.log_message(f"🔄 Recompensa '{reward_name}' agora está {status}.", "system")

        def play_sound(self, file_path):
            """Toca um arquivo de som usando pygame."""
            if not file_path or not os.path.exists(file_path):
                self.log_message(f"🔊 Erro: Arquivo de som não encontrado: {file_path}", "error")
                return

            try:
                pygame.mixer.music.stop() 
                pygame.mixer.music.load(file_path)
                pygame.mixer.music.play()
                #self.log_message(f"🔊 Tocando som: {os.path.basename(file_path)}", "info")
            except Exception as e:
                self.log_message(f"🔊 Erro ao tocar som {file_path}: {e}", "error")

        def _is_bot_connected(self) -> bool:
            try:
                if hasattr(self.bot, "is_connected"):
                    return bool(self.bot.is_connected())
                if hasattr(self.bot, "connected"):
                    return bool(self.bot.connected)
                if hasattr(self.bot, "impl") and hasattr(self.bot.impl, "connected"):
                    return bool(self.bot.impl.connected)
            except Exception:
                pass
            return False

        def test_reward_action(self, reward_name):
            """Executa a ação de uma recompensa (som/mensagem) como teste."""
            if not self.is_running or not self.bot or not self._is_bot_connected():
                #self.log_message("Aviso: Bot não está conectado para testar recompensa.", "warning")
                CustomDialog(master=self.root, title="⚠️ Aviso", text="Conecte o bot antes de testar!", colors=self.colors, dialog_type='warning')
                return

            action_config = self.reward_actions.get(reward_name)

            if not action_config:
                self.log_message(f"Erro: Configuração não encontrada para recompensa de teste '{reward_name}'.", "error")
                return

            test_placeholders = {
                'user': '<TESTE>',
                'input': '<INPUT_TESTE>',
                'tier': '1', 
                'raider': '<RAIDER_FETADS>', 
                'viewers': '99',
                'channel': self.bot.config['channel'] if self.bot and hasattr(self.bot, 'config') else self.settings.get('last_channel', '<CANAL>')
            }

            ToastNotification(self.root, f"Testando: {reward_name}", colors=self.colors, toast_type="success")
            self.log_message(f"▶️ Testando recompensa: {reward_name}", "info")

            try:
                event_type_for_activity = "channel.channel_points_custom_reward_redemption.add"
                user_for_activity = "<TESTE>"
                details_for_activity = f"[TESTE] {reward_name}"

                self.add_activity_entry(event_type_for_activity, user_for_activity, details_for_activity)
            except Exception as e:
                self.log_message(f"Erro ao adicionar entrada de teste na atividade: {e}", "error")

            if 'sound' in action_config and action_config['sound']:
                self.play_sound(action_config['sound'])

            if 'message' in action_config and action_config['message']:
                msg_template = action_config['message']
                try:
                    test_message = msg_template.format_map(test_placeholders)
                    self.bot.send_message(f"[TESTE] {test_message}")
                    #self.log_message(f"▶️ (Chat Teste) {test_message}", "bot")

                except KeyError as e:
                     self.log_message(f"❌ Erro ao formatar mensagem: Placeholder {e} faltando.", "error")
                except Exception as e:
                     self.log_message(f"❌ Erro ao enviar mensagem de teste: {e}", "error")

            try:
                event_type_for_activity = "channel.channel_points_custom_reward_redemption.add"
                details_for_activity = f"[TESTE] {reward_name}"
                self.add_activity_entry(event_type_for_activity, test_placeholders['user'], details_for_activity)
            except Exception as e:
                self.log_message(f"Erro ao adicionar entrada de teste na atividade: {e}", "error")


        def _update_reward_test_buttons_state(self, enable: bool):
            """Habilita ou desabilita todos os botões 'Testar' na página de Recompensas."""
            if not hasattr(self, 'rewards_page') or not hasattr(self.rewards_page, 'rewards_scroll_frame'):
                return

            state_to_set = tk.NORMAL if enable else tk.DISABLED
            try:
                for item_widget in self.rewards_page.rewards_scroll_frame.winfo_children():
                    if isinstance(item_widget, ctk.CTkFrame) and hasattr(item_widget, 'test_button'):
                        item_widget.test_button.configure(state=state_to_set)
            except Exception as e:
                 self.log_message(f"Erro ao atualizar estado dos botões de teste: {e}", "error")


        def request_tts_playback(self, text_to_speak):
            """
            Adiciona um texto à fila de TTS (chamado pelo EventSub).
            """
            if not text_to_speak:
                 return
            self.tts_queue.put(text_to_speak)


        def _tts_playback_loop(self):
            """
            Executa em uma thread dedicada. Processa a fila de TTS serialmente.
            """
            tts_file_path = "tts_output.mp3"

            while self.is_running:
                try:
                    text_to_speak = self.tts_queue.get()
                    if text_to_speak is None or not self.is_running:
                        self.log_message("🛑 Thread TTS parada.", "system")
                        break

                    try:
                        lang_code = self.settings.get('tts_voice_lang', 'pt-br') 
                        tts = gTTS(text=text_to_speak, lang=lang_code)
                        tts.save(tts_file_path)
                    except Exception as e:
                        self.log_message(f"❌ Erro ao gerar/salvar TTS: {e}", "error")
                        continue
                    try:
                        if not pygame.mixer.get_init():
                             pygame.mixer.init()
                             self.log_message("Aviso: Mixer do Pygame reinicializado.", "warning")

                        volume = self.settings.get('tts_volume', 50) / 100.0
                        pygame.mixer.music.set_volume(volume)

                        pygame.mixer.music.load(tts_file_path)
                        pygame.mixer.music.play()

                        while pygame.mixer.music.get_busy():
                            if not self.is_running:
                                pygame.mixer.music.stop()
                                break
                            time.sleep(0.1)

                        pygame.mixer.music.unload()

                    except Exception as e:
                        self.log_message(f"🔊 Erro ao tocar áudio TTS: {e}", "error")

                except Exception as e:
                     self.log_message(f"💥 Erro fatal na thread TTS: {e}", "error")
                     time.sleep(1)

            if os.path.exists(tts_file_path):
                try:
                    os.remove(tts_file_path)
                except Exception as e:
                    self.log_message(f"Aviso: Não foi possível limpar {tts_file_path}: {e}", "warning")


        def update_tts_volume(self, value):
            """Chamado pelo slider de volume. Atualiza o label e o mixer."""
            volume_float = float(value) / 100.0
            self.mixer_volume = volume_float

            if hasattr(self, 'tts_page') and hasattr(self.tts_page, 'tts_volume_label'):
                self.tts_page.tts_volume_label.configure(text=f"{int(value)}%")

            try:
                pygame.mixer.music.set_volume(volume_float)
            except Exception as e:
                self.log_message(f"Erro ao definir volume: {e}", "error")

        def edit_reward(self):
            """Identifica a recompensa selecionada e abre o modal de edição."""

            if not hasattr(self, 'rewards_page') or not hasattr(self.rewards_page, 'rewards_scroll_frame'): return
            frame = self.rewards_page.rewards_scroll_frame

            selected_reward_name = None
            for item_widget in frame.winfo_children():
                if isinstance(item_widget, ctk.CTkFrame) and getattr(item_widget, '_is_selected', False):
                    selected_reward_name = item_widget.reward_name
                    break

            if selected_reward_name:
                reward_config = self.reward_actions.get(selected_reward_name)

                if reward_config:
                    dialog = EditCommandDialog(
                        self.root, 
                        self, 
                        selected_reward_name, 
                        reward_config
                    )
                    dialog.wait_window()
                else:
                     CustomDialog(self.root, "Aviso", "Recompensa não encontrada na memória.", self.colors, 'warning')
            else:
                CustomDialog(self.root, "Aviso", "Selecione uma recompensa para editar!", self.colors, 'warning')

