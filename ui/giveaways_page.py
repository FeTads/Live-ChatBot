import tkinter as tk
import customtkinter as ctk
from collections import Counter
from datetime import datetime, timezone
from services.giveaway_service import GiveawayService
from ui.components.tooltip import attach_tooltip
from ui.toast_notification import ToastNotification
from ui.custom_dialog import CustomDialog


class GiveawaysPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=app.colors['background'])
        self.app = app
        self.grid(row=0, column=0, sticky="nsew")

        self.service = GiveawayService(
            storage_path=app.settings.get('giveaways_store_file', 'giveaways.json'),
            logger=app.log_message
        )
        self._winner = None
        root_card = ctk.CTkScrollableFrame(self, fg_color=app.colors['surface'], corner_radius=16)
        root_card.pack(fill=tk.BOTH, expand=True, padx=12, pady=(12, 5))

        header = ctk.CTkFrame(root_card, fg_color="transparent")
        header.pack(fill=tk.X, padx=16, pady=(6, 10))

        left_h = ctk.CTkFrame(header, fg_color="transparent")
        left_h.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ctk.CTkLabel(
            left_h, text="🎁", font=ctk.CTkFont(size=24, weight="bold"),
            text_color=app.colors['twitch_purple_light']
        ).pack(side=tk.LEFT, padx=(0, 8))
        ctk.CTkLabel(
            left_h, text="Giveaways (Sorteios)",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=app.colors['twitch_purple_light']
        ).pack(side=tk.LEFT)
        ctk.CTkLabel(
            left_h, text="Preço • Participantes • Chat do vencedor",
            font=ctk.CTkFont(size=12), text_color=app.colors['text_secondary']
        ).pack(side=tk.LEFT, padx=(10, 0))

        right_h = ctk.CTkFrame(header, fg_color="transparent")
        right_h.pack(side=tk.RIGHT)
        save_btn = ctk.CTkButton(
            right_h, text="💾 Salvar",
            command=lambda: (self._save_price_setting(), self.app.save_settings(),
                             ToastNotification(self, "Configurações salvas")),
            fg_color=app.colors.get('success', '#22c55e'),
            hover_color="#00cc6a",
            font=ctk.CTkFont(size=13, weight="bold"), height=34, corner_radius=10
        )
        save_btn.pack()

        ctk.CTkFrame(root_card, fg_color=app.colors['twitch_purple'], height=2, corner_radius=999).pack(
            fill=tk.X, padx=16, pady=(0, 6)
        )

        def section(parent, title_text, icon=""):
            bar = ctk.CTkFrame(parent, fg_color=app.colors['surface'])
            bar.pack(fill=tk.X, padx=16, pady=(12, 6))
            wrap = ctk.CTkFrame(bar, fg_color=app.colors['surface_dark'], corner_radius=12)
            wrap.pack(fill=tk.X)
            ctk.CTkFrame(wrap, fg_color=app.colors['twitch_purple'], height=3, corner_radius=999).pack(
                fill=tk.X, side=tk.TOP
            )
            inner = ctk.CTkFrame(wrap, fg_color=app.colors['surface_dark'])
            inner.pack(fill=tk.BOTH, padx=10, pady=8)
            row_title = ctk.CTkFrame(inner, fg_color="transparent")
            row_title.pack(fill=tk.X)
            ctk.CTkLabel(
                row_title, text=f"{icon}  {title_text}",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=app.colors['twitch_purple_light']
            ).pack(side=tk.LEFT)
            ctk.CTkFrame(inner, fg_color=app.colors['surface'], height=1).pack(fill=tk.X, pady=(6, 8))
            return inner

        sec_switch = section(root_card, "Ativação e preço", "⚙️")
        row0 = ctk.CTkFrame(sec_switch, fg_color="transparent")
        row0.pack(fill=tk.X)
        for i in range(4):
            row0.grid_columnconfigure(i, weight=1)

        self.enable_var = ctk.BooleanVar(value=bool(app.settings.get('giveaways_enabled', True)))
        enable = ctk.CTkSwitch(row0, text="Ativar sorteios", variable=self.enable_var, command=self._toggle_enabled)
        enable.grid(row=0, column=0, sticky="w", padx=8, pady=6)
        attach_tooltip(
            enable, "Sorteios", "Liga/desliga comandos e UI de sorteios.",
            colors=self.app.colors, delay=350, wraplength=320
        )

        ctk.CTkLabel(row0, text="valor (pontos):", font=ctk.CTkFont(size=12)).grid(
            row=1, column=0, sticky="e", padx=(8, 4), pady=6
        )
        self.price_var = tk.StringVar(value=str(app.settings.get("giveaways_entry_price", "0")))
        price_entry = ctk.CTkEntry(
            row0, textvariable=self.price_var,
            fg_color=self.app.colors['surface_light'],
            border_color=self.app.colors['twitch_purple'], width=120
        )
        price_entry.grid(row=1, column=1, sticky="w", padx=(4, 8), pady=6)
        attach_tooltip(
            price_entry, "Preço", "Defina 0 para participação gratuita.",
            colors=self.app.colors, delay=350, wraplength=320
        )

        ctk.CTkLabel(row0, text="Máx. bilhetes por usuário:", font=ctk.CTkFont(size=12)).grid(
            row=1, column=2, sticky="e", padx=(20, 4), pady=6
        )
        self.max_per_user_var = tk.StringVar(
            value=str(self.app.settings.get("giveaways_max_entries_per_user", "0"))
        )
        max_entry = ctk.CTkEntry(
            row0, textvariable=self.max_per_user_var,
            fg_color=self.app.colors['surface_light'],
            border_color=self.app.colors['twitch_purple'], width=120
        )
        max_entry.grid(row=1, column=3, sticky="w", padx=(4, 8), pady=6)
        attach_tooltip(
            max_entry, "Limite por usuário",
            "Número máximo de bilhetes que cada usuário pode ter neste sorteio.\nUse 0 para ilimitado.",
            colors=self.app.colors, delay=350, wraplength=320
        )

        row1 = ctk.CTkFrame(sec_switch, fg_color="transparent")
        row1.pack(fill=tk.X)
        for i in range(4):
            row1.grid_columnconfigure(i, weight=1)

        ctk.CTkLabel(row1, text="Máx. bilhetes p/ subs:", font=ctk.CTkFont(size=12)).grid(
            row=0, column=0, sticky="e", padx=(8, 4), pady=6
        )
        self.max_per_sub_var = tk.StringVar(
            value=str(self.app.settings.get("giveaways_max_entries_per_subs", "0"))
        )
        max_sub_entry = ctk.CTkEntry(
            row1, textvariable=self.max_per_sub_var,
            fg_color=self.app.colors['surface_light'],
            border_color=self.app.colors['twitch_purple'], width=120
        )
        max_sub_entry.grid(row=0, column=1, sticky="w", padx=(4, 8), pady=6)
        attach_tooltip(
            max_sub_entry, "Limite para subs",
            "Número máximo de bilhetes para assinantes (subs). Use 0 para ilimitado.",
            colors=self.app.colors, delay=350, wraplength=320
        )

        ctk.CTkLabel(row1, text="Bônus de tickets p/ subs:", font=ctk.CTkFont(size=12)).grid(
            row=0, column=2, sticky="e", padx=(20, 4), pady=6
        )
        self.sub_bonus_var = tk.StringVar(
            value=str(self.app.settings.get("giveaways_sub_bonus", "0"))
        )
        sub_bonus_entry = ctk.CTkEntry(
            row1, textvariable=self.sub_bonus_var,
            fg_color=self.app.colors['surface_light'],
            border_color=self.app.colors['twitch_purple'], width=120
        )
        sub_bonus_entry.grid(row=0, column=3, sticky="w", padx=(4, 8), pady=6)
        attach_tooltip(
            sub_bonus_entry, "Bônus para subs",
            "Bônus somado ao pedido do sub a cada compra de tickets. Ex.: pediu 3, com bônus 2 vira 5.",
            colors=self.app.colors, delay=350, wraplength=320
        )

        sec_msgs = section(root_card, "Mensagens personalizadas", "💬")
        msgs_grid = ctk.CTkFrame(sec_msgs, fg_color="transparent")
        msgs_grid.pack(fill=tk.X, padx=4, pady=(2, 0))
        for i in range(4):
            msgs_grid.grid_columnconfigure(i, weight=1 if i in (1, 3) else 0)

        def add_msg(row: int, col_base: int, label_text: str, var_name: str, default_text: str, tip: str):
            ctk.CTkLabel(msgs_grid, text=label_text, font=ctk.CTkFont(size=12)).grid(
                row=row, column=col_base, sticky="w", padx=(8, 6), pady=(6, 2)
            )
            var = tk.StringVar(value=self.app.settings.get(var_name, default_text))
            entry = ctk.CTkEntry(
                msgs_grid, textvariable=var,
                fg_color=self.app.colors['surface_light'],
                border_color=self.app.colors['twitch_purple'],
                height=34
            )
            entry.grid(row=row, column=col_base + 1, sticky="ew", padx=(0, 8), pady=(0, 8))
            attach_tooltip(entry, label_text, tip, colors=self.app.colors, delay=350, wraplength=360)
            setattr(self, f"{var_name}_var", var)
            if var_name == "giveaways_not_enough_points_msg":
                self.no_points_msg_var = var
            elif var_name == "giveaways_buy_message":
                self.buy_msg_var = var
            elif var_name == "giveaways_limit_message":
                self.limit_msg_var = var

        add_msg(
            row=0, col_base=0,
            label_text="Mensagem sem pontos:",
            var_name="giveaways_not_enough_points_msg",
            default_text="❌ @{user}, você não tem pontos suficientes para entrar (custa {price}).",
            tip="Mostrada se o usuário não tem pontos. Use {user} e {price}."
        )
        add_msg(
            row=1, col_base=0,
            label_text="Mensagem de compra:",
            var_name="giveaways_buy_message",
            default_text="🎟️ @{user} comprou {tickets} bilhete(s) por {spent} pontos!",
            tip="Mostrada ao comprar bilhetes. Use {user}, {tickets}, {spent}, {price}."
        )
        add_msg(
            row=2, col_base=0,
            label_text="Mensagem de limite:",
            var_name="giveaways_limit_message",
            default_text="❌ @{user}, você já atingiu o limite de {max} bilhete(s).",
            tip="Mostrada ao bater limite. Use {user}, {max}, {current}, {requested}."
        )
        ctk.CTkLabel(msgs_grid, text="").grid(row=1, column=2, sticky="w", padx=8, pady=6)

        sec_cmds = section(root_card, "Comandos", "⌨️")
        grid_cmds = ctk.CTkFrame(sec_cmds, fg_color="transparent")
        grid_cmds.pack(fill=tk.X)
        for i in range(4):
            grid_cmds.grid_columnconfigure(i, weight=1)

        def cmd_field(col, label, key, placeholder):
            wrap = ctk.CTkFrame(grid_cmds, fg_color="transparent")
            wrap.grid(row=0, column=col, sticky="ew", padx=6)
            ctk.CTkLabel(wrap, text=label, font=ctk.CTkFont(size=12)).pack(anchor="w")
            var = tk.StringVar(value=(self.app.settings.get(key, "") or ""))
            entry = ctk.CTkEntry(
                wrap, textvariable=var, placeholder_text=placeholder,
                fg_color=self.app.colors['surface_light'],
                border_color=self.app.colors['twitch_purple']
            )
            entry.pack(fill=tk.X, pady=(2, 0))
            setattr(self, f"{key}_var", var)

        cmd_field(0, "Entrar",   "giveaways_cmd_join",  "!sorteio")
        cmd_field(1, "Sortear",  "giveaways_cmd_draw",  "!sortear")
        cmd_field(2, "Criar",    "giveaways_cmd_start", "!criasorteio")
        cmd_field(3, "Encerrar", "giveaways_cmd_end",   "!encerrasorteio")

        sec_run = section(root_card, "Criar e ações", "🆕")
        run_grid = ctk.CTkFrame(sec_run, fg_color="transparent")
        run_grid.pack(fill=tk.X)
        run_grid.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(run_grid, text="Título:", font=ctk.CTkFont(size=12)).grid(row=0, column=0, sticky="w", padx=8)
        self.title_var = tk.StringVar(value="")

        self.title_entry = ctk.CTkEntry(
            run_grid, textvariable=self.title_var, placeholder_text="Ex.: Gift Card",
            fg_color=self.app.colors['surface_light'], border_color=self.app.colors['twitch_purple']
        )
        self.title_entry.grid(row=0, column=1, sticky="ew", padx=(8, 8), pady=(2, 6))

        self.create_btn = ctk.CTkButton(
            run_grid, text="Criar", command=self._create,
            font=ctk.CTkFont(size=13, weight="bold"),
            height=36, corner_radius=10,
            fg_color=self.app.colors['twitch_purple'],
            hover_color=self.app.colors['twitch_purple_dark']
        )
        self.create_btn.grid(row=0, column=2, padx=8, pady=(2, 6))

        self.status_title = ctk.CTkLabel(
            sec_run, text="",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.app.colors['twitch_purple_light']
        )
        self.status_title.pack(anchor="w", padx=8, pady=(2, 0))

        status_line = ctk.CTkFrame(sec_run, fg_color="transparent")
        status_line.pack(fill=tk.X, padx=8, pady=(2, 6))
        self.current_lbl = ctk.CTkLabel(status_line, text="Sem sorteio em andamento.", font=ctk.CTkFont(size=12))
        self.current_lbl.pack(side=tk.LEFT)

        badges = ctk.CTkFrame(status_line, fg_color="transparent")
        badges.pack(side=tk.RIGHT)
        self.badge_unique = ctk.CTkLabel(
            badges, text="👤 0", font=ctk.CTkFont(size=12, weight="bold"),
            text_color="white", fg_color=app.colors['twitch_purple'], corner_radius=999, padx=10, pady=4
        )
        self.badge_unique.pack(side=tk.LEFT, padx=(0, 6))
        self.badge_tickets = ctk.CTkLabel(
            badges, text="🎟️ 0", font=ctk.CTkFont(size=12, weight="bold"),
            text_color="white", fg_color=app.colors.get('twitch_purple_light', '#8b5cf6'),
            corner_radius=999, padx=10, pady=4
        )
        self.badge_tickets.pack(side=tk.LEFT)

        actions = ctk.CTkFrame(sec_run, fg_color="transparent")
        actions.pack(fill=tk.X, padx=8, pady=(0, 6))
        ctk.CTkButton(
            actions, text="Sortear vencedor", command=self._draw_winner,
            font=ctk.CTkFont(size=13, weight="bold"), height=36, corner_radius=10
        ).pack(side=tk.LEFT, padx=(0, 8))
        ctk.CTkButton(
            actions, text="Resortear", command=self._redraw_winner,
            font=ctk.CTkFont(size=13, weight="bold"), height=36, corner_radius=10
        ).pack(side=tk.LEFT, padx=(0, 8))
        self._lock_btn_text = tk.StringVar(value="Encerrar entradas")
        ctk.CTkButton(
            actions, textvariable=self._lock_btn_text, command=self._toggle_lock,
            font=ctk.CTkFont(size=13, weight="bold"), height=36, corner_radius=10
        ).pack(side=tk.LEFT, padx=(0, 8))

        sec_duo = section(root_card, "Participantes  •  Chat do vencedor", "")
        duo = ctk.CTkFrame(sec_duo, fg_color="transparent")
        duo.pack(fill=tk.BOTH, expand=True)
        duo.grid_columnconfigure(0, weight=1)
        duo.grid_columnconfigure(1, weight=1)
        duo.grid_rowconfigure(0, weight=1)

        left_card = ctk.CTkFrame(duo, fg_color=self.app.colors['surface_dark'], corner_radius=10)
        left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 6), pady=4)
        ctk.CTkLabel(
            left_card, text="Participantes", font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.app.colors['text_secondary']
        ).pack(anchor="w", padx=10, pady=(8, 0))
        ctk.CTkFrame(left_card, fg_color=self.app.colors['surface'], height=1).pack(fill=tk.X, padx=8, pady=(6, 4))
        self.participants_box = ctk.CTkScrollableFrame(
            left_card, fg_color="transparent", corner_radius=10, height=240
        )
        self.participants_box.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        right_card = ctk.CTkFrame(duo, fg_color=self.app.colors['surface_dark'], corner_radius=10)
        right_card.grid(row=0, column=1, sticky="nsew", padx=(6, 0), pady=4)
        ctk.CTkLabel(
            right_card, text="💬 Chat do vencedor", font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.app.colors['text_secondary']
        ).pack(anchor="w", padx=10, pady=(8, 0))
        ctk.CTkFrame(right_card, fg_color=self.app.colors['surface'], height=1).pack(fill=tk.X, padx=8, pady=(6, 4))
        self.winner_chat = ctk.CTkTextbox(
            right_card, fg_color=self.app.colors['surface_light'],
            corner_radius=10, height=240
        )
        self.winner_chat.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))
        self._set_winner_chat_hint()

        sec_hist = section(root_card, "Histórico", "🗂️")
        self.history_box = ctk.CTkScrollableFrame(
            sec_hist, fg_color=self.app.colors['surface_dark'], corner_radius=10, height=160
        )
        self.history_box.pack(fill=tk.BOTH, expand=True, padx=6, pady=(6, 2))

        self._force_reload_from_disk()
        self._refresh_ui()

    def feed_chat(self, user: str, message: str):
        if not self._winner:
            return
        try:
            if user.strip().lower() == self._winner.lower():
                self.winner_chat.insert(tk.END, f"@{user}: {message}\n")
                self.winner_chat.see(tk.END)
        except Exception:
            pass

    def _toggle_enabled(self):
        self.app.settings['giveaways_enabled'] = bool(self.enable_var.get())
        self._save_price_setting()
        self.app.save_settings(quiet=True)
        ToastNotification(self, "Sorteios " + ("ativados" if self.enable_var.get() else "desativados"))

    def _save_price_setting(self):
        try:
            price = int((self.price_var.get() or "0").strip())
            if price < 0:
                price = 0
        except Exception:
            price = 0
        self.app.settings["giveaways_entry_price"] = price
        if hasattr(self, "giveaways_not_enough_points_msg_var"):
            self.app.settings["giveaways_not_enough_points_msg"] = self.giveaways_not_enough_points_msg_var.get().strip()
        if hasattr(self, "giveaways_buy_message_var"):
            self.app.settings["giveaways_buy_message"] = self.giveaways_buy_message_var.get().strip()
        if hasattr(self, "no_points_msg_var"):
            self.app.settings["giveaways_not_enough_points_msg"] = self.no_points_msg_var.get().strip()
        if hasattr(self, "buy_msg_var"):
            self.app.settings["giveaways_buy_message"] = self.buy_msg_var.get().strip()

        try:
            max_per_user = int((self.max_per_user_var.get() or "0").strip())
            if max_per_user < 0:
                max_per_user = 0
        except Exception:
            max_per_user = 0
        self.app.settings["giveaways_max_entries_per_user"] = max_per_user

        try:
            max_per_sub = int((self.max_per_sub_var.get() or "0").strip())
            if max_per_sub < 0:
                max_per_sub = 0
        except Exception:
            max_per_sub = 0
        self.app.settings["giveaways_max_entries_per_subs"] = max_per_sub

        try:
            sub_bonus = int((self.sub_bonus_var.get() or "0").strip())
            if sub_bonus < 0:
                sub_bonus = 0
        except Exception:
            sub_bonus = 0
        self.app.settings["giveaways_sub_bonus"] = sub_bonus

        if hasattr(self, "giveaways_limit_message_var"):
            self.app.settings["giveaways_limit_message"] = self.giveaways_limit_message_var.get().strip()
        elif hasattr(self, "limit_msg_var"):
            self.app.settings["giveaways_limit_message"] = self.limit_msg_var.get().strip()

    def _alert(self, title: str, message: str):
        win = ctk.CTkToplevel(self)
        win.title(title)
        win.transient(self.winfo_toplevel())
        win.grab_set()
        win.configure(fg_color=self.app.colors['surface_dark'])
        try:
            win.iconbitmap(self.app.icon_path)
        except Exception:
            pass

        ctk.CTkLabel(
            win, text=title, font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.app.colors['twitch_purple_light']
        ).pack(padx=18, pady=(16, 6), anchor="w")
        ctk.CTkLabel(
            win, text=message, font=ctk.CTkFont(size=12),
            text_color=self.app.colors['text_primary']
        ).pack(padx=18, pady=(0, 14), anchor="w")

        btn = ctk.CTkButton(win, text="OK", command=win.destroy, height=34, corner_radius=10)
        btn.pack(padx=18, pady=(0, 16), anchor="e")

        win.update_idletasks()
        w, h = 420, 160
        x = self.winfo_rootx() + (self.winfo_width() - w) // 2
        y = self.winfo_rooty() + (self.winfo_height() - h) // 2
        win.geometry(f"{w}x{h}+{x}+{y}")

    def _announce_and_refresh_bot(self, title: str):
        try:
            self._save_price_setting()
            self._sync_settings_from_entries()

            max_per_user = int(self.app.settings.get("giveaways_max_entries_per_user", 0) or 0)
            max_per_sub = int(self.app.settings.get("giveaways_max_entries_per_subs", 0) or 0)
            sub_bonus = int(self.app.settings.get("giveaways_sub_bonus", 0) or 0)
            join_cmd = (self.app.settings.get("giveaways_cmd_join", "!sorteio") or "!sorteio").strip()

            if hasattr(self.app, "bot") and self.app.bot:
                if hasattr(self.app.bot, "_reload_giveaways"):
                    self.app.bot._reload_giveaways()
                if hasattr(self.app.bot, "_notify_giveaways"):
                    self.app.bot._notify_giveaways(refresh=True)

                if self.app.bot.connected:
                    base = f"🎁 Sorteio criado: {title} | Digite {join_cmd} para participar!"
                    lim_user = f" (máximo de {max_per_user} entradas)" if max_per_user > 0 else ""
                    lim_sub = f" (subs até {max_per_sub}" + (f", bônus +{sub_bonus}" if sub_bonus > 0 else "") + ")" if max_per_sub > 0 or sub_bonus > 0 else ""
                    self.app.bot.send_message(base + lim_user + lim_sub)
                    self._set_button_to_end()
        except Exception as e:
            print("⚠️ erro ao anunciar sorteio:", e)

    def _set_create_controls_enabled(self, enabled: bool):
        try:
            self.title_entry.configure(state="normal" if enabled else "disabled")
        except Exception:
            pass

    def _create(self):
        raw = (self.title_var.get() or "").strip()
        if not raw:
            CustomDialog(
                master=self, title="Título vazio",
                text="O sorteio está sem nome. Informe um título antes de criar.",
                colors=self.app.colors, dialog_type='warning'
            )
            return

        title = raw
        self._sync_settings_from_entries()
        self._save_price_setting()
        self.service.create(title)

        try:
            self._set_entries_locked(False)
        except Exception:
            self.app.settings['giveaways_entries_locked'] = False
            self.app.save_settings()

        self._winner = None
        self._set_winner_chat_hint()
        ToastNotification(self, f"Sorteio criado: {title}")

        try:
            if hasattr(self, "_announce_and_refresh_bot"):
                self._announce_and_refresh_bot(title)
        except Exception:
            pass

        self._set_create_controls_enabled(False)
        self._force_reload_from_disk()
        self._refresh_ui()

    def _end(self):
        self._sync_settings_from_entries()
        self._save_price_setting()

        locked = bool(self.app.settings.get('giveaways_entries_locked', False))
        if not locked and not self._winner:
            def _on_answer(val):
                if str(val) in ("yes", "ok", "confirm"):
                    if self.service.close():
                        ToastNotification(self, "Sorteio encerrado.")
                        self._set_button_to_create()
                    self._winner = None
                    self._set_winner_chat_hint()
                    self._set_create_controls_enabled(True)
                    self._force_reload_from_disk()
                    self._refresh_ui()

            CustomDialog(
                master=self,
                title="Confirmar encerramento",
                text=("Você ainda não encerrou as entradas e nem sorteou um vencedor.\n"
                      "Tem certeza que deseja encerrar o sorteio?"),
                colors=self.app.colors,
                dialog_type="warning",
                buttons=[("Cancelar", "no"), ("Sim, encerrar", "yes")],
                callback=_on_answer
            )
            return

        if self.service.close():
            ToastNotification(self, "Sorteio encerrado.")
            self._set_button_to_create()
        self._winner = None
        self._set_winner_chat_hint()
        self._set_create_controls_enabled(True)
        self._force_reload_from_disk()
        self._refresh_ui()

    def _draw_winner(self):
        self._sync_settings_from_entries()
        self._save_price_setting()

        locked = bool(self.app.settings.get('giveaways_entries_locked', False))
        if not locked:
            def _on_answer(val):
                if str(val) in ("yes", "ok", "confirm"):
                    try:
                        self._set_entries_locked(True)
                    except Exception:
                        self.app.settings['giveaways_entries_locked'] = True
                        self.app.save_settings()
                    self._do_draw_winner()

            CustomDialog(
                master=self,
                title="Encerrar entradas antes de sortear",
                text=("Para sortear um vencedor é preciso encerrar as entradas.\n"
                      "Deseja encerrar agora e realizar o sorteio?"),
                colors=self.app.colors,
                dialog_type="warning",
                buttons=[("Cancelar", "no"), ("Encerrar entradas e sortear", "yes")],
                callback=_on_answer
            )
            return

        self._do_draw_winner()

    def _do_draw_winner(self):
        winner = self.service.pick_winner()
        if winner:
            self._winner = winner
            self._reset_winner_chat_area()
            ToastNotification(self, f"Vencedor: @{winner}")

            if self.app.bot and self.app.bot.connected:
                cur = self.service.current() or {}
                msg = self.app.settings.get('giveaways_draw_message', '🎉 @{winner} venceu o sorteio {title}!')
                self.app.bot.send_message(msg.format(winner=winner, title=cur.get('title', 'Sorteio')))

            try:
                self._set_entries_locked(True)
            except Exception:
                self.app.settings['giveaways_entries_locked'] = True
                self.app.save_settings()
        else:
            ToastNotification(self, "Sem participantes ainda.")

        self._force_reload_from_disk()
        self._refresh_ui()

    def _redraw_winner(self):
        self._draw_winner()

    def _reset_winner_chat_area(self):
        self.winner_chat.configure(state="normal")
        self.winner_chat.delete("1.0", tk.END)
        self.winner_chat.insert(tk.END, f"(Somente mensagens de @{self._winner} aparecerão aqui)\n")
        self.winner_chat.see(tk.END)

    def _set_winner_chat_hint(self):
        self.winner_chat.configure(state="normal")
        self.winner_chat.delete("1.0", tk.END)
        self.winner_chat.insert(tk.END, "(Aparecerá aqui o chat do vencedor após sortear)\n")
        self.winner_chat.see(tk.END)

    def _sync_settings_from_entries(self):
        for key in ["giveaways_cmd_join", "giveaways_cmd_draw", "giveaways_cmd_start", "giveaways_cmd_end"]:
            self.app.settings[key] = getattr(self, f"{key}_var").get().strip() or self.app.settings.get(key, "")
        self.app.save_settings(quiet=True)

    def _format_ended_at(self, ended_at: str | None) -> str:
        if not ended_at:
            return "-"
        try:
            iso = ended_at.replace("Z", "+00:00")
            dt_utc = datetime.fromisoformat(iso)
            if dt_utc.tzinfo is None:
                dt_utc = dt_utc.replace(tzinfo=timezone.utc)
            else:
                dt_utc = dt_utc.astimezone(timezone.utc)
            dt_local = dt_utc.astimezone()
            offset_seconds = dt_local.utcoffset().total_seconds()
            offset_hours = int(offset_seconds // 3600)
            sign = "+" if offset_hours >= 0 else "-"
            offset_abs = abs(offset_hours)
            return dt_local.strftime(f"%d/%m/%Y - %H:%Mh GMT {sign}{offset_abs}")
        except Exception:
            return ended_at

    def _refresh_ui(self):
        cur = self.service.current()
        locked = bool(self.app.settings.get('giveaways_entries_locked', False))

        if cur:
            self.status_title.configure(text=f"Em andamento: {cur.get('title')}")
            meta = f"Participantes únicos: {cur.get('unique_count', 0)}  |  Tickets: {cur.get('total_tickets', 0)}"
            if locked:
                meta += "  |  🔒 Entradas encerradas"
            self.current_lbl.configure(text=meta)
            self._set_create_controls_enabled(False)
            self._set_button_to_end()
        else:
            self.status_title.configure(text="")
            self.current_lbl.configure(text="Sem sorteio em andamento.")
            if locked:
                self._set_entries_locked(False)
            self._set_create_controls_enabled(True)
            self._set_button_to_create()

        self._lock_btn_text.set("🔓 Reabrir entradas" if locked else "🛑 Encerrar entradas")

        unique_count = cur.get('unique_count', 0) if cur else 0
        total_tickets = cur.get('total_tickets', 0) if cur else 0
        self.badge_unique.configure(text=f"👤 {unique_count}")
        self.badge_tickets.configure(text=f"🎟️ {total_tickets}")

        for w in list(self.participants_box.winfo_children()):
            w.destroy()
        if cur and cur.get("entrants"):
            counts = Counter(cur["entrants"])
            for user, tickets in sorted(counts.items(), key=lambda x: (-x[1], x[0].lower())):
                row = ctk.CTkFrame(self.participants_box, fg_color="transparent")
                row.pack(fill=tk.X, padx=8, pady=3)
                name = ctk.CTkLabel(row, text=f"@{user}", font=ctk.CTkFont(size=12, weight="bold"))
                name.pack(side=tk.LEFT)
                pill = ctk.CTkLabel(
                    row, text=f"{tickets} ticket(s)",
                    font=ctk.CTkFont(size=11, weight="bold"),
                    text_color="white",
                    fg_color=self.app.colors.get('twitch_purple_light', '#8b5cf6'),
                    corner_radius=999, padx=8, pady=2
                )
                pill.pack(side=tk.RIGHT)
        else:
            ctk.CTkLabel(self.participants_box, text="Sem participantes ainda.").pack(anchor="w", padx=8, pady=8)

        for child in self.history_box.winfo_children():
            child.destroy()
        hist = self.service.history()[:50]
        if not hist:
            ctk.CTkLabel(self.history_box, text="Nenhum sorteio finalizado ainda.").pack(anchor="w", padx=8, pady=6)
        else:
            for item in hist:
                item_row = ctk.CTkFrame(self.history_box, fg_color="transparent")
                item_row.pack(fill=tk.X, padx=8, pady=2)
                ctk.CTkLabel(item_row, text=f"{item.get('title')}",
                             font=ctk.CTkFont(size=12, weight="bold")).pack(side=tk.LEFT)
                ended_fmt = self._format_ended_at(item.get('ended_at', ''))
                ctk.CTkLabel(
                    item_row,
                    text=f"vencedor: @{item.get('winner','-')}  •  {ended_fmt}",
                    font=ctk.CTkFont(size=11),
                    text_color=self.app.colors['text_secondary']
                ).pack(side=tk.RIGHT)

    def refresh_from_bot(self):
        self._force_reload_from_disk()
        self._refresh_ui()

    def set_winner_from_bot(self, winner: str | None):
        self._winner = winner
        if winner:
            self._reset_winner_chat_area()
        else:
            self._set_winner_chat_hint()
        self._force_reload_from_disk()
        self._refresh_ui()

    def _force_reload_from_disk(self):
        try:
            for m in ("reload", "reload_from_disk", "load", "refresh"):
                if hasattr(self.service, m) and callable(getattr(self.service, m)):
                    getattr(self.service, m)()
                    return
        except Exception:
            print("❌ Erro ao recarregar serviço de sorteios via método.")
        try:
            self.service = GiveawayService(
                storage_path=self.app.settings.get('giveaways_store_file', 'giveaways.json'),
                logger=self.app.log_message
            )
        except Exception:
            print("❌ Erro ao recarregar serviço de sorteios.")

    def _set_entries_locked(self, locked: bool):
        self.app.settings['giveaways_entries_locked'] = bool(locked)
        self.app.save_settings()
        try:
            if hasattr(self.app, "bot") and self.app.bot and hasattr(self.app.bot, "_notify_giveaways"):
                self.app.bot._notify_giveaways(refresh=True)
        except Exception:
            pass

    def _toggle_lock(self):
        cur_state = bool(self.app.settings.get('giveaways_entries_locked', False))
        new_state = not cur_state
        self._set_entries_locked(new_state)
        ToastNotification(self, "Entradas encerradas." if new_state else "Entradas reabertas.")
        try:
            if hasattr(self.app, "bot") and self.app.bot and self.app.bot.connected:
                if new_state:
                    self.app.bot.send_message("🔒 Entradas encerradas. Aguarde o sorteio!")
                else:
                    join_cmd = (self.app.settings.get("giveaways_cmd_join", "!sorteio") or "!sorteio").strip()
                    self.app.bot.send_message(f"🔓 Entradas reabertas. Use {join_cmd} para participar!")
        except Exception:
            pass
        self._refresh_ui()

    def _set_button_to_end(self):
        self.create_btn.configure(
            text="Encerrar",
            command=self._end,
            fg_color=self.app.colors.get('error', '#ef4444'),
            hover_color="#b91c1c"
        )

    def _set_button_to_create(self):
        self.create_btn.configure(
            text="Criar",
            command=self._create,
            fg_color=self.app.colors['twitch_purple'],
            hover_color=self.app.colors['twitch_purple_dark']
        )
