from flask import request
from flask_socketio import emit
from ..engine.game_state import game_state
from ..engine.lifelines import submit_audience_vote

def register_audience_events(socketio):
    @socketio.on('audience_join')
    def handle_audience_join():
        sid = request.sid
        game_state.add_audience(sid)

        # Send current poll state and current question
        snapshot = game_state.get_snapshot(sid=sid)
        emit('audience_init', {
            'poll_active': game_state.audience_poll_active,
            'votes': game_state.audience_votes,
            'question': game_state.current_question if game_state.audience_poll_active else None,
            'is_friend': snapshot.get('is_friend', False)
        })

    @socketio.on('audience_vote')
    def handle_audience_vote(data):
        option = data.get('option', '').upper()
        if option in ['A', 'B', 'C', 'D']:
            submit_audience_vote(option, socketio)

    @socketio.on('friend_submit_answer')
    def handle_friend_answer(data):
        sid = request.sid
        if game_state.current_friend_sid == sid:
            option = data.get('option', '').upper()
            if option in ['A', 'B', 'C', 'D']:
                # Notify the student
                socketio.emit('lifeline_phone_answer', {'answer': option})
                # Reset friend state
                game_state.current_friend_sid = None

    @socketio.on('disconnect')
    def handle_disconnect():
        sid = request.sid
        game_state.remove_audience(sid)
