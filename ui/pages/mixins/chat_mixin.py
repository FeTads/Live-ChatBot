from datetime import datetime
import threading
import tkinter as tk
from ui.custom_dialog import CustomDialog
from ui.toast_notification import ToastNotification


class ChatMixin:
        def start_bot(self):
            """Starts the verification thread."""
            if self.is_running: return
            channel = self.channel_var.get().strip().lower()
            token = self.token_var.get().strip()
            if not channel:
                CustomDialog(master=self.root, title="❌ Erro", text="Digite o nome do canal!", colors=self.colors, dialog_type='error')
                return
            if not token:
                CustomDialog(master=self.root, title="❌ Erro", text="Digite o token OAuth!", colors=self.colors, dialog_type='error')
                return
            
            if not token.startswith("oauth:"):
                token = "oauth:" + token
                self.token_var.set(token)

            self.is_running = True
            self.start_button.configure(state="disabled")
            if hasattr(self, 'navigation_frame'):
                self.navigation_frame.update_status("● VERIFICANDO...", "warning")

            self.channel_entry.configure(state="disabled", fg_color=self.colors['disabled_bg'], text_color=self.colors['disabled_text'])
            self.token_entry.configure(state="disabled", fg_color=self.colors['disabled_bg'], text_color=self.colors['disabled_text'])

            self.thread = threading.Thread(target=self.run_verification_thread, args=(channel, token), daemon=True)
            self.thread.start()


        def stop_bot(self):
            """Stops bot threads, cancels timers, saves log."""
            if not self.is_running: return
            self.is_running = False

            if self.bot: self.bot.disconnect()
            if self.eventsub: self.eventsub.stop()

            self._update_reward_test_buttons_state(False)
            if hasattr(self, 'tts_queue'):
                self.tts_queue.put(None)

            ToastNotification(self.root, f"Desconectado!", colors=self.colors, toast_type="error")
            if self._update_timestamps_after_id:
                self.root.after_cancel(self._update_timestamps_after_id)
                self._update_timestamps_after_id = None

            self._save_activity_log_to_file()

            if hasattr(self, 'start_button'): self.start_button.configure(state="normal")
            if hasattr(self, 'stop_button'): self.stop_button.configure(state="disabled")
            if hasattr(self, 'navigation_frame'): self.navigation_frame.update_status("● OFFLINE", "error")
            if hasattr(self, 'channel_entry'): self.channel_entry.configure(state="normal", fg_color=self.colors['surface_light'], text_color=self.colors['text_primary'])
            if hasattr(self, 'token_entry'): self.token_entry.configure(state="normal", fg_color=self.colors['surface_light'], text_color=self.colors['text_primary'])

            self.log_message("🛑 Bot desconectado!", "system")


        def log_message(self, message, message_type="info"):
            """Adicionar mensagem ao chat"""

            if hasattr(self, 'chat_page') and hasattr(self.chat_page, 'chat_text'):
                chat_widget = self.chat_page.chat_text

                def update_chat():
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    colors = {
                        "info": "#adadb8", "chat": "#bf94ff", "bot": "#00ff7f", 
                        "error": "#ff5555", "system": "#9146FF", "success": "#00ff7f"
                    }
                    color = colors.get(message_type, "#adadb8")
                    chat_widget.configure(state=tk.NORMAL)
                    chat_widget.insert(tk.END, f"[{timestamp}] ", "timestamp")
                    chat_widget.insert(tk.END, f"{message}\n", message_type)
                    chat_widget.tag_config("timestamp", foreground="#6e6e7a")
                    chat_widget.tag_config(message_type, foreground=color)
                    chat_widget.configure(state=tk.DISABLED)
                    chat_widget.see(tk.END)

                self.root.after(0, update_chat)

            else:
                print(f"[{message_type.upper()}] {message}")


        def clear_chat_display(self):
            """Clears the content of the chat display text area."""
            if hasattr(self, 'chat_page') and hasattr(self.chat_page, 'chat_text'):
                chat_widget = self.chat_page.chat_text
                try:
                    chat_widget.configure(state=tk.NORMAL)
                    chat_widget.delete('1.0', tk.END)
                    chat_widget.configure(state=tk.DISABLED)
                    #self.log_message("Chat display cleared.", "system")
                except Exception as e:
                    self.log_message(f"Error clearing chat display: {e}", "error")
            else:
                self.log_message("Error: Chat display widget not found for clearing.", "error")


        def send_message(self, event=None):
            """Enviar mensagem para o chat"""
            if hasattr(self, 'chat_page') and hasattr(self.chat_page, 'message_var'):
                message = self.chat_page.message_var.get().strip()
                if message and self.bot and self.bot.connected:
                    self.bot.send_message(message)
                    self.chat_page.message_var.set("")

