import eventlet
eventlet.monkey_patch()

from app import create_app
from app.extensions import socketio

app = create_app()

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5003))
    print("[App] WWTBAM School Game starting...")
    print(f"[Screen] Projector screen: http://localhost:{port}/screen")
    print(f"[Play]   Student join:     http://localhost:{port}/play")
    print(f"[Admin]  Admin panel:      http://localhost:{port}/admin")
    socketio.run(app, host='0.0.0.0', port=port, debug=True)
