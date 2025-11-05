
import os
import sys
import zipfile
from datetime import datetime
from tkinter import filedialog
import json

from ui.toast_notification import ToastNotification

class ProfilesMixin:
    """
    Exporta/Importa um 'perfil' do bot:
      - settings.json
      - commands.json
      - timers.json
      - activity_file.json (se existir)
    Operações usam o diretório atual como base (compatível com PyInstaller).
    Requisitos:
      - self.settings_file / self.commands_file / self.timers_file
      - self.root, self.colors, self.log_message(...)
    """

    def _profile_files(self):
        files = [getattr(self, "settings_file", "settings.json"),
                 getattr(self, "commands_file", "commands.json"),
                 getattr(self, "timers_file", "timers.json"),
                 getattr(self, "activity_file", "activity_log.json")]
        rewards_file = getattr(self, "rewards_file", None)
        if rewards_file:
            files.append(rewards_file)
        return [f for f in files if f and os.path.exists(f)]

    def export_profile(self):
        """Abre dialog e exporta os JSONs num .zip."""
        profile_name = f"LiveChatBot_Profile_{datetime.now():%Y%m%d_%H%M%S}.zip"
        path = filedialog.asksaveasfilename(
            defaultextension=".zip",
            initialfile=profile_name,
            filetypes=[("Perfil do Live ChatBot", "*.zip")],
            title="Salvar perfil como..."
        )
        if not path:
            return
        try:
            with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
                for f in self._profile_files():
                    z.write(f, os.path.basename(f))
            self.log_message(f"✅ Perfil exportado para: {path}", "success")
            ToastNotification(self.root, "Perfil exportado!", colors=self.colors, toast_type="success")
        except Exception as e:
            self.log_message(f"❌ Erro ao exportar perfil: {e}", "error")
            ToastNotification(self.root, "Erro ao exportar perfil", colors=self.colors, toast_type="error")

    def import_profile(self):
        """Abre dialog e importa JSONs de um .zip para substituir os atuais."""
        path = filedialog.askopenfilename(
            filetypes=[("Perfil do Live ChatBot", "*.zip")],
            title="Selecione o arquivo de perfil (.zip)"
        )
        if not path:
            return
        try:
            with zipfile.ZipFile(path, "r") as z:
                z.extractall(".")
            self.log_message("✅ Perfil importado. Recarregando configurações...", "success")
            ToastNotification(self.root, "Perfil importado!", colors=self.colors, toast_type="success")

            self.root.after(1500, lambda: self.restart_app())

        except Exception as e:
            self.log_message(f"❌ Erro ao importar perfil: {e}", "error")
            ToastNotification(self.root, "Erro ao importar perfil", colors=self.colors, toast_type="error")

    def restart_app(self):
        """Reinicia completamente o aplicativo."""
        try:
            python = sys.executable
            os.execl(python, python, *sys.argv)
        except Exception as e:
            self.log_message(f"❌ Erro ao reiniciar o app: {e}", "error")
