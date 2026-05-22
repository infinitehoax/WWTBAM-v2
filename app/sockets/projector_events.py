"""
Projector Socket Events — Big screen listeners (mostly broadcast recipients)
"""
from flask import request
from flask_socketio import emit
from ..engine.game_state import game_state


def register_projector_events(socketio):

    @socketio.on('projector_connect')
    def handle_projector_connect():
        snapshot = game_state.get_snapshot()
        emit('state_snapshot', snapshot)
