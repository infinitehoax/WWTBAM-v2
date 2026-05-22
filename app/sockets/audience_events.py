from flask import request
from flask_socketio import emit
from ..engine.game_state import game_state
from ..engine.lifelines import submit_audience_vote

def register_audience_events(socketio):
    @socketio.on('audience_join')
    def handle_audience_join():
        # Send current poll state and current question
        snapshot = game_state.get_snapshot()
        emit('audience_init', {
            'poll_active': game_state.audience_poll_active,
            'votes': game_state.audience_votes,
            'question': game_state.current_question if game_state.audience_poll_active else None
        })

    @socketio.on('audience_vote')
    def handle_audience_vote(data):
        option = data.get('option', '').upper()
        if option in ['A', 'B', 'C', 'D']:
            submit_audience_vote(option, socketio)
