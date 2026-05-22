"""
Student Socket Events — Podium interactions
"""
from flask import request
from flask_socketio import emit
from ..engine.game_state import game_state
from ..engine.lifelines import submit_audience_vote


def register_student_events(socketio):

    @socketio.on('student_join')
    def handle_join(data):
        name = data.get('name', 'Anonymous')[:50]
        sid = request.sid

        # Check if the player already exists to get their old sid
        old_sid = None
        for osid, p in list(game_state.players.items()):
            if p['name'] == name:
                old_sid = osid
                break

        game_state.add_player(sid, name)

        if old_sid and old_sid != sid:
            # Broadcast player_left for old_sid first to clean up UI caches
            socketio.emit('player_left', {'sid': old_sid})

        player_data = game_state.players.get(sid, {})
        my_answer = game_state.answers.get(sid)

        # Notify admin of new player
        socketio.emit('player_joined', {
            'sid': sid,
            'name': name,
            'score': player_data.get('score', 0),
            'answer': my_answer.get('answer') if my_answer else None,
            'answer_time': my_answer.get('time') if my_answer else None,
            'total_players': len([p for p in game_state.players.values() if p.get('active')])
        })

        # Send current state to the joining player
        snapshot = game_state.get_snapshot(sid=sid)
        emit('state_snapshot', snapshot)

    @socketio.on('student_answer')
    def handle_answer(data):
        sid = request.sid
        answer = data.get('answer', '').upper()
        if answer not in ['A', 'B', 'C', 'D']:
            return
        if game_state.phase != 'question':
            return

        success = game_state.record_answer(sid, answer)
        if success:
            emit('answer_locked', {'answer': answer})
            # Notify admin privately about the answer (spy view)
            player = game_state.players.get(sid, {})
            socketio.emit('admin_spy_update', {
                'sid': sid,
                'name': player.get('name', '?'),
                'answer': answer,
                'time': game_state.answers[sid]['time']
            })

    @socketio.on('student_audience_vote')
    def handle_audience_vote(data):
        option = data.get('option', '').upper()
        submit_audience_vote(option, socketio)

    @socketio.on('disconnect')
    def handle_disconnect(*args, **kwargs):
        sid = request.sid
        game_state.remove_player(sid)
        socketio.emit('player_left', {'sid': sid})
