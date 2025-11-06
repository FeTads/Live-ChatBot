import tkinter as tk
import customtkinter as ctk

from ui.components.tooltip import attach_tooltip


class PointsPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=app.colors['background'])
        self.app = app
        self.grid(row=0, column=0, sticky="nsew")

        root_card = ctk.CTkScrollableFrame(
            self,
            fg_color=app.colors['surface'],
            corner_radius=16
        )
        root_card.pack(fill=tk.BOTH, expand=True, padx=12, pady=(12, 5))

        header = ctk.CTkFrame(root_card, fg_color="transparent")
        header.pack(fill=tk.X, padx=16, pady=(14, 8))

        badge = ctk.CTkLabel(
            header, text="🪙",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=app.colors['twitch_purple_light']
        )
        badge.pack(side=tk.LEFT, padx=(0, 8))

        title = ctk.CTkLabel(
            header, text="Sistema de Pontos",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=app.colors['twitch_purple_light']
        )
        title.pack(side=tk.LEFT)

        subtitle = ctk.CTkLabel(
            header, text="Gerencie saldo, transferência, acúmulo automático e mensagens.",
            font=ctk.CTkFont(size=12), text_color=app.colors['text_secondary']
        )
        subtitle.pack(side=tk.LEFT, padx=(10, 0))

        def section(parent, title_text, icon=""):
            bar = ctk.CTkFrame(parent, fg_color=app.colors['surface'])
            bar.pack(fill=tk.X, padx=16, pady=(14, 6))
            wrap = ctk.CTkFrame(bar, fg_color=app.colors['surface_dark'], corner_radius=10)
            wrap.pack(fill=tk.X)
            line = ctk.CTkFrame(wrap, fg_color=app.colors['twitch_purple'], height=3)
            line.pack(fill=tk.X, side=tk.TOP)
            inner = ctk.CTkFrame(wrap, fg_color=app.colors['surface_dark'])
            inner.pack(fill=tk.X, padx=10, pady=8)

            label = ctk.CTkLabel(inner, text=f"{icon}  {title_text}", font=ctk.CTkFont(size=14, weight="bold"))
            label.pack(anchor="w")
            return inner

        sec_switches = section(root_card, "Ativação e comportamento", "⚙️")
        grid1 = ctk.CTkFrame(sec_switches, fg_color="transparent")
        grid1.pack(fill=tk.X, pady=(6, 2))
        for i in range(3):
            grid1.grid_columnconfigure(i, weight=1)

        self.app.points_enabled_switch = ctk.CTkSwitch(grid1, text="Ativar sistema de pontos")
        self.app.points_enabled_switch.grid(row=0, column=0, sticky="w", padx=8, pady=6)
        attach_tooltip(
            self.app.points_enabled_switch,
            "Sistema de pontos",
            "Liga/desliga todos os recursos de pontos.",
            colors=self.app.colors,
            delay=350,
            wraplength=320
        )

        self.app.points_accrual_switch = ctk.CTkSwitch(grid1, text="Acúmulo automático por mensagem")
        self.app.points_accrual_switch.grid(row=0, column=1, sticky="w", padx=8, pady=6)
        attach_tooltip(
            self.app.points_accrual_switch,
            "Acúmulo automático",
            "Concede pontos automaticamente quando o usuário envia mensagens (respeitando cooldown).",
            colors=self.app.colors,
            delay=350,
            wraplength=320
        )

        self.app.points_bypass_mods_switch = ctk.CTkSwitch(grid1, text="Bypass de cooldown p/ Mods/Streamer")
        self.app.points_bypass_mods_switch.grid(row=0, column=2, sticky="w", padx=8, pady=6)
        attach_tooltip(
            self.app.points_bypass_mods_switch,
            "Bypass para staff",
            "Se ligado, Mods/Streamer não sofrem cooldown de acúmulo.",
            colors=self.app.colors,
            delay=350,
            wraplength=320
        )

        sec_cmds = section(root_card, "Comandos", "⌨️")
        cmds = ctk.CTkFrame(sec_cmds, fg_color="transparent")
        cmds.pack(fill=tk.X, pady=(6, 2))

        for i in range(6):
            cmds.grid_columnconfigure(i, weight=1 if i in (1, 4) else 0)

        def labeled_entry_with_switch(parent, r, c0, label_text, var_attr, switch_attr, tip_text_entry=None, tip_text_switch=None):
            ctk.CTkLabel(parent, text=label_text, font=ctk.CTkFont(size=12)).grid(
                row=r, column=c0, sticky="w", padx=8, pady=(8, 4)
            )
            var = tk.StringVar(value="")
            entry = ctk.CTkEntry(
                parent, textvariable=var,
                fg_color=self.app.colors['surface_light'],
                border_color=self.app.colors['twitch_purple']
            )
            entry.grid(row=r, column=c0 + 1, sticky="ew", padx=(8, 8), pady=(8, 4))

            sw = ctk.CTkSwitch(parent, text="")
            sw.select()
            sw.grid(row=r, column=c0 + 2, sticky="w", padx=(4, 8), pady=(8, 4))

            if tip_text_entry:
                attach_tooltip(
                    entry,
                    f"{label_text}",
                    tip_text_entry,
                    colors=self.app.colors,
                    delay=350,
                    wraplength=320
                )
            if tip_text_switch:
                attach_tooltip(
                    sw,
                    f"{label_text} - Ativar",
                    tip_text_switch,
                    colors=self.app.colors,
                    delay=350,
                    wraplength=320
                )

            setattr(self.app, var_attr, var)
            setattr(self.app, switch_attr, sw)
            return entry, sw

        labeled_entry_with_switch(
            cmds, 0, 0,
            "Comando saldo:",
            "points_cmd_balance_var",
            "points_cmd_balance_switch",
            tip_text_entry="Ex.: !pontos, !saldo, !coins",
            tip_text_switch="Liga/desliga o comando de consulta de saldo."
        )
        labeled_entry_with_switch(
            cmds, 0, 3,
            "Comando transferir:",
            "points_cmd_give_var",
            "points_cmd_give_switch",
            tip_text_entry="Ex.: !give, !transferir, !pay",
            tip_text_switch="Liga/desliga o comando de transferência de pontos."
        )

        labeled_entry_with_switch(
            cmds, 1, 0,
            "Comando add (mods):",
            "points_cmd_add_var",
            "points_cmd_add_switch",
            tip_text_entry="Ex.: !addpontos, !addcoins",
            tip_text_switch="Liga/desliga o comando de adicionar pontos (mods/streamer)."
        )
        labeled_entry_with_switch(
            cmds, 1, 3,
            "Comando set (mods):",
            "points_cmd_set_var",
            "points_cmd_set_switch",
            tip_text_entry="Ex.: !setpontos, !setcoins",
            tip_text_switch="Liga/desliga o comando de definir saldo (mods/streamer)."
        )

        sec_acc = section(root_card, "Acúmulo e limites", "⏱️")
        acc = ctk.CTkFrame(sec_acc, fg_color="transparent")
        acc.pack(fill=tk.X, pady=(6, 2))
        for i in range(6):
            acc.grid_columnconfigure(i, weight=1 if i % 2 == 1 else 0)

        ctk.CTkLabel(acc, text="Pontos por mensagem:", font=ctk.CTkFont(size=12)).grid(
            row=0, column=0, sticky="w", padx=8, pady=(8, 4)
        )
        self.app.points_per_msg_var = tk.StringVar(value="1")
        e_ppm = ctk.CTkEntry(acc, textvariable=self.app.points_per_msg_var,
                             fg_color=self.app.colors['surface_light'],
                             border_color=self.app.colors['twitch_purple'])
        e_ppm.grid(row=0, column=1, sticky="ew", padx=(8, 8), pady=(8, 4))
        attach_tooltip(
            e_ppm,
            "Pontos por mensagem",
            "Quantidade de pontos ganhos por mensagem (respeita o cooldown).",
            colors=self.app.colors,
            delay=350,
            wraplength=320
        )

        ctk.CTkLabel(acc, text="Cooldown por usuário (s):", font=ctk.CTkFont(size=12)).grid(
            row=0, column=2, sticky="w", padx=8, pady=(8, 4)
        )
        self.app.points_cd_user_var = tk.StringVar(value="60")
        e_cd = ctk.CTkEntry(acc, textvariable=self.app.points_cd_user_var,
                            fg_color=self.app.colors['surface_light'],
                            border_color=self.app.colors['twitch_purple'])
        e_cd.grid(row=0, column=3, sticky="ew", padx=(8, 8), pady=(8, 4))
        attach_tooltip(
            e_cd,
            "Cooldown",
            "Tempo mínimo entre ganhos para o MESMO usuário.",
            colors=self.app.colors,
            delay=350,
            wraplength=320
        )

        ctk.CTkLabel(acc, text="Mínimo p/ transferir:", font=ctk.CTkFont(size=12)).grid(
            row=0, column=4, sticky="w", padx=8, pady=(8, 4)
        )
        self.app.points_min_transfer_var = tk.StringVar(value="1")
        e_min = ctk.CTkEntry(acc, textvariable=self.app.points_min_transfer_var,
                             fg_color=self.app.colors['surface_light'],
                             border_color=self.app.colors['twitch_purple'])
        e_min.grid(row=0, column=5, sticky="ew", padx=(8, 8), pady=(8, 4))
        attach_tooltip(
            e_min,
            "Mínimo de transferência",
            "Quantidade mínima para !give.",
            colors=self.app.colors,
            delay=350,
            wraplength=320
        )

        sec_msgs = section(root_card, "Mensagens", "💬")
        msgs = ctk.CTkFrame(sec_msgs, fg_color="transparent")
        msgs.pack(fill=tk.BOTH, expand=True, pady=(6, 2))
        msgs.grid_columnconfigure(1, weight=1)

        def msg_row(r, label, attr, tip_title, tip_body):
            ctk.CTkLabel(msgs, text=label, font=ctk.CTkFont(size=12)).grid(
                row=r, column=0, sticky="w", padx=8, pady=(8, 4)
            )
            entry = ctk.CTkEntry(msgs,
                                 fg_color=self.app.colors['surface_light'],
                                 border_color=self.app.colors['twitch_purple'])
            entry.grid(row=r, column=1, sticky="ew", padx=(8, 8), pady=(8, 4))
            setattr(self.app, attr, entry)
            attach_tooltip(
                entry,
                tip_title,
                tip_body,
                colors=self.app.colors,
                delay=350,
                wraplength=360
            )

        msg_row(0, "Mensagem saldo", "msg_balance_entry",
                "Modelo de saldo", "Ex.: '💰 {user} tem {balance} pontos.'")
        msg_row(1, "Transferência OK", "msg_transfer_ok_entry",
                "Modelo sucesso", "Ex.: '✅ @{from} transferiu {amount} pontos para @{to}.'")
        msg_row(2, "Transferência falhou", "msg_transfer_fail_entry",
                "Modelo falha", "Ex.: '❌ Saldo insuficiente para @{from}.'")
        msg_row(3, "Transferência inválida", "msg_transfer_invalid_entry",
                "Modelo inválido", "Ex.: 'Quantidade inválida.'")
        msg_row(4, "Uso do give", "msg_usage_give_entry",
                "Uso do comando", "Ex.: 'Uso: {cmd_give} @alvo <quantidade>'")
        msg_row(5, "Add OK (admin)", "msg_add_ok_entry",
                "Modelo add", "Ex.: '➕ {target} agora tem {balance} pontos.'")
        msg_row(6, "Set OK (admin)", "msg_set_ok_entry",
                "Modelo set", "Ex.: '📝 {target} teve o saldo definido para {balance}.'")
        msg_row(7, "Uso admin (add/set)", "msg_usage_admin_entry",
                "Uso admin", "Ex.: 'Uso: {cmd} @user <quantidade>'")

        footer = ctk.CTkFrame(self, fg_color=self.app.colors['surface_dark'])
        footer.pack(side=tk.BOTTOM, fill=tk.X, padx=(15, 15))

        save_btn = ctk.CTkButton(
            footer, text="💾 SALVAR", command=self.app.points_save_from_ui,
            fg_color=self.app.colors['success'], hover_color="#00cc6a",
            font=ctk.CTkFont(size=13, weight="bold"), height=40, corner_radius=10
        )
        save_btn.pack(side=tk.RIGHT, padx=12, pady=10)

        self.app.points_sync_from_settings()
