import socket
import time
import random
import re
from datetime import datetime
import requests
from services.twitch_api import TwitchAPIService
from services.points_service import PointsService

class TwitchChatBot:
    def __init__(self, gui, config):
        self.gui = gui
        self.config = config
        self.connected = False
        self.sock = None
        
        self.server = "irc.chat.twitch.tv"
        self.port = 6667

        self.last_chatter_update = 0
        self.chatters = []

        self.chat_lines_this_tick = 0

        self.twitch_api = TwitchAPIService(self.config, self.gui.log_message)
        self.points = PointsService(
            storage_path=self.gui.settings.get('points_store_file', 'points.json'),
            logger=self.gui.log_message
        )
        self._points_last_msg_time = {}
        
    def connect(self):
        """Conectar ao servidor Twitch"""
        try:
            self.sock = socket.socket()
            self.sock.connect((self.server, self.port))
            
            self.send_raw(f"PASS {self.config['token']}")
            self.send_raw(f"NICK {self.config['bot_user_name']}")
            self.send_raw(f"JOIN #{self.config['channel']}")
            self.send_raw("CAP REQ :twitch.tv/commands")
            self.send_raw("CAP REQ :twitch.tv/tags")
            
            self.connected = True
            self.gui.log_message(f"✅ Conectado ao canal #{self.config['channel']}!", "success")
            self.gui.log_message("💡 Use !cmdd add/remove para gerenciar comandos!", "info")
            
        except Exception as e:
            self.gui.log_message(f"❌ Erro de conexão: {e}", "error")
            self.connected = False
    
    def disconnect(self):
        """Desconectar do servidor"""
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
        self.connected = False
    
    def send_raw(self, message):
        """Enviar mensagem raw"""
        if self.sock:
            self.sock.send(f"{message}\r\n".encode('utf-8'))
    
    def send_message(self, message):
        """Enviar mensagem para o chat"""
        if self.connected:
            self.send_raw(f"PRIVMSG #{self.config['channel']} :{message}")
            self.gui.log_message(f"🤖 {message}", "bot")
    
    def parse_message(self, line):
        """Parsear mensagem do IRC e extrair tags de permissão."""
        if "PRIVMSG" not in line:
            return

        try:
            tags_match = re.search(r'^@([^ ]+) :', line)
            user_match = re.search(r':(\w+)!', line)
            message_match = re.search(r'PRIVMSG #\w+ :(.+)', line)
            
            if not (user_match and message_match):
                return

            user = user_match.group(1)
            message = message_match.group(1).strip()

            permissions = {'is_mod': False, 'is_broadcaster': False, 'is_vip': False}
            is_cheer = False
            bits_amount = 0
            
            if tags_match:
                tags_raw = tags_match.group(1)
                tags = {tag.split('=')[0]: tag.split('=')[1] for tag in tags_raw.split(';') if '=' in tag}

                if user.lower() == self.config['channel'].lower() or ('badges' in tags and 'broadcaster/1' in tags['badges']):
                    permissions['is_broadcaster'] = True
                    permissions['is_mod'] = True
                
                if tags.get('mod') == '1':
                    permissions['is_mod'] = True
                
                if 'badges' in tags and 'vip/1' in tags['badges']:
                    permissions['is_vip'] = True
                
                if 'bits' in tags and tags['bits'].isdigit() and int(tags['bits']) > 0:
                    is_cheer = True
                    bits_amount = int(tags['bits'])
            
            if user.lower() != self.config['bot_user_name'].lower():
                self.chat_lines_this_tick += 1

            self.gui.log_message(f"{user}: {message}", "chat")
            try:
                ps = self.gui.settings or {}
                if ps.get("points_enabled", False) and ps.get("points_accrual_enabled", True):
                    if user.lower() != self.config['bot_user_name'].lower():
                        now = time.time()
                        cd = int(ps.get("points_accrual_cooldown_s", 60) or 0)
                        last = self._points_last_msg_time.get(user.lower(), 0)

                        bypass = ps.get("points_bypass_mods", True) and (permissions.get('is_mod') or permissions.get('is_broadcaster'))
                        if bypass or now - last >= cd:
                            amount = int(ps.get("points_accrual_per_msg", 1) or 0)
                            if amount > 0:
                                self.points.add(user, amount)
                            self._points_last_msg_time[user.lower()] = now
            except Exception as e:
                self.gui.log_message(f"⚠️ points acumulados: {e}", "warning")
            
            if is_cheer:
                self._process_cheer_event(user, message, bits_amount)

            ps = self.gui.settings or {}
            points_on = ps.get("points_enabled", False)

            def _cmd_maybe(name_key, enabled_key, default_cmd, default_enabled=True):
                c = (ps.get(name_key, default_cmd) or default_cmd).strip().lower()
                en = bool(ps.get(enabled_key, default_enabled))
                if not c:
                    en = False
                return c if (points_on and en) else None

            cmd_balance = _cmd_maybe("points_cmd_balance", "points_cmd_balance_enabled", "!pontos", True)
            cmd_give    = _cmd_maybe("points_cmd_give",    "points_cmd_give_enabled",    "!give",   True)
            cmd_add     = _cmd_maybe("points_cmd_add",     "points_cmd_add_enabled",     "!addpoints", True)
            cmd_set     = _cmd_maybe("points_cmd_set",     "points_cmd_set_enabled",     "!setpoints", True)

            points_cmds = {c for c in [cmd_balance, cmd_give, cmd_add, cmd_set] if c}

            mod_only_cmds = set()
            if permissions['is_mod']:
                mod_only_cmds.update(["!cmdd", "!setcount", "!addcount"])

            config_cmds = set(self.config.get('commands', {}).keys())

            candidate_cmds = points_cmds.union(config_cmds).union(mod_only_cmds)

            found_command = None
            start_index = -1

            for part in message.split():
                if not part.startswith('!'):
                    continue

                m = re.match(r'^![a-z0-9_]+', part.lower())
                if not m:
                    continue
                root = m.group(0)

                if root in candidate_cmds:
                    found_command = root
                    start_index = message.lower().find(root)
                    break

            if found_command and start_index != -1:
                full_command_message = message[start_index:].strip()
                self.process_command(user, full_command_message, permissions)

        except Exception as e:
            self.gui.log_message(f"Erro ao parsear: {e}", "error")

    
    def process_command(self, user, message, permissions):
        """Processar comandos do chat"""
        cmd_parts = message.split(' ')
        cmd = cmd_parts[0].lower()

        user_level = 0
        if permissions.get('is_vip', False): user_level = 1
        if permissions.get('is_mod', False): user_level = 2
        if permissions.get('is_broadcaster', False): user_level = 3

        perm_map = {"everyone": 0, "vip": 1, "mod": 2, "broadcaster": 3}

        ps = self.gui.settings or {}

        points_on = ps.get("points_enabled", False)
        def _cmd_active(name_key, enabled_key, default_cmd, default_enabled=True):
            c = (ps.get(name_key, default_cmd) or default_cmd).strip().lower()
            en = bool(ps.get(enabled_key, default_enabled))
            if not c:
                en = False
            return c, en

        #print(f"{cmd}")

        cmd_balance, cmd_balance_enabled = _cmd_active("points_cmd_balance", "points_cmd_balance_enabled", "!pontos", True)
        cmd_give,    cmd_give_enabled    = _cmd_active("points_cmd_give",    "points_cmd_give_enabled",    "!give",   True)
        cmd_add,     cmd_add_enabled     = _cmd_active("points_cmd_add",     "points_cmd_add_enabled",     "!addpoints", True)
        cmd_set,     cmd_set_enabled     = _cmd_active("points_cmd_set",     "points_cmd_set_enabled",     "!setpoints", True)

        min_transfer = int(ps.get("points_min_transfer", 1) or 1)
        pm = ps.get("points_messages", {}) or {}

        if points_on and cmd_balance_enabled and cmd == cmd_balance:
            target = user
            if len(cmd_parts) >= 2:
                target = cmd_parts[1].lstrip("@")
            bal = self.points.get(target)
            msg = (pm.get("balance", "💰 {user} tem {balance} pontos.")
                    .format(user=target, balance=bal))
            self.send_message(msg)
            return

        if points_on and cmd_give_enabled and cmd == cmd_give:
            if len(cmd_parts) < 3:
                self.send_message((pm.get("usage_give", "Uso: {cmd_give} @alvo <quantidade>")).format(cmd_give=cmd_give))
                return
            to_user = cmd_parts[1].lstrip("@")
            try:
                amount = int(cmd_parts[2])
            except Exception:
                self.send_message(pm.get("transfer_invalid", "Quantidade inválida."))
                return
            if amount < min_transfer:
                self.send_message(pm.get("transfer_invalid", "Quantidade inválida."))
                return
            ok = self.points.transfer(user, to_user, amount)
            if ok:
                self.send_message((pm.get("transfer_ok", "✅ @{from} transferiu {amount} pontos para @{to}."))
                                .format(**{"from": user, "to": to_user, "amount": amount}))
            else:
                self.send_message((pm.get("transfer_fail", "❌ Saldo insuficiente para @{from}."))
                                .format(**{"from": user}))
            return

        if points_on and (cmd_add_enabled or cmd_set_enabled) and cmd in (cmd_add, cmd_set):
            if (cmd == cmd_add and not cmd_add_enabled) or (cmd == cmd_set and not cmd_set_enabled):
                return

            if user_level < perm_map["mod"]:
                self.send_message(f"🚨 {user}, você não tem permissão para usar {cmd}.")
                return
            if len(cmd_parts) < 3:
                self.send_message((pm.get("usage_admin", "Uso: {cmd} @user <quantidade>")).format(cmd=cmd))
                return
            target = cmd_parts[1].lstrip("@")
            try:
                amount = int(cmd_parts[2])
            except Exception:
                self.send_message((pm.get("usage_admin", "Uso: {cmd} @user <quantidade>")).format(cmd=cmd))
                return

            if cmd == cmd_add:
                bal = self.points.add(target, amount)
                self.send_message((pm.get("add_ok", "➕ {target} agora tem {balance} pontos."))
                                .format(target=target, balance=bal))
            else:
                bal = self.points.set(target, amount)
                self.send_message((pm.get("set_ok", "📝 {target} teve o saldo definido para {balance}."))
                                .format(target=target, balance=bal))
            return
        
        if cmd == "!setcount" or cmd == "!addcount":

            if user_level < perm_map["mod"]:
                self.send_message(f"🚨 {user}, você não tem permissão para usar {cmd}.")
                return
            
            parts = message.split(' ', 3)
            if len(parts) < 3:
                self.send_message(f"❌ {user}, uso incorreto. Tente: {cmd} <contador> <valor>")
                return
            
            action = cmd[1:]
            count_name = parts[1].lower().strip() 
            value_str = parts[2].strip()
            
            try:
                value = int(value_str)
                if 'counts' not in self.config['settings']:
                    self.config['settings']['counts'] = {}
                
                current_counts = self.config['settings']['counts']
                current_value = current_counts.get(count_name, 0)
                
                if action == "setcount":
                    new_value = value
                    self.send_message(f"💀 Contador '{count_name}' definido para {new_value}.")
                elif action == "addcount":
                    new_value = current_value + value
                    self.send_message(f"➕ {count_name.capitalize()} aumentou para {new_value}.")
                
                current_counts[count_name] = new_value
                self.gui.save_settings(quiet=True)
                
            except ValueError:
                self.send_message(f"❌ {user}, o valor '{value_str}' não é um número válido.")
            except Exception as e:
                self.gui.log_message(f"❌ Erro ao manipular contador {count_name}: {e}", "error")
            return
        
        if cmd == "!cmdd":
            if user_level < perm_map["mod"]:
                self.send_message(f"🚨 {user}, você não tem permissão para usar {cmd}.")
                return
            
            response = self.gui.process_cmdd_command(user, message, permissions)
            if response:
                self.send_message(response)
            return
        
        if cmd in self.config['commands']:
            command_config = self.config['commands'][cmd]

            if command_config.get('disabled', False):
                # self.gui.log_message(f"Comando '{cmd}' desabilitado.", "info")
                return
            
            required_perm_str = command_config.get('permission', 'everyone').lower()
            required_level = perm_map.get(required_perm_str, 0)
            
            if user_level < required_level:
                self.send_message(f"🚨 {user}, você não tem permissão para usar {cmd}.")
                return

            allowed, cd_left = self.gui.check_command_cooldown(cmd, user, command_config, permissions)
            if not allowed:
                # if permissions.get("is_mod") or permissions.get("is_broadcaster"):
                #     self.send_message(f"⏳ {cmd} em cooldown ({cd_left}s).")
                return

            response = self.generate_response(user, command_config, message)
            if response:
                self.send_message(response)

            self.gui.arm_command_cooldown(cmd, user, command_config, permissions)

    
    def generate_response(self, user, command_config, full_message):
        """
        Gera resposta para comando, com suporte a variáveis dinâmicas e contadores.
        (full_message é passado do process_command)
        """
        cmd_type = command_config.get('type', 'static')
        response_template = command_config['response']
        
        format_vars = {'user': user}
        format_vars['channel'] = self.config['channel']
        response_output = response_template

        if '{uptime}' in response_output:
            response_output = response_output.replace('{uptime}', self._format_uptime())
        
        should_save_settings = False
        counts_dict = self.config['settings'].get('counts', {}).copy()

        parts = full_message.split(' ')
        try:
            target_user = parts[1].strip().lstrip('@')
            format_vars['touser'] = '@' + target_user
        except IndexError:
             format_vars['touser'] = '@' + user
        
        if '{rand_user}' in response_template:
            if time.time() - self.last_chatter_update > 60 or not self.chatters:
                 self._update_chatters_list()
                 
            if self.chatters:
                 format_vars['rand_user'] = '@' + random.choice(self.chatters)
            else:
                 format_vars['rand_user'] = '@visitante'
        
        count_matches = re.findall(r'\$count\{([^}]+)\}', response_template)
        if count_matches:
            for full_tag_content in count_matches: 
                
                final_display_value = 0
                count_key = full_tag_content.lower().strip()
                
                match_op = re.match(r'^(\w+)\s*([\+\-])\s*(\d+)$', full_tag_content.strip(), re.IGNORECASE)
                
                if match_op:
                    count_key = match_op.group(1).lower()
                    operator = match_op.group(2)
                    operand = int(match_op.group(3))
                    
                    current_value = counts_dict.get(count_key, 0)
                    
                    if operator == '+':
                        new_value = current_value + operand
                    else:
                        new_value = current_value - operand
                    counts_dict[count_key] = new_value
                    final_display_value = new_value
                    should_save_settings = True
                    
                else:
                    final_display_value = counts_dict.get(count_key, 0)
                response_output = response_output.replace(
                    f"$count{{{full_tag_content}}}", 
                    str(final_display_value),
                    1
                )
        
        dynamic_vars = {}
        if cmd_type == 'random_range':
            min_val = command_config.get('min', 1)
            max_val = command_config.get('max', 100)
            value = random.randint(min_val, max_val)
            
            dynamic_vars['value'] = value
            dynamic_vars['size'] = value
            
            #usavel?
            reaction = ""
            if 'reactions' in command_config:
                reactions = command_config['reactions']
                if value < 5:
                    reaction = random.choice(reactions.get('tiny', [""]))
                elif value < 7:
                    reaction = random.choice(reactions.get('small', [""]))
                elif value < 10:
                    reaction = random.choice(reactions.get('medium_small', [""]))
                elif value < 12:
                    reaction = random.choice(reactions.get('medium_large', [""]))
                elif value < 14:
                    reaction = random.choice(reactions.get('medium', [""]))
                elif value < 18:
                    reaction = random.choice(reactions.get('large_medium', [""]))
                elif value < 22:
                    reaction = random.choice(reactions.get('large', [""]))
                else:
                    reaction = random.choice(reactions.get('huge', [""]))
            
            dynamic_vars['reaction'] = reaction

        elif cmd_type == 'random_list':
            options = command_config.get('options', [])
            if options:
                selected = random.choice(options)
                dynamic_vars['value'] = selected
                dynamic_vars['joke'] = selected
            
        elif cmd_type == 'dynamic_time':
            current_time = datetime.now().strftime("%H:%M:%S")
            dynamic_vars['value'] = current_time
            dynamic_vars['time'] = current_time

        rand_matches = re.findall(r'\$rand\{(\s*\d+\s*,\s*\d+\s*)\}', response_output, re.IGNORECASE)

        if rand_matches:
            for full_range_content in rand_matches:
                full_tag = f"$rand{{{full_range_content}}}"
                
                try:
                    min_val, max_val = [int(n.strip()) for n in full_range_content.split(',')]
                    
                    if min_val <= max_val:
                        random_value = random.randint(min_val, max_val)
                    else:
                        random_value = random.randint(max_val, min_val) 

                    response_output = response_output.replace(full_tag, str(random_value), 1)

                except ValueError:
                    self.gui.log_message(f"❌ Erro de formato no $rand: {full_range_content}. Usando valor padrão 0.", "error")
                    response_output = response_output.replace(full_tag, "0", 1)

        if should_save_settings:
            self.config['settings']['counts'] = counts_dict
            self.gui.save_settings(quiet=True)

        final_format_vars = {**format_vars, **dynamic_vars}
        
        try:
            return response_output.format(**final_format_vars)
        except KeyError as e:
            self.gui.log_message(f"❌ Erro de placeholder: Variável {e} não preenchida.", "error")
            return f"❌ Erro no comando! Variável {e} não reconhecida ou preenchida."
        except Exception as e:
            self.gui.log_message(f"❌ Erro de formatação no comando: {e}", "error")
            return f"❌ Erro grave no comando! (Erro: {e})"
    

    def _format_uptime(self) -> str:
        try:
            login = self.config.get('channel', '') or self.config.get('channel_login', '')
            secs = self.twitch_api.get_uptime_seconds(channel_login=login, user_id=str(self.config.get('target_channel_id', '') or ''))
            if secs <= 0:
                return "offline"
            m, s = divmod(secs, 60)
            h, m = divmod(m, 60)
            if h:
                return f"{h}h {m}m {s}s"
            elif m:
                return f"{m}m {s}s"
            else:
                return f"{s}s"
        except Exception as e:
            self.gui.log_message(f"Erro uptime: {e}", "error")
            return "offline"

    def run(self):
        """Loop principal do bot"""
        self.connect()
        
        buffer = ""
        while self.connected and self.gui.is_running:
            try:
                data = self.sock.recv(1024).decode('utf-8')
                if not data:
                    break
                
                buffer += data
                lines = buffer.split('\r\n')
                buffer = lines.pop()
                
                for line in lines:
                    line = line.strip()
                    if line:
                        if line.startswith('PING'):
                            self.send_raw('PONG :tmi.twitch.tv')
                        else:
                            self.parse_message(line)
                            
            except Exception as e:
                #self.gui.log_message(f"Erro: {e}", "error")
                break
        
        self.disconnect()

    def _update_chatters_list(self):
        """Busca a lista de chatters usando a API Helix (requer token e permissão)."""

        broadcaster_id = self.config['target_channel_id']
        moderator_id = self.config['bot_user_id']
        
        url = f"https://api.twitch.tv/helix/chat/chatters?broadcaster_id={broadcaster_id}&moderator_id={moderator_id}&first=1000"

        headers = {
            'Authorization': f"Bearer {self.config['api_token']}",
            'Client-Id': self.config['client_id']
        }

        try:
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            chatters_list = [chatter['user_login'] for chatter in data.get('data', [])]
            
            chatters_list.append(self.config['bot_user_name'])
            chatters_list.append(self.config['channel'])
            
            self.chatters = list(set(chatters_list))
            self.last_chatter_update = time.time()
 
            return True

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401 or e.response.status_code == 403:
                self.gui.log_message("❌ Erro 401/403: Token sem escopo 'moderator:read:chatters' ou Bot não é mod no canal.", "error")
            elif e.response.status_code == 400:
                 self.gui.log_message("❌ Erro 400: Parâmetros de API incorretos.", "error")
            else:
                 self.gui.log_message(f"❌ Erro HTTP {e.response.status_code} ao buscar chatters.", "error")
            return False

        except Exception as e:
            self.gui.log_message(f"❌ Erro de conexão ao buscar chatters: {e}", "error")
            return False
        
    def _process_cheer_event(self, user, message, bits):
        """Manipula o evento de Cheer (Alerta e/ou TTS)."""
        settings = self.gui.settings
        
        placeholders = {
            'user': user,
            'bits': bits,
            'message': message,
            'channel': self.config['channel']
        }

        if settings.get('msg_cheer_alert_enabled', False):
            msg_template = settings.get('msg_cheer_alert', '{user} cheerou {bits} bits!')
            try:
                chat_message = msg_template.format_map(placeholders)
                self.send_message(chat_message)
            except KeyError as e:
                self.gui.log_message(f"Erro no formato da msg de cheer (alerta): {e}", "error")
            
        if settings.get('tts_cheer_enabled', False):
            min_bits = settings.get('tts_cheer_min_bits', 100)
            
            if bits >= min_bits:
                tts_template = settings.get('tts_cheer_format', '{user} disse: {message}')
                try:
                    tts_message = tts_template.format_map(placeholders)
                    self.gui.request_tts_playback(tts_message)
                except KeyError as e:
                     self.gui.log_message(f"Erro no formato da msg de cheer (TTS): {e}", "error")

        activity_details = f"{bits} bits: {message[:20]}..."
        self.gui.add_activity_entry("cheer.message", user, activity_details)