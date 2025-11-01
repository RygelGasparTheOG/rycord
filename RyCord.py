#!/usr/bin/env python3
"""
RyCord - Messaging App Server
Features: Authentication, File/Image/Video sharing, Message deletion, Persistent storage, Admin controls
"""

import json
import uuid
import base64
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime
from threading import Lock
import hashlib
import random

# ADMIN PASSWORD - Change this to your desired admin password
ADMIN_PASSWORD = "password"

# File size limit (100MB)
MAX_FILE_SIZE = 100 * 1024 * 1024

# Data store
DATA_DIR = "rycord_data"
MESSAGES_FILE = os.path.join(DATA_DIR, "messages.json")
USERS_FILE = os.path.join(DATA_DIR, "users.json")
CHANNELS_FILE = os.path.join(DATA_DIR, "channels.json")
BANNED_USERS_FILE = os.path.join(DATA_DIR, "bannedusers.json")
RESTRICTED_FILE = os.path.join(DATA_DIR, "restricted.json")
FILES_DIR = os.path.join(DATA_DIR, "files")

# Create data directories
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(FILES_DIR, exist_ok=True)

channels = {}
registered_users = {}
active_sessions = {}
banned_users = []
restricted_channels = {}
admin_sessions = {}
data_lock = Lock()

def load_data():
    """Load all data from disk"""
    global channels, registered_users, banned_users, restricted_channels
    
    if os.path.exists(CHANNELS_FILE):
        try:
            with open(CHANNELS_FILE, 'r') as f:
                channel_names = json.load(f)
                for ch in channel_names:
                    if ch not in channels:
                        channels[ch] = {"name": ch, "messages": []}
        except Exception as e:
            print(f"Error loading channels: {e}")
    
    if not channels:
        channels = {
            "general": {"name": "general", "messages": []},
            "random": {"name": "random", "messages": []}
        }
        save_channels()
    
    if os.path.exists(MESSAGES_FILE):
        try:
            with open(MESSAGES_FILE, 'r') as f:
                loaded_channels = json.load(f)
                for channel_name, channel_data in loaded_channels.items():
                    if channel_name in channels:
                        channels[channel_name]["messages"] = channel_data.get("messages", [])
        except Exception as e:
            print(f"Error loading messages: {e}")
    
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r') as f:
                registered_users.update(json.load(f))
        except Exception as e:
            print(f"Error loading users: {e}")
    
    if os.path.exists(BANNED_USERS_FILE):
        try:
            with open(BANNED_USERS_FILE, 'r') as f:
                banned_users.extend(json.load(f))
        except Exception as e:
            print(f"Error loading banned users: {e}")
    
    if os.path.exists(RESTRICTED_FILE):
        try:
            with open(RESTRICTED_FILE, 'r') as f:
                restricted_channels.update(json.load(f))
        except Exception as e:
            print(f"Error loading restricted channels: {e}")

def save_channels():
    with open(CHANNELS_FILE, 'w') as f:
        json.dump(list(channels.keys()), f, indent=2)

def save_messages():
    with open(MESSAGES_FILE, 'w') as f:
        json.dump(channels, f, indent=2)

def save_users():
    with open(USERS_FILE, 'w') as f:
        json.dump(registered_users, f, indent=2)

def save_banned_users():
    with open(BANNED_USERS_FILE, 'w') as f:
        json.dump(banned_users, f, indent=2)

def save_restricted():
    with open(RESTRICTED_FILE, 'w') as f:
        json.dump(restricted_channels, f, indent=2)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_random_color():
    colors = ['#ed4245', '#f57c00', '#ffa500', '#43b581', '#00acc1', '#5865f2', '#9c27b0', '#e91e63']
    return random.choice(colors)

class ChatHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        
        if parsed.path == '/':
            self.serve_file('index.html', 'text/html')
        elif parsed.path == '/admin':
            self.serve_file('admin.html', 'text/html')
        elif parsed.path == '/styles.css':
            self.serve_file('styles.css', 'text/css')
        elif parsed.path == '/admin-styles.css':
            self.serve_file('admin-styles.css', 'text/css')
        elif parsed.path == '/app.js':
            self.serve_file('app.js', 'application/javascript')
        elif parsed.path == '/admin.js':
            self.serve_file('admin.js', 'application/javascript')
        elif parsed.path == '/api/channels':
            self.get_channels()
        elif parsed.path.startswith('/api/messages'):
            self.get_messages(parsed)
        elif parsed.path == '/api/users':
            self.get_users()
        elif parsed.path.startswith('/api/file/'):
            self.get_file(parsed.path)
        elif parsed.path.startswith('/api/admin/data'):
            self.get_admin_data(parsed)
        else:
            self.send_error(404)
    
    def serve_file(self, filename, content_type):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.end_headers()
            self.wfile.write(content.encode())
        except FileNotFoundError:
            self.send_error(404)
    
    def do_POST(self):
        parsed = urlparse(self.path)
        
        if parsed.path == '/api/signup':
            self.signup()
        elif parsed.path == '/api/login':
            self.login()
        elif parsed.path == '/api/send':
            self.send_message()
        elif parsed.path == '/api/upload':
            self.upload_file()
        elif parsed.path == '/api/delete':
            self.delete_message()
        elif parsed.path == '/api/heartbeat':
            self.heartbeat()
        elif parsed.path == '/api/admin/login':
            self.admin_login()
        elif parsed.path == '/api/admin/data':
            self.save_admin_data_api()
        else:
            self.send_error(404)
    
    def signup(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode())
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        with data_lock:
            if username in registered_users:
                self.send_json({"status": "error", "message": "Username already exists"})
                return
            
            if username in banned_users:
                self.send_json({"status": "error", "message": "You are banned from RyCord"})
                return
            
            registered_users[username] = {
                "password_hash": hash_password(password),
                "color": get_random_color()
            }
            save_users()
        
        self.send_json({"status": "ok"})
    
    def login(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode())
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        with data_lock:
            if username in banned_users:
                self.send_json({"status": "error", "message": "You are banned from RyCord"})
                return
            
            if username not in registered_users:
                self.send_json({"status": "error", "message": "Invalid username or password"})
                return
            
            user = registered_users[username]
            if user["password_hash"] != hash_password(password):
                self.send_json({"status": "error", "message": "Invalid username or password"})
                return
            
            session_id = str(uuid.uuid4())
            active_sessions[session_id] = {
                "username": username,
                "last_seen": datetime.now().timestamp(),
                "color": user["color"]
            }
        
        self.send_json({
            "status": "ok",
            "sessionId": session_id,
            "color": user["color"]
        })
    
    def admin_login(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode())
        
        password = data.get('password', '')
        
        if password == ADMIN_PASSWORD:
            session_id = str(uuid.uuid4())
            admin_sessions[session_id] = datetime.now().timestamp()
            self.send_json({"status": "ok", "sessionId": session_id})
        else:
            self.send_json({"status": "error", "message": "Invalid password"})
    
    def get_admin_data(self, parsed):
        params = parse_qs(parsed.query)
        session = params.get('session', [''])[0]
        
        if session not in admin_sessions:
            self.send_json({"status": "error", "message": "Unauthorized"})
            return
        
        with data_lock:
            data = {
                "channels": list(channels.keys()),
                "users": list(registered_users.keys()),
                "banned_users": banned_users,
                "restricted_channels": restricted_channels
            }
        
        self.send_json(data)
    
    def save_admin_data_api(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode())
        
        session = data.get('sessionId', '')
        if session not in admin_sessions:
            self.send_json({"status": "error", "message": "Unauthorized"})
            return
        
        with data_lock:
            global channels, banned_users, restricted_channels
            
            new_channels = data.get('channels', [])
            for ch in new_channels:
                if ch not in channels:
                    channels[ch] = {"name": ch, "messages": []}
            
            for ch in list(channels.keys()):
                if ch not in new_channels:
                    del channels[ch]
            
            banned_users = data.get('banned_users', [])
            restricted_channels = data.get('restricted_channels', {})
            
            save_channels()
            save_messages()
            save_banned_users()
            save_restricted()
        
        self.send_json({"status": "ok"})
    
    def get_channels(self):
        with data_lock:
            data = {"channels": list(channels.keys())}
        self.send_json(data)
    
    def get_messages(self, parsed):
        params = parse_qs(parsed.query)
        channel = params.get('channel', ['general'])[0]
        
        with data_lock:
            if channel in channels:
                data = {"messages": channels[channel]["messages"]}
            else:
                data = {"messages": []}
        
        self.send_json(data)
    
    def get_users(self):
        with data_lock:
            now = datetime.now().timestamp()
            active_users = [
                {"username": s["username"], "color": s["color"]}
                for s in active_sessions.values()
                if now - s["last_seen"] < 10
            ]
        
        self.send_json({"users": active_users})
    
    def send_message(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode())
        
        session_id = data.get("sessionId")
        username = data.get("username")
        channel = data.get("channel", "general")
        
        if not session_id or session_id not in active_sessions:
            self.send_json({"status": "error", "message": "Invalid session"})
            return
        
        if username in banned_users:
            self.send_json({"status": "error", "message": "You are banned"})
            return
        
        if channel in restricted_channels and username in restricted_channels[channel]:
            self.send_json({"status": "error", "message": "You cannot access this channel"})
            return
        
        message = {
            "id": data.get("id"),
            "username": username,
            "text": data.get("text", ""),
            "timestamp": datetime.now().isoformat(),
            "color": data.get("color", "#5865f2"),
            "type": data.get("type", "text")
        }
        
        with data_lock:
            if channel in channels:
                channels[channel]["messages"].append(message)
                save_messages()
        
        self.send_json({"status": "ok"})
    
    def upload_file(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode())
        
        session_id = data.get("sessionId")
        username = data.get("username")
        channel = data.get("channel", "general")
        
        if not session_id or session_id not in active_sessions:
            self.send_json({"status": "error", "message": "Invalid session"})
            return
        
        if username in banned_users:
            self.send_json({"status": "error", "message": "You are banned"})
            return
        
        if channel in restricted_channels and username in restricted_channels[channel]:
            self.send_json({"status": "error", "message": "You cannot access this channel"})
            return
        
        file_data = data.get("fileData")
        
        try:
            decoded_data = base64.b64decode(file_data)
            if len(decoded_data) > MAX_FILE_SIZE:
                self.send_json({"status": "error", "message": "File too large. Maximum size is 100MB."})
                return
        except Exception as e:
            self.send_json({"status": "error", "message": "Invalid file data"})
            return
        
        file_id = data.get("id")
        mime_type = data.get("mimeType")
        
        file_path = os.path.join(FILES_DIR, file_id)
        try:
            with open(file_path, 'wb') as f:
                f.write(decoded_data)
        except Exception as e:
            self.send_json({"status": "error", "message": "Failed to save file"})
            return
        
        metadata_path = file_path + ".meta"
        with open(metadata_path, 'w') as f:
            json.dump({"mimeType": mime_type, "fileName": data.get("fileName")}, f)
        
        message = {
            "id": file_id,
            "username": username,
            "text": "",
            "timestamp": datetime.now().isoformat(),
            "color": data.get("color", "#5865f2"),
            "type": data.get("type", "file"),
            "fileId": file_id,
            "fileName": data.get("fileName"),
            "fileSize": data.get("fileSize", 0)
        }
        
        with data_lock:
            if channel in channels:
                channels[channel]["messages"].append(message)
                save_messages()
        
        self.send_json({"status": "ok"})
    
    def get_file(self, path):
        file_id = path.split('/')[-1]
        file_path = os.path.join(FILES_DIR, file_id)
        metadata_path = file_path + ".meta"
        
        if not os.path.exists(file_path):
            self.send_error(404)
            return
        
        mime_type = "application/octet-stream"
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                    mime_type = metadata.get("mimeType", mime_type)
            except:
                pass
        
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
        except:
            self.send_error(500)
            return
        
        self.send_response(200)
        self.send_header('Content-type', mime_type)
        self.send_header('Content-Length', len(content))
        self.end_headers()
        self.wfile.write(content)
    
    def delete_message(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode())
        
        session_id = data.get("sessionId")
        if not session_id or session_id not in active_sessions:
            self.send_json({"status": "error", "message": "Invalid session"})
            return
        
        message_id = data.get("messageId")
        channel = data.get("channel")
        username = data.get("username")
        
        with data_lock:
            if channel in channels:
                messages = channels[channel]["messages"]
                for i, msg in enumerate(messages):
                    if msg.get("id") == message_id:
                        if msg.get("username") == username:
                            if msg.get("fileId"):
                                file_path = os.path.join(FILES_DIR, msg["fileId"])
                                if os.path.exists(file_path):
                                    try:
                                        os.remove(file_path)
                                    except:
                                        pass
                                metadata_path = file_path + ".meta"
                                if os.path.exists(metadata_path):
                                    try:
                                        os.remove(metadata_path)
                                    except:
                                        pass
                            
                            messages.pop(i)
                            save_messages()
                            self.send_json({"status": "ok"})
                            return
                        else:
                            self.send_json({"status": "error", "message": "Not authorized"})
                            return
        
        self.send_json({"status": "error", "message": "Message not found"})
    
    def heartbeat(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode())
        
        session_id = data.get("sessionId")
        
        with data_lock:
            if session_id in active_sessions:
                active_sessions[session_id]["last_seen"] = datetime.now().timestamp()
            else:
                username = data.get("username")
                if username in registered_users:
                    active_sessions[session_id] = {
                        "username": username,
                        "last_seen": datetime.now().timestamp(),
                        "color": data.get("color", registered_users[username]["color"])
                    }
        
        self.send_json({"status": "ok"})
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def log_message(self, format, *args):
        pass

def run_server(port=8000):
    load_data()
    
    server = HTTPServer(('', port), ChatHandler)
    print(f"RyCord server running at http://localhost:{port}")
    print(f"Admin panel at http://localhost:{port}/admin")
    print(f"Admin password: {ADMIN_PASSWORD}")
    print(f"Data files:")
    print(f"   - Channels: {CHANNELS_FILE}")
    print(f"   - Banned users: {BANNED_USERS_FILE}")
    print(f"   - Messages: {MESSAGES_FILE}")
    print(f"   - Users: {USERS_FILE}")
    print(f"\nPress Ctrl+C to stop the server")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\nSaving data...")
        save_messages()
        save_users()
        save_channels()
        save_banned_users()
        save_restricted()
        print("Server stopped. Thanks for using RyCord!")
        server.shutdown()

if __name__ == '__main__':
    run_server()
