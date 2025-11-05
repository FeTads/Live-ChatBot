from datetime import datetime
import json
import os

import customtkinter as ctk

from ui.custom_dialog import CustomDialog
from ui.edit_timer_dialog import EditTimerDialog
from ui.toast_notification import ToastNotification


class TimersMixin:
        def load_timers_from_file(self):
            """Carrega os timers do arquivo JSON."""
            if os.path.exists(self.timers_file):
                try:
                    with open(self.timers_file, 'r', encoding='utf-8') as f:
                        self.timers = json.load(f)
                    self.log_message(f"⏱️ {len(self.timers)} Timers carregados.", "system")
                except Exception as e:
                    self.log_message(f"❌ Erro ao carregar timers.json: {e}", "error")
                    self.timers = {}
            else:
                self.timers = {}
                self.save_timers()

            for name, config in self.timers.items():
                config['last_run'] = datetime.now()
                config['lines_since_last_run'] = 0


        def save_timers(self):
            """Salva os timers no arquivo JSON (sem a chave last_run)."""
            serializable_timers = {}
            try:
                for name, config in self.timers.items():
                    temp_config = config.copy()
                    temp_config.pop('last_run', None)
                    serializable_timers[name] = temp_config

                with open(self.timers_file, 'w', encoding='utf-8') as f:
                    json.dump(serializable_timers, f, indent=2, ensure_ascii=False)
                self.log_message("💾 Timers salvos com sucesso!", "success")
                ToastNotification(self.root, "Timers salvos!", colors=self.colors, toast_type="success")
            except Exception as e:
                self.log_message(f"❌ Erro ao salvar timers: {e}", "error")
                ToastNotification(self.root, "Erro ao salvar timers!", colors=self.colors, toast_type="error")


        def _timer_loop_check(self):
            """
            Verifica se algum timer precisa ser disparado.
            Roda a cada 60 segundos (1 "Tick").
            """
            if not self.is_running or not self.bot:
                if self.is_running:
                     self.root.after(60000, self._timer_loop_check)
                return

            self.timer_tick_count += 1
            lines_this_tick = self.bot.chat_lines_this_tick
            self.bot.chat_lines_this_tick = 0

            for name, config in self.timers.items():
                if not config.get('enabled', False):
                    continue

                config['lines_since_last_run'] = config.get('lines_since_last_run', 0) + lines_this_tick

                interval_min = config.get('interval_min', 10)

                if (self.timer_tick_count % interval_min) == 0:
                    min_lines = config.get('min_lines', 0)

                    if config['lines_since_last_run'] >= min_lines:
                        self.log_message(f"⏱️ Disparando Timer: {name}", "system")
                        self.bot.send_message(config['message'])
                        config['lines_since_last_run'] = 0 

            self.root.after(60000, self._timer_loop_check)


        def add_new_timer(self):
            """Adiciona um novo timer pego da UI."""
            if not hasattr(self, 'timers_page'): return

            page = self.timers_page
            name = page.new_timer_name_var.get().strip()
            message = page.new_timer_msg_var.get().strip()
            try:
                interval = int(page.new_timer_interval_var.get())
                min_lines = int(page.new_timer_lines_var.get())
            except ValueError:
                CustomDialog(self.root, "Erro", "Intervalo e Linhas Mínimas devem ser números inteiros!", self.colors, 'error')
                return

            if not name or not message:
                CustomDialog(self.root, "Erro", "Nome do Timer e Mensagem são obrigatórios!", self.colors, 'error')
                return

            if name in self.timers:
                CustomDialog(self.root, "Erro", f"O timer '{name}' já existe!", self.colors, 'error')
                return

            self.timers[name] = {
                "message": message,
                "interval_min": interval,
                "min_lines": min_lines,
                "enabled": True,
                "last_run": datetime.now()
            }

            self.log_message(f"⏱️ Timer '{name}' adicionado.", "success")
            self.save_timers()
            self.refresh_timers_list()

            page.new_timer_name_var.set("")
            page.new_timer_msg_var.set("")
            page.new_timer_interval_var.set("15")
            page.new_timer_lines_var.set("5")


        def remove_timer(self):
            """Remove o timer selecionado após confirmação."""
            if not hasattr(self, 'timers_page') or not hasattr(self.timers_page, 'timers_scroll_frame'): return
            frame = self.timers_page.timers_scroll_frame

            selected_timer_name = None
            for item_widget in frame.winfo_children():
                if isinstance(item_widget, ctk.CTkFrame) and getattr(item_widget, '_is_selected', False):
                    selected_timer_name = item_widget.timer_name
                    break

            if selected_timer_name:
                CustomDialog(
                    master=self.root,
                    title="🗑️ Confirmar Remoção",
                    text=f"Você tem certeza que deseja remover o timer:\n\n{selected_timer_name}?",
                    colors=self.colors,
                    dialog_type='warning',
                    buttons=[("Sim, Remover", "yes"), ("Não", "no")],
                    callback=lambda result: self._handle_generic_deletion(
                        result,
                        selected_timer_name,
                        self.timers,
                        self.refresh_timers_list,
                        "timer"
                    )
                )
            else:
                CustomDialog(self.root, "Aviso", "Selecione um timer para remover!", self.colors, 'warning')


        def open_edit_timer_dialog(self):
            """Abre o modal de edição para o timer selecionado."""
            if not hasattr(self, 'timers_page') or not hasattr(self.timers_page, 'timers_scroll_frame'): return
            frame = self.timers_page.timers_scroll_frame

            selected_timer_name = None
            for item_widget in frame.winfo_children():
                if isinstance(item_widget, ctk.CTkFrame) and getattr(item_widget, '_is_selected', False):
                    selected_timer_name = item_widget.timer_name
                    break

            if selected_timer_name:
                timer_config = self.timers.get(selected_timer_name)

                if timer_config:
                    EditTimerDialog(self.root, self, selected_timer_name, timer_config)
                else:
                     CustomDialog(self.root, "Aviso", "Timer não encontrado na memória.", self.colors, 'warning')
            else:
                CustomDialog(self.root, "Aviso", "Selecione um timer para editar!", self.colors, 'warning')


        def reload_timers(self):
            """Recarrega os timers do JSON e atualiza a UI."""
            self.load_timers_from_file()
            self.refresh_timers_list()


        def toggle_timer_state(self, timer_name, item_widget, switch_widget):
            """Alterna o estado 'enabled' do timer e atualiza a UI localmente."""
            if timer_name not in self.timers:
                self.log_message(f"Erro: Timer '{timer_name}' não encontrado.", "error")
                return

            current_state = self.timers[timer_name].get('enabled', False)
            new_state = not current_state
            self.timers[timer_name]['enabled'] = new_state
            self.save_timers() 

            new_fg_color = self.colors['surface_dark'] if new_state else self.colors['disabled_bg']
            item_widget.configure(fg_color=new_fg_color)

            new_button_color = self.colors['success'] if new_state else self.colors['error']
            switch_widget.configure(button_color=new_button_color)

            status = "HABILITADO" if new_state else "DESABILITADO"
            self.log_message(f"⏱️ Timer '{timer_name}' agora está {status}.", "system")


        def refresh_timers_list(self):
            """Atualiza a área de exibição de timers, aplicando o filtro de busca."""
            if not hasattr(self, 'timers_page') or not hasattr(self.timers_page, 'timers_scroll_frame'):
                return

            frame = self.timers_page.timers_scroll_frame
            search_term = self.timers_page.search_var.get().lower()

            for widget in frame.winfo_children():
                widget.destroy()

            row_index = 0
            for name, config in self.timers.items():
                if search_term and search_term not in name.lower() and search_term not in config.get('message', '').lower():
                    continue

                item_widget = self._create_timer_item_widget(frame, name, config)
                item_widget.grid(row=row_index, column=0, sticky="ew", padx=5, pady=(5, 0))
                row_index += 1
