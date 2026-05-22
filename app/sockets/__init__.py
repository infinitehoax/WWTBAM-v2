from .admin_events import register_admin_events
from .student_events import register_student_events
from .projector_events import register_projector_events


def register_all_events(socketio):
    register_admin_events(socketio)
    register_student_events(socketio)
    register_projector_events(socketio)
