# 🎮 Who Wants To Be A Millionaire — Crystal Brooks College Edition

A full real-time multiplayer WWTBAM clone built with **Flask + Socket.IO**.  
Supports LaTeX math, rich formatting, images on questions and options, lifelines, audio, and a live spy view.

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. (Optional) Configure
Edit `.env` to change the admin password:
```
ADMIN_PASSWORD=your_secret_password
```

### 3. Run
```bash
python run.py
```

---

## 🌐 URLs

| URL | Who uses it |
|-----|-------------|
| `http://localhost:5000/play` | **Students** — join screen (open on each device/phone) |
| `http://localhost:5000/screen` | **Projector** — the big audience display |
| `http://localhost:5000/admin` | **Host/Admin** — full control room |

---

## 🎮 How to Run a Game Night

1. Open `/screen` on the projector/big screen
2. Open `/admin` on your laptop (password: `admin123` by default)
3. Students open `/play` on their phones and enter their name
4. In Admin, click **Generate Code** and announce the URL
5. When everyone's joined, click **▶ Push** next to Question 1
6. Watch answers come in live on the Admin spy view
7. Hit **Reveal Answer** when ready — scores update automatically
8. Use **Sound buttons** to add atmosphere
9. Use **Lifelines** (50:50, Audience, Phone) when needed
10. Hit **Leaderboard** to show final scores with confetti 🎉

---

## ✏️ Adding Questions

### Via Admin Panel
Go to `/admin/questions/new`

**LaTeX support:** Use `$...$` for inline math and `$$...$$` for display math.  
Example: `What is $\int_0^1 x^2\,dx$?`

**Images:** Paste any image URL into the image field for questions or individual options.

### Via JSON (bulk import)
Edit `data/questions.json` and visit `/admin/seed-questions` to load them.

JSON format:
```json
{
  "category": "Mathematics",
  "difficulty": 5,
  "question_text": "What is $e^{i\\pi} + 1$?",
  "use_latex": true,
  "question_image": "https://example.com/formula.png",
  "options": { "A": "$0$", "B": "$1$", "C": "$-1$", "D": "$2i$" },
  "option_images": { "A": null, "B": null, "C": null, "D": null },
  "correct_answer": "A",
  "time_limit": 40,
  "prize_value": "₦50,000"
}
```

---

## 🎵 Audio

Replace the placeholder files in `app/static/audio/` with real MP3s:

| File | When it plays |
|------|---------------|
| `theme.mp3` | Background lobby music |
| `suspense.mp3` | During a question countdown |
| `correct.mp3` | Correct answer reveal |
| `wrong.mp3` | Wrong answer |
| `lockin.mp3` | Student locks in answer |
| `million.mp3` | Final leaderboard / winner |

Free WWTBAM-style sounds can be found on freesound.org or similar.

---

## 🏗️ Architecture

```
Admin Dashboard  ──► socket.emit('admin_push_question')
                           │
                    Flask-SocketIO Server
                    app/engine/game_state.py  (in-memory brain)
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
   Student Podiums   Projector Screen   Admin Spy View
   (answer buttons)  (big display)      (live answers)
```

- **Game State** is held in memory — if a student's phone refreshes, they reconnect and receive the current state instantly
- **No database needed** for gameplay — SQLite only stores the question bank
- **LaTeX** is rendered via MathJax 3 (CDN, no install needed)

---

## 🔧 Tech Stack

- **Backend:** Python, Flask, Flask-SocketIO, eventlet, SQLAlchemy
- **Frontend:** Vanilla JS + Socket.IO client
- **Fonts:** Cinzel Decorative (display), Exo 2 (body) via Google Fonts
- **Math:** MathJax 3
- **DB:** SQLite (via SQLAlchemy)
