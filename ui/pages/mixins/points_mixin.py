import os
import json
import tkinter as tk
import customtkinter as ctk

from ui.toast_notification import ToastNotification


class PointsMixin:
    """Lógica de binding entre UI <-> settings para a aba de Pontos."""

    def _pget(self, key, default=None):
        return (self.settings or {}).get(key, default)

    def _pset(self, key, value):
        self.settings[key] = value

    def _pmsg(self):
        return self._pget("points_messages", {}) or {}

    def points_sync_from_settings(self):
        s = self.settings

        if hasattr(self, "points_enabled_switch"):
            self.points_enabled_switch.select() if s.get("points_enabled", False) else self.points_enabled_switch.deselect()

        if hasattr(self, "points_accrual_switch"):
            self.points_accrual_switch.select() if s.get("points_accrual_enabled", True) else self.points_accrual_switch.deselect()

        if hasattr(self, "points_bypass_mods_switch"):
            self.points_bypass_mods_switch.select() if s.get("points_bypass_mods", True) else self.points_bypass_mods_switch.deselect()

        if hasattr(self, "points_cmd_balance_var"):
            self.points_cmd_balance_var.set(s.get("points_cmd_balance", "!pontos"))
        if hasattr(self, "points_cmd_balance_switch"):
            self.points_cmd_balance_switch.select() if s.get("points_cmd_balance_enabled", True) else self.points_cmd_balance_switch.deselect()

        if hasattr(self, "points_cmd_give_var"):
            self.points_cmd_give_var.set(s.get("points_cmd_give", "!give"))
        if hasattr(self, "points_cmd_give_switch"):
            self.points_cmd_give_switch.select() if s.get("points_cmd_give_enabled", True) else self.points_cmd_give_switch.deselect()

        if hasattr(self, "points_cmd_add_var"):
            self.points_cmd_add_var.set(s.get("points_cmd_add", "!addpoints"))
        if hasattr(self, "points_cmd_add_switch"):
            self.points_cmd_add_switch.select() if s.get("points_cmd_add_enabled", True) else self.points_cmd_add_switch.deselect()

        if hasattr(self, "points_cmd_set_var"):
            self.points_cmd_set_var.set(s.get("points_cmd_set", "!setpoints"))
        if hasattr(self, "points_cmd_set_switch"):
            self.points_cmd_set_switch.select() if s.get("points_cmd_set_enabled", True) else self.points_cmd_set_switch.deselect()

        if hasattr(self, "points_per_msg_var"):
            self.points_per_msg_var.set(str(s.get("points_accrual_per_msg", 1)))
        if hasattr(self, "points_cd_user_var"):
            self.points_cd_user_var.set(str(s.get("points_accrual_cooldown_s", 60)))
        if hasattr(self, "points_min_transfer_var"):
            self.points_min_transfer_var.set(str(s.get("points_min_transfer", 1)))

        pm = self._pmsg()
        def _fill(entry_attr, key, default):
            if hasattr(self, entry_attr):
                entry = getattr(self, entry_attr)
                entry.delete(0, tk.END)
                entry.insert(0, pm.get(key, default))

        _fill("msg_balance_entry", "balance", "💰 {user} tem {balance} pontos.")
        _fill("msg_transfer_ok_entry", "transfer_ok", "✅ @{from} transferiu {amount} pontos para @{to}.")
        _fill("msg_transfer_fail_entry", "transfer_fail", "❌ Saldo insuficiente para @{from}.")
        _fill("msg_transfer_invalid_entry", "transfer_invalid", "Quantidade inválida.")
        _fill("msg_usage_give_entry", "usage_give", "Uso: {cmd_give} @alvo <quantidade>")
        _fill("msg_add_ok_entry", "add_ok", "➕ {target} agora tem {balance} pontos.")
        _fill("msg_set_ok_entry", "set_ok", "📝 {target} teve o saldo definido para {balance}.")
        _fill("msg_usage_admin_entry", "usage_admin", "Uso: {cmd} @user <quantidade>")

    def points_save_from_ui(self):
        try:
            s = self.settings

            s["points_enabled"] = bool(self.points_enabled_switch.get()) if hasattr(self, "points_enabled_switch") else s.get("points_enabled", False)
            s["points_accrual_enabled"] = bool(self.points_accrual_switch.get()) if hasattr(self, "points_accrual_switch") else s.get("points_accrual_enabled", True)
            s["points_bypass_mods"] = bool(self.points_bypass_mods_switch.get()) if hasattr(self, "points_bypass_mods_switch") else s.get("points_bypass_mods", True)

            if hasattr(self, "points_cmd_balance_var"):
                s["points_cmd_balance"] = self.points_cmd_balance_var.get().strip()
            if hasattr(self, "points_cmd_balance_switch"):
                s["points_cmd_balance_enabled"] = bool(self.points_cmd_balance_switch.get())

            if hasattr(self, "points_cmd_give_var"):
                s["points_cmd_give"] = self.points_cmd_give_var.get().strip()
            if hasattr(self, "points_cmd_give_switch"):
                s["points_cmd_give_enabled"] = bool(self.points_cmd_give_switch.get())

            if hasattr(self, "points_cmd_add_var"):
                s["points_cmd_add"] = self.points_cmd_add_var.get().strip()
            if hasattr(self, "points_cmd_add_switch"):
                s["points_cmd_add_enabled"] = bool(self.points_cmd_add_switch.get())

            if hasattr(self, "points_cmd_set_var"):
                s["points_cmd_set"] = self.points_cmd_set_var.get().strip()
            if hasattr(self, "points_cmd_set_switch"):
                s["points_cmd_set_enabled"] = bool(self.points_cmd_set_switch.get())

            try:
                s["points_accrual_per_msg"] = int(self.points_per_msg_var.get())
            except Exception:
                pass
            try:
                s["points_accrual_cooldown_s"] = int(self.points_cd_user_var.get())
            except Exception:
                pass
            try:
                s["points_min_transfer"] = int(self.points_min_transfer_var.get())
            except Exception:
                pass

            pm = s.get("points_messages", {}) or {}
            def _save_msg(entry_attr, key):
                if hasattr(self, entry_attr):
                    pm[key] = getattr(self, entry_attr).get().strip()
            _save_msg("msg_balance_entry", "balance")
            _save_msg("msg_transfer_ok_entry", "transfer_ok")
            _save_msg("msg_transfer_fail_entry", "transfer_fail")
            _save_msg("msg_transfer_invalid_entry", "transfer_invalid")
            _save_msg("msg_usage_give_entry", "usage_give")
            _save_msg("msg_add_ok_entry", "add_ok")
            _save_msg("msg_set_ok_entry", "set_ok")
            _save_msg("msg_usage_admin_entry", "usage_admin")
            s["points_messages"] = pm

            self.save_settings()
            self.log_message("💾 Configurações de Pontos salvas.", "success")

            if getattr(self, "bot", None):
                try:
                    if hasattr(self.bot, "points") and self.bot.points:
                        self.bot.points.storage_path = s.get("points_store_file", "points.json")
                except Exception:
                    pass

        except Exception as e:
            self.log_message(f"❌ Erro ao salvar Pontos: {e}", "error")
            ToastNotification(self.root, "Erro ao salvar Pontos", colors=self.colors, toast_type="error")
