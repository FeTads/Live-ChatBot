import websocket
import json
import requests
import time

class TwitchEventSubClient:
    def __init__(self, gui, config):
        self.gui = gui
        self.config = config
        self.ws = None
        self.session_id = None
        self.is_running = True
        self.logger = self.gui.log_message
        self.headers_api = {
            'Authorization': f'Bearer {self.config["api_token"]}',
            'Client-Id': self.config['client_id'],
            'Content-Type': 'application/json'
        }

    def run(self):
        """Loop principal do WebSocket"""
        try:
            self.ws = websocket.create_connection("wss://eventsub.wss.twitch.tv/ws")
            #self.logger("EventSub conectado. Aguardando 'welcome'...", "system")
            
            while self.is_running:
                try:
                    message = self.ws.recv()
                    if not message:
                        break
                    data = json.loads(message)
                    self.on_message(data)
                
                except websocket.WebSocketConnectionClosedException:
                    self.logger("🔌 Conexão EventSub fechada.", "system")
                    break
                except Exception as e:
                    self.logger(f"💥 Erro no EventSub: {e}", "error")
                    time.sleep(5)
                    
        except Exception as e:
            self.logger(f"❌ Falha ao conectar ao EventSub: {e}", "error")
            self.logger("Verifique o token e a conexão.", "error")
        
        self.stop()
        self.logger("🛑 EventSub parado.", "system")

    def stop(self):
        """Para o loop e fecha o WebSocket"""
        self.is_running = False
        if self.ws:
            try:
                self.ws.close()
            except:
                pass

    def on_message(self, data):
        """Processa mensagens recebidas do WebSocket"""
        msg_type = data['metadata']['message_type']
        
        if msg_type == 'session_welcome':
            self.session_id = data['payload']['session']['id']
            #self.logger(f"✅ EventSub 'Welcome' recebido (ID: {self.session_id[:8]}...)", "success")
            self.subscribe_to_events()
            
        elif msg_type == 'notification':
            self.handle_notification(data['payload'])
            
        elif msg_type == 'session_reconnect':
            self.logger("🔄 EventSub pedindo reconexão...", "system")
            pass
            
        elif msg_type == 'revocation':
            sub_type = data['payload']['subscription']['type']
            self.logger(f"🚫 Inscrição revogada: {sub_type}", "error")

    def subscribe(self, event_type, version, condition):
        """Envia um pedido HTTP para a API para se inscrever em um evento"""
        body = {
            "type": event_type,
            "version": version,
            "condition": condition,
            "transport": {
                "method": "websocket",
                "session_id": self.session_id
            }
        }
        
        try:
            resp = requests.post('https://api.twitch.tv/helix/eventsub/subscriptions', headers=self.headers_api, json=body)
            resp.raise_for_status()

        except requests.RequestException as e:
            self.logger(f"❌ Falha ao inscrever em {event_type}", "error")
            if e.response:
                self.logger(f"Detalhe: {e.response.json()}", "error")

    def subscribe_to_events(self):
        """Se inscreve em todos os eventos que queremos ouvir"""

        broadcaster_id = self.config['target_channel_id']
        mod_id = self.config['bot_user_id']
        
        self.subscribe(
            "channel.follow", "2", 
            {"broadcaster_user_id": broadcaster_id, "moderator_user_id": mod_id}
        )
        
        self.subscribe(
            "channel.subscribe", "1", 
            {"broadcaster_user_id": broadcaster_id}
        )
        
        self.subscribe(
            "channel.raid", "1", 
            {"to_broadcaster_user_id": broadcaster_id}
        )

        self.subscribe(
            "channel.channel_points_custom_reward_redemption.add", "1",
            {"broadcaster_user_id": self.config['target_channel_id']}
        )

    def handle_notification(self, payload):
        """Lida com a notificação do evento e envia a mensagem no chat"""
        event_type = payload['subscription']['type']
        event = payload['event']

        action = None
        
        settings = self.config.get('settings', {})
        reward_actions = settings.get('reward_actions', {})
        tts_reward_name = settings.get('tts_reward_name', '').strip()
        tts_enabled = settings.get('tts_enabled', False)

        user_name = event.get('user_name', '')
        user_input = event.get('user_input', '').strip() 
        
        placeholders = {
            'user': user_name,
            'input': user_input,
            'channel': self.config['channel']
        }
        
        def send_chat_msg(message):
            if self.gui.bot and self.gui.bot.connected:
                self.gui.bot.send_message(message)
            else:
                self.logger("... Evento recebido, mas bot IRC está offline.", "info")

        def trigger_sound(file_path):
            self.gui.root.after(0, self.gui.play_sound, file_path)

        #self.logger(f"DEBUG: Evento recebido - tipo: {event_type}", "warning")

        if event_type == 'channel.follow':
            event = payload['event']
            user_name = event['user_name']
            activity_msg = f"Follow: {user_name}"
            self.logger(f"✨ {activity_msg}!", "system")
            self.gui.add_activity_entry(event_type, user_name, "Follow")
            
            msg_template = settings.get('msg_follow', "Obrigado pelo follow, @{user}! <3")
            send_chat_msg(msg_template.format(**placeholders))
            
        elif event_type == 'channel.subscribe':
            event = payload['event']
            user_name = event['user_name']
            tier = event['tier'].replace("000", "") 
            is_gift = event.get('is_gift', False)
            
            activity_details = f"T{tier}" + (" (Gift)" if is_gift else "")
            activity_msg = f"Sub (T{tier}): {user_name}" + (" (Gift)" if is_gift else "")
            self.logger(f"⭐ {activity_msg}!", "system")
            self.gui.add_activity_entry(event_type, user_name, activity_details)
            
            if is_gift:
                 msg_template = settings.get('msg_gift_sub', "Obrigado pelo Sub de presente, @{user}! <3")
            else:
                 msg_template = settings.get('msg_sub', "Obrigado pelo Sub (Tier {tier}), @{user}! <3")
            send_chat_msg(msg_template.format(**placeholders))

        elif event_type == 'channel.raid':
            event = payload['event']
            raider_name = event['from_broadcaster_user_name']
            viewers = event['viewers']
            
            activity_details = f"{viewers} viewers"
            activity_msg = f"Raid de {raider_name} ({viewers} viewers)"
            self.logger(f"⚔️ {activity_msg}!", "system")
            self.gui.add_activity_entry(event_type, raider_name, activity_details)
            
            msg_template = settings.get('msg_raid', "RAID! Bem-vindos, time do @{raider}! ({viewers} pessoas)")
            send_chat_msg(msg_template.format(**placeholders))

        elif event_type == 'channel.channel_points_custom_reward_redemption.add':
            reward_title = event['reward']['title']

            if reward_title in reward_actions:
                action = reward_actions[reward_title]

            is_tts_event = (
                tts_enabled and 
                tts_reward_name and 
                reward_title.lower() == tts_reward_name.lower() and 
                user_input
            )

            is_tts_event = (
                tts_enabled and tts_reward_name and 
                reward_title.lower() == tts_reward_name.lower() and user_input
            )
            
            if is_tts_event:
                self.gui.add_activity_entry("tts.redemption", user_name, user_input)
                self.gui.request_tts_playback(user_input)
            else:
                self.gui.add_activity_entry(event_type, user_name, reward_title)


            if reward_title in reward_actions:
                action = reward_actions[reward_title]

                if 'sound' in action and action['sound']:
                    trigger_sound(action['sound']) 
                
                if 'message' in action and action['message']:
                    msg_template = action['message']
                    send_chat_msg(msg_template.format(**placeholders))

            