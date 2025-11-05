# 💬 Live ChatBot — Twitch Companion

![Python](https://img.shields.io/badge/Python-3.11-blue.svg)
![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-2ea44f)
![License](https://img.shields.io/badge/license-MIT-green.svg)

Um **chatbot completo para Twitch**, com **interface moderna**, **TTS**, **timers automáticos**, e suporte a **EventSub** (seguidores, subs, cheers, raids).  
Desenvolvido em **Python**, com arquitetura **MVVM** e interface em **CustomTkinter**.

---

## 🧠 Visão geral

O **Live ChatBot** permite automatizar e gerenciar interações da Twitch diretamente do desktop — sem precisar de painel web.  
Ele foi refatorado com base em um projeto monolítico (`gui.py` de +2000 linhas) para uma arquitetura **modular e escalável (MVVM)**, dividida em:

```
chatbot/
├── main.py # Ponto de entrada principal
├── bot.py # Cliente IRC da Twitch
├── eventsub.py # Gerenciador de WebHooks/EventSub
├── services/ # Camada de lógica (BotService, EventSubService, etc.)
├── viewmodels/ # MVVM intermediário (AppViewModel, ConfigViewModel, etc.)
├── ui/ # Interface CustomTkinter
│ ├── pages/ # Telas (SettingsPage, CommandsPage, TimersPage, etc.)
│ ├── pages/mixins/ # Mixins (TTS, Timers, Rewards, Settings, Commands...)
│ └── components/ # Diálogos, Toasts, Widgets
├── images/ # Ícones e imagens do app
└── sounds/ # Sons e alertas
```
---

## ✨ Recursos

✅ **Interface Moderna**  
- Feita em `CustomTkinter` com design escuro e responsivo.  
- Modo MVVM: separação clara entre lógica e UI.

✅ **Bot da Twitch (IRC)**  
- Conecta com canal e responde a comandos `!`.  
- Permissões: viewer / VIP / mod / broadcaster.  
- Suporte a contadores (`$count{}`), variáveis dinâmicas, e comandos randômicos.  
- Comandos customizáveis em JSON via interface.

✅ **Timers Automáticos**  
- Envio periódico de mensagens de chat.  
- Baseado em intervalo + número mínimo de linhas de chat.  
- Controle de ativação/desativação direto na UI.

✅ **EventSub / Alertas**  
- Notificações de Follow, Sub, Gift, Raid e Cheer.  
- Mensagens customizadas e alertas TTS.

✅ **TTS (Text-to-Speech)**  
- Reprodução de voz via Google TTS.  
- Configuração de idioma, voz e volume.  
- Pode ser atrelado a recompensas de canal.

✅ **Logs e Toasts visuais**  
- Sistema de logs colorido na UI.  
- Notificações flutuantes para feedbacks rápidos.

---
```
[View/UI]  →  [ViewModel]  →  [Service]  →  [Core/Backend]
   ↑               ↓               ↓
   └────────────── [Events, Data Bindings, Callbacks]
```
---

## 💜 Autor

**Felipe Forte** ([@FeTads](https://github.com/fetads))  
💻 Dev.

📺 **Twitch:** [twitch.tv/fetads](https://twitch.tv/fetads)  
🐙 **GitHub:** [github.com/fetads](https://github.com/fetads)  
📧 **Contato:** [felps18.08@gmail.com](mailto:felps18.08@gmail.com)
---