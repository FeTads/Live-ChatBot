import json
import os
import re
import customtkinter as ctk

from ui.custom_dialog import CustomDialog
from ui.edit_command_dialog import EditCommandDialog
from ui.toast_notification import ToastNotification


class CommandsMixin:
        def load_commands_from_json(self):
            """Carregar comandos do arquivo JSON"""
            if os.path.exists(self.commands_file):
                try:
                    with open(self.commands_file, 'r', encoding='utf-8') as f:
                        self.default_commands = json.load(f)
                    self.log_message(f"📁 Comandos carregados: {len(self.default_commands)} comandos", "system")
                except Exception as e:
                    self.log_message(f"❌ Erro ao carregar JSON: {e}", "error")
                    self.load_default_commands()
            else:
                self.load_default_commands()
                self.save_commands()


        def load_default_commands(self):
            """Carregar comandos padrão"""
            self.default_commands = {
                "!comandos": {
                    "response": "📋 Comandos disponíveis: !comandos. Use !cmdd add/remove para gerenciar!",
                    "type": "static"
                }
            }
            self.log_message("📝 Comandos padrão carregados", "system")


        def refresh_commands_list(self):
            """Atualiza a área de exibição de comandos na CommandsPage."""
            if hasattr(self, 'commands_page') and hasattr(self.commands_page, 'commands_scroll_frame'):
                frame = self.commands_page.commands_scroll_frame

                for widget in frame.winfo_children():
                    widget.destroy()

                row_index = 0
                for cmd, config in self.default_commands.items():
                    item_widget = self._create_command_item_widget(frame, cmd, config)
                    item_widget.grid(row=row_index, column=0, sticky="ew", padx=5, pady=(5, 0))
                    row_index += 1
            else:
                 self.log_message("DEBUG: `commands_page` ou `commands_scroll_frame` não encontrados durante refresh.", "warning")


        def save_commands(self):
            """Salvar comandos no JSON"""
            try:
                with open(self.commands_file, 'w', encoding='utf-8') as f:
                    json.dump(self.default_commands, f, indent=2, ensure_ascii=False)
                self.log_message("💾 Comandos salvos com sucesso!", "success")
                ToastNotification(self.root, f"Comandos salvos!", colors=self.colors, toast_type="success")
            except Exception as e:
                self.log_message(f"❌ Erro ao salvar: {e}", "error")


        def reload_commands(self):
            """Recarregar comandos do JSON"""
            self.load_commands_from_json()
            self.refresh_commands_list()
            if self.bot:
                self.bot.config['commands'] = self.default_commands
            self.log_message("🔄 Comandos recarregados!", "system")


        def add_command(self):
            """Adicionar novo comando"""
            cmd = self.new_cmd_var.get().strip()
            response = self.new_response_var.get().strip()

            permission = self.new_cmd_permission_var.get().lower()

            if not cmd.startswith('!'):
                cmd = '!' + cmd

            if cmd and response:
                self.default_commands[cmd] = {
                    "response": response,
                    "type": "static",
                    "permission": permission
                }
                self.new_cmd_var.set("")
                self.new_response_var.set("")
                self.new_cmd_permission_var.set("Everyone")
                self.refresh_commands_list()
                self.save_commands()
                if self.bot:
                    self.bot.config['commands'] = self.default_commands
                self.log_message(f"✅ Comando {cmd} (Perm: {permission}) adicionado!", "success")
            else:
                CustomDialog(master=self.root, title="⚠️ Aviso", text="Preencha o comando e a resposta!", colors=self.colors, dialog_type='warning')


        def edit_command(self):
            """Identifica o comando selecionado e abre o modal de edição."""
            if not hasattr(self, 'commands_page') or not hasattr(self.commands_page, 'commands_scroll_frame'): return
            frame = self.commands_page.commands_scroll_frame

            selected_command_name = None
            for item_widget in frame.winfo_children():
                if isinstance(item_widget, ctk.CTkFrame) and getattr(item_widget, '_is_selected', False):
                    selected_command_name = item_widget.command_name
                    break

            if selected_command_name:
                command_config = self.default_commands.get(selected_command_name)

                if command_config:
                    EditCommandDialog(self.root, self, selected_command_name, command_config)
                else:
                     CustomDialog(self.root, "Aviso", "Comando não encontrado na memória.", self.colors, 'warning')
            else:
                CustomDialog(self.root, "Aviso", "Selecione um comando para editar!", self.colors, 'warning')


        def remove_command(self):
            """Shows confirmation dialog before removing the selected command."""
            if not hasattr(self, 'commands_page') or not hasattr(self.commands_page, 'commands_scroll_frame'): return
            frame = self.commands_page.commands_scroll_frame

            selected_command_name = None
            for item_widget in frame.winfo_children():
                if isinstance(item_widget, ctk.CTkFrame) and getattr(item_widget, '_is_selected', False):
                    selected_command_name = item_widget.command_name
                    break

            if selected_command_name:
                cmd = selected_command_name
                dialog = CustomDialog(
                    master=self.root,
                    title="🗑️ Confirmar Remoção",
                    text=f"Você tem certeza que deseja remover o comando:\n\n{cmd}?",
                    colors=self.colors,
                    dialog_type='warning',
                    buttons=[("Sim, Remover", "yes"), ("Não", "no")],
                    callback=lambda result: self._handle_generic_deletion(
                        result,
                        cmd,
                        self.default_commands,
                        self.refresh_commands_list,
                        "command"
                    )
                )
                dialog.wait_window()
            else:
                CustomDialog(master=self.root, title="⚠️ Aviso", text="Selecione um comando para remover!", colors=self.colors, dialog_type='warning')


        def process_cmdd_command(self, user, message, permissions):
            """
            Processa o comando !cmdd (administração de comandos), 
            incluindo a detecção e inicialização de novos contadores.
            """

            is_allowed = permissions.get('is_mod', False) or permissions.get('is_broadcaster', False)
            if not is_allowed:
                self.log_message(f"🚨 Acesso negado: {user} tentou usar !cmdd.", "warning")
                return f"🚨 {user}, você precisa ser um moderador ou streamer para usar este comando."

            parts = message.split(' ', 3)

            if len(parts) < 2:
                return "❌ Use: !cmdd add <comando> <resposta> OU !cmdd remove <comando>"

            action = parts[1].lower()

            if action == "add" and len(parts) == 4:
                cmd = parts[2].strip()
                response_text = parts[3].strip()

                if not cmd.startswith('!'):
                    cmd = '!' + cmd

                if cmd and response_text:

                    new_counters = re.findall(r'\$count\{([^}]+)\}', response_text)
                    base_keys_to_init = set()
                    is_settings_modified = False

                    if new_counters:
                        for full_tag_content in new_counters:
                            full_tag_content = full_tag_content.strip()

                            match_op = re.match(r'^(\w+)\s*([\+\-])\s*(\d+)$', full_tag_content, re.IGNORECASE)

                            if match_op:
                                base_key = match_op.group(1).lower()
                            else:
                                base_key = full_tag_content.lower()
                            base_keys_to_init.add(base_key)

                        counts = self.settings.get('counts', {})

                        for count_key in base_keys_to_init:
                            if count_key not in counts:
                                counts[count_key] = 0
                                self.log_message(f"🆕 Contador '$count{{{count_key}}}' inicializado para 0.", "system")
                                is_settings_modified = True

                        self.settings['counts'] = counts 
                        if is_settings_modified:
                            self.save_settings()
                    self.default_commands[cmd] = { "response": response_text, "type": "static" }

                    self.refresh_commands_list()
                    self.save_commands()

                    if self.bot:
                        self.bot.config['commands'] = self.default_commands

                    return f"✅ {user} adicionou: {cmd}. Contadores verificados."

                return "❌ Formato: !cmdd add <comando> <resposta>"

            elif action == "remove" and len(parts) >= 3:
                cmd = parts[2].strip()

                if not cmd.startswith('!'):
                    cmd = '!' + cmd

                if cmd in self.default_commands and cmd not in ["!comandos", "!cmdd"]:
                    del self.default_commands[cmd]

                    self.refresh_commands_list()
                    self.save_commands()

                    if self.bot:
                        self.bot.config['commands'] = self.default_commands

                    return f"✅ {user} removeu: {cmd}"

                return f"❌ Comando {cmd} não encontrado ou é essencial!"

            return "❌ Uso: !cmdd add <comando> <resposta> OU !cmdd remove <comando>"


        def edit_command_by_name(self, command_name):
            """Helper para o botão de edição que abre o modal diretamente."""
            command_config = self.default_commands.get(command_name)

            if command_config:
                EditCommandDialog(self.root, self, command_name, command_config)
            else:
                CustomDialog(self.root, "Aviso", "Comando não encontrado na memória.", self.colors, 'warning')


        def _handle_command_state_toggle(self, command_name, item_widget):
            """
            Manipula o clique no switch, salva no JSON, e ATUALIZA O WIDGET LOCALMENTE.
            Isso elimina a 'piscada'.
            """
            current_state_in_memory = self.default_commands[command_name].get('disabled', False)
            new_state = not current_state_in_memory

            self.default_commands[command_name]['disabled'] = new_state
            self.save_commands()

            switch_widget = item_widget.grid_slaves(row=0, column=2)[0]
            new_button_color = self.colors['error'] if new_state else self.colors['success']
            switch_widget.configure(button_color=new_button_color)

            status = "DESABILITADO" if new_state else "HABILITADO"
            self.log_message(f"🔄 Comando '{command_name}' agora está {status}.", "system")

