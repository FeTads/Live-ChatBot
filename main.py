import os
from services.bot_service import BotService
from services.eventsub_service import EventSubService
from viewmodels.app_viewmodel import AppViewModel
from ui.pages.main_window import ModernTwitchChatBotGUI

import pygame
try:
    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    pygame.mixer.music.set_volume(0.5)
    #debug
    print("🔊 Pygame mixer inicializado no main.py")
except Exception as e:
    print(f"⚠️ Falha ao inicializar mixer: {e}")

def main():

    app = ModernTwitchChatBotGUI(root=None)

    bot = BotService(gui=app, config={})
    eventsub = EventSubService(gui=app, config={})
    vm = AppViewModel(bot=bot, eventsub=eventsub)

    try:
        app.vm = vm
    except Exception:
        pass

    bot.set_gui(app)
    eventsub.set_gui(app)

    app.mainloop()

if __name__ == "__main__":
    main()
