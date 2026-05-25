from flask import Flask
from .extensions import db, socketio
from config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    socketio.init_app(app, cors_allowed_origins='*', async_mode='eventlet')

    # Register blueprints
    from .blueprints.admin.routes import admin_bp
    from .blueprints.student.routes import student_bp
    from .blueprints.projector.routes import projector_bp
    from .blueprints.api.routes import api_bp

    app.register_blueprint(admin_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(projector_bp)
    app.register_blueprint(api_bp)
    from .blueprints.audience.routes import audience_bp
    app.register_blueprint(audience_bp)

    # Register socket events
    from .sockets import register_all_events
    register_all_events(socketio)

    # Root redirect
    from flask import redirect, url_for
    @app.route('/')
    def index():
        return redirect(url_for('student.join'))  # This should now point to /play/

    # Create tables and seed
    with app.app_context():
        db.create_all()
        _seed_if_empty()

    return app


def _seed_if_empty():
    import os
    from .models import Question
    from .engine.question_loader import load_questions_from_json
    if Question.query.count() == 0:
        path = os.path.join(os.path.dirname(__file__), '..', 'data', 'questions.json')
        load_questions_from_json(path, db, Question)
