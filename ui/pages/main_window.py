from .base_view import ModernTwitchBaseView
from .mixins.bot_mixin import BotMixin
from .mixins.commands_mixin import CommandsMixin
from .mixins.timers_mixin import TimersMixin
from .mixins.rewards_tts_mixin import RewardsTtsMixin
from .mixins.activity_mixin import ActivityMixin
from .mixins.settings_mixin import SettingsMixin
from .mixins.chat_mixin import ChatMixin
from .mixins.utils_mixin import UtilsMixin
from .mixins.profiles_mixin import ProfilesMixin
from .mixins.points_mixin import PointsMixin

class ModernTwitchChatBotGUI(ModernTwitchBaseView, BotMixin, CommandsMixin, TimersMixin, RewardsTtsMixin, ActivityMixin, SettingsMixin, ChatMixin, UtilsMixin, ProfilesMixin, PointsMixin):
    """Refatorado automaticamente em mixins; conserva nomes de métodos/atributos."""
    pass
