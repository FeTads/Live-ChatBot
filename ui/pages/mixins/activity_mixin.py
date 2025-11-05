from datetime import datetime
import json
import os


class ActivityMixin:
        def add_activity_entry(self, raw_event_type, user, details_text):
            """
            Adiciona uma entrada (como dicionário) ao log e agenda atualização da GUI.
            `raw_event_type` é a string do EventSub (e.g., 'channel.follow')
            `user` é o nome do usuário.
            `details_text` é o texto específico (e.g., 'Hidratação!', 'T1', '100 viewers').
            """

            #self.log_message(f"DEBUG: add_activity_entry chamada com: type={raw_event_type}, user={user}", "warning")

            current_datetime = datetime.now()

            log_entry_data = {
                "raw_event_type": raw_event_type,
                "user": user,
                "details": details_text,
                "timestamp_obj": current_datetime
            }
            self.activity_log.append(log_entry_data)

            #self.log_message("DEBUG: Agendando _add_new_activity_bubble...", "warning")
            self.root.after(0, self._add_new_activity_bubble, log_entry_data)


        def _load_initial_activity_display(self):
            """
            Limpa e recria TODOS os 'balões' de atividade no ScrollableFrame,
            usando grid. Chamado APENAS na conexão inicial.
            """
            if not hasattr(self, 'activity_page') or not hasattr(self.activity_page, 'activity_scroll_frame'):
                # self.log_message("Aviso: Tentativa carregar feed antes da ActivityPage estar pronta.", "warning")
                return
            frame = self.activity_page.activity_scroll_frame


            for widget in frame.winfo_children():
                widget.destroy()

            if not self.activity_log:
                 self.log_message("Feed de atividade inicial: Vazio.", "info")
                 return

            #self.log_message(f"Carregando {len(self.activity_log)} entradas no feed inicial...", "info")

            row_index = 0
            for entry_data in reversed(self.activity_log):
                item_widget = self._create_activity_item_widget(frame, entry_data)
                item_widget.grid(row=row_index, column=0, sticky="ew", padx=5, pady=(5, 0))
                row_index += 1


        def _add_new_activity_bubble(self, event_data):
            """
            Adiciona UM novo 'balão' de atividade no TOPO (row=0) do ScrollableFrame,
            usando grid e reconfigurando os existentes.
            """
            #self.log_message(f"DEBUG: _add_new_activity_bubble chamada com dados: {event_data}", "warning")

            if not hasattr(self, 'activity_page') or not hasattr(self.activity_page, 'activity_scroll_frame'):
                # self.log_message("Aviso: Tentativa add balão antes da ActivityPage estar pronta.", "warning")
                return

            frame = self.activity_page.activity_scroll_frame
            existing_widgets = frame.winfo_children()

            for widget in existing_widgets:
                try:
                    grid_info = widget.grid_info()
                    current_row = grid_info.get('row', 0)
                    widget.grid_configure(row=current_row + 1)
                except Exception as e:
                    self.log_message(f"DEBUG: Erro ao reconfigurar grid do widget {widget}: {e}", "error")

            item_widget = self._create_activity_item_widget(frame, event_data)

            item_widget.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 0))
            current_widgets_after_add = frame.winfo_children()
            max_bubbles = self.activity_log.maxlen

            if len(current_widgets_after_add) > max_bubbles:
                widget_to_remove = None
                max_row = -1
                for widget in current_widgets_after_add:
                     try:
                         grid_info = widget.grid_info()
                         row = grid_info.get('row', -1)
                         if row > max_row:
                             max_row = row
                             widget_to_remove = widget
                     except:
                         continue

                if widget_to_remove:
                    self.log_message(f"DEBUG: Removendo balão antigo da row {max_row}.", "info")
                    widget_to_remove.destroy()
                else:
                     self.log_message("DEBUG: Limpeza visual não encontrou widget para remover.", "warning")


        def _load_activity_log_from_file(self):
            """Carrega o histórico de atividades do arquivo JSON, limitado ao maxlen do deque."""
            if os.path.exists(self.activity_log_file):
                try:
                    with open(self.activity_log_file, 'r', encoding='utf-8') as f:
                        log_data_list_full = json.load(f)

                    limit = self.activity_log.maxlen
                    log_data_list = log_data_list_full[-limit:]

                    loaded_entries = []
                    for entry_dict in log_data_list:
                        try:
                            entry_dict['timestamp_obj'] = datetime.fromisoformat(entry_dict['timestamp_iso'])
                            loaded_entries.append(entry_dict)
                        except (ValueError, KeyError):
                            print(f"Aviso: Ignorando entrada de log inválida: {entry_dict}")
                            continue

                    self.activity_log.clear()
                    self.activity_log.extend(loaded_entries)

                    self.log_message(f"📜 Histórico de {len(self.activity_log)} atividades carregado (Limitado aos últimos {limit}).", "system")

                except Exception as e:
                    self.log_message(f"❌ Erro ao carregar {self.activity_log_file}: {e}", "error")
                    self.activity_log.clear()
            else:
                self.log_message("📜 Nenhum histórico de atividades encontrado.", "info")


        def _save_activity_log_to_file(self):
            """Salva o histórico atual de atividades no arquivo JSON."""
            try:
                log_data_list = list(self.activity_log)
                serializable_list = []
                for entry_dict in log_data_list:
                    save_entry = entry_dict.copy() 
                    if isinstance(save_entry.get('timestamp_obj'), datetime):
                        save_entry['timestamp_iso'] = save_entry['timestamp_obj'].isoformat()
                    save_entry.pop('timestamp_obj', None) 
                    serializable_list.append(save_entry)

                with open(self.activity_log_file, 'w', encoding='utf-8') as f:
                    json.dump(serializable_list, f, indent=2, ensure_ascii=False)
                self.log_message(f"📜 Histórico de atividades salvo ({len(serializable_list)} entradas).", "system")

            except Exception as e:
                self.log_message(f"❌ Erro ao salvar {self.activity_log_file}: {e}", "error")


        def _update_all_activity_timestamps(self):
            """Percorre todos os balões visíveis e atualiza seus timestamps."""

            if not hasattr(self, 'activity_page') or not hasattr(self.activity_page, 'activity_scroll_frame') or not self.is_running:
                return
            frame = self.activity_page.activity_scroll_frame

            # self.log_message("DEBUG: Atualizando timestamps...", "info")
            try:
                activity_items = frame.winfo_children()
                for item_widget in activity_items:
                    if hasattr(item_widget, 'timestamp_obj') and hasattr(item_widget, 'time_label_widget'):
                        original_timestamp = item_widget.timestamp_obj
                        time_label = item_widget.time_label_widget
                        new_time_ago_str = self._get_time_ago_string(original_timestamp)
                        if time_label.cget("text") != new_time_ago_str:
                            time_label.configure(text=new_time_ago_str)

            except Exception as e:
                self.log_message(f"Erro ao atualizar timestamps: {e}", "error")

