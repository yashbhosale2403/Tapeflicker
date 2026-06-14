# Tapeflicker | Next-gen Learning Ecosystem

Tapeflicker is a premium, high-performance web platform designed to deliver advanced technology and cybersecurity education. Featuring interactive lessons, a gamified learning rank system, real-time group chat rooms, and a comprehensive management dashboard, Tapeflicker equips students with real-world technical skills in a sleek, modern interface.

---

## 🚀 Key Features

*   **Premium Interactive Homepage**: Ambient grid animations, Canvas-based knowledge graph nodes, and interactive SVG learning pathway elements (*Learn → Practice → Build → Certify → Grow*).
*   **Gamified User Profiles**: Interactive student dashboard featuring XP tracking, rank milestones (e.g., Novice, Elite Scout), active day streaks, and badge showcase.
*   **Hybrid Authentication**: Secured integration combining client-side **Firebase Authentication** (Google Sign-In, Password resets) and Django session tracking.
*   **Advanced Lesson Player**: Integrated YouTube video player tracking, progress save states, downloadable lesson resources, and responsive sidebars.
*   **Real-time Chat Channels**: WebSocket-enabled group discussions per course featuring user tagging, message pins, announcements, message reactions, attachments, and mod-controlled bans/mutes.
*   **Central Administration HQ**: Complete course management, event scheduling, user blocking, support tickets processing, and moderator logs auditing.

---

## 🛠️ Technology Stack

*   **Backend**: Python, Django 6.0, Django Channels (WebSockets)
*   **Frontend**: Vanilla HTML5, CSS3, JavaScript (ES6 modules), HTML5 Canvas
*   **Database**: SQLite (Development) / PostgreSQL (Production ready)
*   **Authentication & Security**: Firebase Client SDK, Firebase Admin Python SDK, custom CSP & Rate-limiting Middleware

---

## 💻 Installation & Local Setup

### Prerequisites
*   Python 3.10 or higher
*   Git

### 1. Clone the Repository
```bash
git clone https://github.com/yashbhosale2403/Tapeflicker.git
cd Tapeflicker
```

### 2. Create and Activate Virtual Environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory:
```env
DJANGO_DEBUG=True
DJANGO_SECRET_KEY=your-development-insecure-key
ALLOWED_HOSTS=127.0.0.1,localhost
# FIREBASE_SERVICE_ACCOUNT_JSON= (Optional in dev, falls back to root service JSON file)
```

### 5. Run Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser (Admin Account)
```bash
python manage.py createsuperuser
```

### 7. Run Local Development Server
```bash
python manage.py runserver
```
Visit the application at `http://127.0.0.1:8000/`.

---

## 🔒 Production Environment Variables

Ensure the following variables are configured on your hosting provider (e.g., Render) in production:

| Variable | Description | Recommended Value |
| :--- | :--- | :--- |
| `DJANGO_DEBUG` | Disables debug mode for detailed error hiding | `False` |
| `DJANGO_SECRET_KEY` | Cryptographically secure random key | `[Secure Random String]` |
| `ALLOWED_HOSTS` | Comma-separated list of permitted domains | `yourdomain.com,tapeflicker.render.com` |
| `FIREBASE_SERVICE_ACCOUNT_JSON` | Firebase SDK credentials certificate details | `{"type": "service_account", ...}` |
| `SECURE_SSL_REDIRECT` | Enforces HTTPS redirection | `True` |

---

## 🌐 Production Deployment (Render)

This project contains a pre-configured `render.yaml` blueprint:
1. Connect your GitHub repository to Render.
2. Click **New** -> **Blueprint Route** on the Render dashboard.
3. Select this repository and follow the configuration wizard. Render will deploy the web service and start the Daphne ASGI server automatically.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for details.
