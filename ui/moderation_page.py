from functools import partial
import tkinter as tk
import customtkinter as ctk
from ui.components.tooltip import attach_tooltip
from ui.toast_notification import ToastNotification

ACTIONS = ["both", "timeout", "delete"]
ACTION_LABELS = {
    "both":   "Deletar + Timeout",
    "timeout":"Somente timeout",
    "delete": "Somente deletar"
}
LABEL_TO_ACTION = {v: k for k, v in ACTION_LABELS.items()}

class ModerationPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=app.colors['background'])
        self.app = app
        self.grid(row=0, column=0, sticky="nsew")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.content = ctk.CTkScrollableFrame(self, fg_color=self.app.colors['background'])
        self.content.grid(row=0, column=0, sticky="nsew")

        footer = ctk.CTkFrame(self, fg_color=self.app.colors['surface_dark'])
        footer.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 8))
        footer.grid_columnconfigure(0, weight=1)

        self._build_ui(self.content)

        self.reload_btn = ctk.CTkButton(
            footer,
            text="↻ RECARREGAR",
            command=partial(self.load_from_settings, quiet=False),
            fg_color=self.app.colors['surface_light'],
            hover_color=self.app.colors['surface'],
            font=ctk.CTkFont(size=13, weight="bold"),
            height=40,
            corner_radius=10
        )
        self.reload_btn.pack(side=tk.RIGHT, padx=8, pady=8)

        self.save_btn = ctk.CTkButton(
            footer, text="💾 SALVAR", command=self._save,
            fg_color=self.app.colors['success'], hover_color="#00cc6a",
            font=ctk.CTkFont(size=13, weight="bold"), height=40, corner_radius=10
        )
        self.save_btn.pack(side=tk.RIGHT, padx=8, pady=8)

        self.load_from_settings()

    def _section(self, parent, title, subtitle=""):
        box = ctk.CTkFrame(
            parent, fg_color=self.app.colors['surface'], corner_radius=10,
            border_width=2, border_color=self.app.colors['twitch_purple_light']
        )
        box.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        header = ctk.CTkFrame(box, fg_color=self.app.colors['surface'], corner_radius=10)
        header.pack(fill=tk.X, padx=12, pady=(10, 6))

        title_lbl = ctk.CTkLabel(
            header, text=title, font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.app.colors['twitch_purple_light']
        )
        title_lbl.pack(side=tk.LEFT)

        if subtitle:
            sub_lbl = ctk.CTkLabel(
                header, text=subtitle, font=ctk.CTkFont(size=12),
                text_color=self.app.colors['text_secondary']
            )
            sub_lbl.pack(side=tk.LEFT, padx=(10, 0))

        sep = ctk.CTkFrame(box, height=2, fg_color=self.app.colors['twitch_purple_light'])
        sep.pack(fill=tk.X, padx=12, pady=(0, 12))

        return box

    def _build_ui(self, root):
        page_title = ctk.CTkLabel(
            root, text="🛡️ MODERAÇÃO",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=self.app.colors['twitch_purple_light']
        )
        page_title.pack(anchor=tk.W, padx=18, pady=(12, 2))

        s1 = self._section(root, "Ativação e comportamento",
                           "Ligue/desligue a moderação e regras principais.")

        s1g = ctk.CTkFrame(s1, fg_color="transparent")
        s1g.pack(fill=tk.X, padx=12, pady=6)
        for i in range(3):
            s1g.grid_columnconfigure(i, weight=1)

        self.mod_enabled = ctk.CTkSwitch(s1g, text="Ativar moderação", command=self._save)
        self.mod_enabled.grid(row=0, column=0, padx=15, pady=6, sticky="w")
        attach_tooltip(
            self.mod_enabled, "Ativar Moderação",
            "Habilita todas as regras de moderação abaixo (anti-link, blacklist e punição).",
            colors=self.app.colors, delay=350, wraplength=360
        )

        self.anti_link = ctk.CTkSwitch(s1g, text="Anti link spam", command=self._save)
        self.anti_link.grid(row=0, column=1, padx=15, pady=6, sticky="w")
        attach_tooltip(
            self.anti_link, "Anti-link",
            "Bloqueia mensagens contendo URLs/domínios, a menos que o usuário tenha recebido !permit.",
            colors=self.app.colors, delay=350, wraplength=360
        )

        self.blacklist_enabled = ctk.CTkSwitch(s1g, text="Word blacklist", command=self._save)
        self.blacklist_enabled.grid(row=0, column=2, padx=15, pady=6, sticky="w")
        attach_tooltip(
            self.blacklist_enabled, "Lista de bloqueio",
            "Ativa a lista de palavras/trechos proibidos. Configure na seção abaixo.",
            colors=self.app.colors, delay=350, wraplength=360
        )

        s2 = self._section(root, "Blacklist",
                           "Defina palavras/trechos. Uma por linha.")

        bl_label = ctk.CTkLabel(
            s2, text="Palavras bloqueadas (uma por linha)",
            font=ctk.CTkFont(size=12), text_color=self.app.colors['text_secondary']
        )
        bl_label.pack(anchor=tk.W, padx=15, pady=(2, 6))

        self.blacklist_text = ctk.CTkTextbox(s2, height=150)
        self.blacklist_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 12))
        attach_tooltip(
            self.blacklist_text, "Blacklist",
            "Se a mensagem do usuário contiver qualquer linha aqui listada, ela será bloqueada."
            "\ncoloque uma palavra ou trecho por linha.\n"
            "Ex.:\n"
            "palavra1\n"
            "palavra2\n"
            "trecho proibido\n",
            colors=self.app.colors, delay=350, wraplength=360
        )

        s3 = self._section(root, "Comando !permit",
                           "Concede permissão temporária para postar links.")

        grid = ctk.CTkFrame(s3, fg_color="transparent")
        grid.pack(fill=tk.X, padx=12, pady=4)
        grid.grid_columnconfigure(0, weight=0)
        grid.grid_columnconfigure(1, weight=1)
        grid.grid_columnconfigure(2, weight=0)
        grid.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(grid, text="Nome do comando:").grid(row=0, column=0, padx=10, pady=6, sticky="w")
        self.permit_name = ctk.CTkEntry(grid, width=140)
        self.permit_name.grid(row=0, column=1, padx=10, pady=6, sticky="w")
        attach_tooltip(
            self.permit_name, "Nome do comando",
            "Defina o comando usado para permitir links (ex.: !permit, !liberalink...).",
            colors=self.app.colors, delay=350, wraplength=360
        )

        ctk.CTkLabel(grid, text="Duração (s):").grid(row=0, column=2, padx=10, pady=6, sticky="e")
        self.permit_secs = ctk.CTkEntry(grid, width=100)
        self.permit_secs.grid(row=0, column=3, padx=10, pady=6, sticky="w")
        attach_tooltip(
            self.permit_secs, "Duração",
            "Tempo (em segundos) que o usuário poderá postar um link após receber o permit.",
            colors=self.app.colors, delay=350, wraplength=360
        )

        self.permit_msg_enabled = ctk.CTkSwitch(s3, text="Mensagem ao conceder", command=self._save)
        self.permit_msg_enabled.pack(anchor=tk.W, padx=15, pady=(6, 2))
        attach_tooltip(
            self.permit_msg_enabled, "Mensagem de confirmação", 
            "Quando ligado, o bot enviará uma mensagem confirmando o permit para o usuário.",
            colors=self.app.colors, delay=350, wraplength=360
        )

        row2 = ctk.CTkFrame(s3, fg_color="transparent")
        row2.pack(fill=tk.X, padx=12, pady=(0, 10))
        ctk.CTkLabel(row2, text="Template mensagem:").pack(side=tk.LEFT, padx=(0, 10))
        self.permit_msg_template = ctk.CTkEntry(row2)
        self.permit_msg_template.pack(side=tk.LEFT, fill=tk.X, expand=True)
        attach_tooltip(
            self.permit_msg_template, "Template do permit",
            "Use placeholders: @{target} e {seconds}. Ex.: '@{target} pode postar 1 link por {seconds}s.'",
            colors=self.app.colors, delay=350, wraplength=360
        )

        s4 = self._section(root, "Punição",
                           "Defina a ação, o timeout e a mensagem aplicada ao bloquear.")

        grid2 = ctk.CTkFrame(s4, fg_color="transparent")
        grid2.pack(fill=tk.X, padx=12, pady=4)
        grid2.grid_columnconfigure(0, weight=0)
        grid2.grid_columnconfigure(1, weight=1)
        grid2.grid_columnconfigure(2, weight=0)
        grid2.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(grid2, text="Ação ao bloquear:").grid(row=0, column=0, padx=10, pady=6, sticky="w")
        self.punish_action_var = ctk.StringVar(value=ACTION_LABELS[ACTIONS[0]])

        self.punish_action = ctk.CTkOptionMenu(
            grid2,
            variable=self.punish_action_var,
            values=list(ACTION_LABELS.values()),
            command=self._on_action_change,
            width=140
        )
        self.punish_action.grid(row=0, column=1, padx=10, pady=6, sticky="w")

        attach_tooltip(
            self.punish_action, "Ação de punição",
            "Escolha o que fazer ao detectar infração:\n"
            "- Deletar + Timeout: deletar a mensagem e aplicar timeout\n"
            "- Somente timeout: apenas aplicar timeout\n"
            "- Somente deletar: apenas deletar a mensagem",
            colors=self.app.colors, delay=350, wraplength=360
        )

        ctk.CTkLabel(grid2, text="Timeout (s) ao bloquear:").grid(row=0, column=2, padx=10, pady=6, sticky="e")
        self.timeout_secs = ctk.CTkEntry(grid2, width=120)
        self.timeout_secs.grid(row=0, column=3, padx=10, pady=6, sticky="w")
        attach_tooltip(
            self.timeout_secs, "Timeout",
            "Tempo de timeout quando a regra for violada. Ignorado se a ação for 'delete'.",
            colors=self.app.colors, delay=350, wraplength=360
        )

        self.punish_msg_enabled = ctk.CTkSwitch(s4, text="Mensagem de punição no chat")
        self.punish_msg_enabled.pack(anchor=tk.W, padx=15, pady=(6, 2))
        attach_tooltip(
            self.punish_msg_enabled, "Mensagem de punição",
            "Quando ligado, o bot envia uma mensagem pública informando o motivo do bloqueio.",
            colors=self.app.colors, delay=350, wraplength=360
        )

        row3 = ctk.CTkFrame(s4, fg_color="transparent")
        row3.pack(fill=tk.X, padx=12, pady=(0, 10))
        ctk.CTkLabel(row3, text="Mensagem de punição:").pack(side=tk.LEFT, padx=(0, 10))
        self.punish_msg = ctk.CTkEntry(row3)
        self.punish_msg.pack(side=tk.LEFT, fill=tk.X, expand=True)
        attach_tooltip(
            self.punish_msg, "Template da punição",
            "Use {user} e {reason}. Ex.: '@{user} mensagem bloqueada: {reason}'. Deixe vazio para não enviar.",
            colors=self.app.colors, delay=350, wraplength=360
        )

    def _on_action_change(self, *_):
        label = (self.punish_action_var.get() or "").strip()
        action = LABEL_TO_ACTION.get(label, "both")

        if action == "delete":
            self.timeout_secs.configure(state="disabled")
        else:
            self.timeout_secs.configure(state="normal")

    def load_from_settings(self, quiet=True):
        m = self.app.settings.get('moderation', {})
        (self.mod_enabled.select() if m.get('enabled', True) else self.mod_enabled.deselect())
        (self.anti_link.select() if m.get('anti_link_spam', False) else self.anti_link.deselect())
        (self.blacklist_enabled.select() if m.get('blacklist_enabled', False) else self.blacklist_enabled.deselect())

        words = "\n".join(m.get('blacklist_words', []))
        self.blacklist_text.delete("1.0", tk.END)
        self.blacklist_text.insert("1.0", words)

        p = m.get('permit', {})
        self.permit_name.delete(0, tk.END); self.permit_name.insert(0, p.get('command_name', '!permit'))
        self.permit_secs.delete(0, tk.END); self.permit_secs.insert(0, str(p.get('duration_seconds', 60)))
        (self.permit_msg_enabled.select() if p.get('message_enabled', True) else self.permit_msg_enabled.deselect())
        self.permit_msg_template.delete(0, tk.END)
        self.permit_msg_template.insert(0, p.get('message_template', '@{target} pode postar 1 link por {seconds}s.'))

        saved_action = (m.get('action') or 'both').lower()
        self.punish_action_var.set(ACTION_LABELS.get(saved_action, ACTION_LABELS['both']))
        self._on_action_change()

        self.timeout_secs.delete(0, tk.END); self.timeout_secs.insert(0, str(m.get('timeout_seconds', 10)))

        if m.get('punish_message_enabled', True):
            self.punish_msg_enabled.select()
        else:
            self.punish_msg_enabled.deselect()

        self.punish_msg.configure(state="normal")
        msg = m.get('punish_message')
        if not isinstance(msg, str) or msg.strip() == "":
            msg = '@{user} mensagem bloqueada: {reason}'

        self.punish_msg.delete(0, tk.END)
        self.punish_msg.insert(0, msg)

        if not quiet:
            ToastNotification(self, "Recarregado com sucesso!", colors=self.app.colors, toast_type="success")

    def _save(self):
        m = self.app.settings.setdefault('moderation', {})
        m['enabled'] = bool(self.mod_enabled.get())
        m['anti_link_spam'] = bool(self.anti_link.get())
        m['blacklist_enabled'] = bool(self.blacklist_enabled.get())

        words = [w.strip() for w in self.blacklist_text.get('1.0', tk.END).splitlines() if w.strip()]
        m['blacklist_words'] = words

        m['permit'] = {
            'command_name': self.permit_name.get().strip() or '!permit',
            'duration_seconds': int(self.permit_secs.get().strip() or '60'),
            'message_enabled': bool(self.permit_msg_enabled.get()),
            'message_template': self.permit_msg_template.get().strip() or '@{target} pode postar 1 link por {seconds}s.'
        }

        m['action'] = LABEL_TO_ACTION.get(self.punish_action_var.get(), 'both')
        try:
            m['timeout_seconds'] = int(self.timeout_secs.get().strip() or '10')
        except ValueError:
            m['timeout_seconds'] = 10

        m['punish_message_enabled'] = bool(self.punish_msg_enabled.get())
        new_msg = self.punish_msg.get().strip()
        old_msg = m.get('punish_message', '')
        if new_msg or not old_msg:
            m['punish_message'] = new_msg

        try:
            self.app.save_settings(quiet=True)
            self._on_action_change()
            self.punish_msg.configure(state="normal")
            ToastNotification(self, "Salvo com sucesso!", colors=self.app.colors, toast_type="success")
        except Exception:
            ToastNotification(self, "Erro ao salvar!", colors=self.app.colors, toast_type="error")