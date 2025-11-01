# 💬 RyCord - Real-Time Messaging Application

A lightweight, self-hosted messaging platform built with Python that requires no external dependencies. Perfect for local networks, small teams, or learning purposes.

![Python](https://img.shields.io/badge/python-3.6+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

### 💬 Core Messaging
- **Real-time chat** with automatic message polling
- **Multiple channels** support
- **User authentication** with secure password hashing
- **Color-coded usernames** for easy identification
- **Online status indicators**
- **Message deletion** (users can delete their own messages)

### 📎 File Sharing
- **Image sharing** with inline preview
- **Video sharing** with inline player
- **File attachments** with download support
- **100MB file size limit**
- Supports all file types

### 🔐 Admin Panel
- **Channel management** - Create and delete channels
- **User management** - View all registered users
- **Access control** - Restrict users from specific channels
- **Ban system** - Ban/unban users globally
- **Modern UI** with gradient design

### 🎨 User Experience
- **Discord-inspired UI** with dark theme
- **Real-time updates** (1-second polling)
- **Responsive design** for mobile and desktop
- **Auto-scroll** to latest messages
- **Timestamp formatting** (Today, Yesterday, Date)
- **File size formatting** (B, KB, MB)

## 📋 Requirements

- Python 3.6 or higher
- **No external dependencies!** Uses only Python standard library

## 🚀 Quick Start

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/rycord.git
cd rycord
```

2. Run the server:
```bash
python3 server.py
```

3. Open your browser:
- **Chat Interface:** http://localhost:8000
- **Admin Panel:** http://localhost:8000/admin

### Default Credentials

- **Admin Password:** `password` (change this in `server.py`)

## 📁 File Structure

```
rycord/
├── server.py          # Main server application
├── index.html         # Chat interface (HTML + CSS + JS)
├── admin.html         # Admin panel (HTML + CSS + JS)
├── README.md          # This file
└── rycord_data/       # Created automatically
    ├── messages.json
    ├── users.json
    ├── channels.json
    ├── bannedusers.json
    ├── restricted.json
    └── files/         # Uploaded files
```

## 🔧 Configuration

### Change Admin Password

Edit `server.py`:
```python
ADMIN_PASSWORD = "your_secure_password_here"
```

### Change Port

Edit `server.py` (bottom of file):
```python
if __name__ == '__main__':
    run_server(port=8080)  # Change to your desired port
```

### Adjust File Size Limit

Edit `server.py`:
```python
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB (change as needed)
```

## 🎯 Usage

### For Users

1. **Register an account** on the login page
2. **Login** with your credentials
3. **Select a channel** from the sidebar
4. **Send messages** by typing and pressing Enter
5. **Upload files** by clicking the 📎 button
6. **Delete your messages** by hovering and clicking Delete

### For Admins

1. **Access admin panel** at `/admin`
2. **Login** with admin password
3. **Create channels** in the Channels tab
4. **View users** in the Users tab
5. **Restrict access** in the Restrictions tab
6. **Ban users** in the Bans tab

## 🔒 Security Features

- **Password hashing** with SHA-256
- **Session-based authentication**
- **Server-side file validation**
- **XSS protection** with HTML escaping
- **Admin-only routes** with session validation

## 🌐 Network Access

### Local Network Access

To allow access from other devices on your network:

1. Find your local IP:
```bash
# Linux/Mac
ifconfig | grep inet
# Windows
ipconfig
```

2. Run the server and access from other devices using:
```
http://YOUR_LOCAL_IP:8000
```

### Remote Access (Advanced)

For remote access, consider:
- **Port forwarding** on your router
- **Reverse proxy** (nginx, Apache)
- **VPN** for secure access
- **Tunneling** (ngrok, cloudflare tunnel)

## 🐛 Troubleshooting

### Server won't start
- Check if port 8000 is already in use
- Try running with a different port

### Can't upload files
- Check file size (must be under 100MB)
- Ensure `rycord_data/files/` directory exists and is writable

### Messages not updating
- Check browser console for errors
- Ensure JavaScript is enabled
- Try refreshing the page

### Admin panel won't load
- Verify you're using the correct password
- Check browser console for errors

## 🛠️ Development

### Project Structure

- `server.py` - HTTP server with routing and API endpoints
- `index.html` - Main chat interface (HTML + CSS + JS merged)
- `admin.html` - Admin panel interface (HTML + CSS + JS merged)

### API Endpoints

**User Endpoints:**
- `POST /api/signup` - Register new user
- `POST /api/login` - User login
- `POST /api/send` - Send message
- `POST /api/upload` - Upload file
- `POST /api/delete` - Delete message
- `POST /api/heartbeat` - Keep session alive
- `GET /api/channels` - Get channel list
- `GET /api/messages` - Get messages for channel
- `GET /api/users` - Get online users
- `GET /api/file/{id}` - Download file

**Admin Endpoints:**
- `POST /api/admin/login` - Admin login
- `GET /api/admin/data` - Get admin data
- `POST /api/admin/data` - Update admin data

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📧 Contact

- **Issues:** [GitHub Issues](https://github.com/yourusername/rycord/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourusername/rycord/discussions)

## 🙏 Acknowledgments

- Inspired by Discord's design and functionality
- Built with vanilla JavaScript - no frameworks!
- Uses Python's built-in HTTP server

---

**⭐ Star this repository if you find it useful!**
