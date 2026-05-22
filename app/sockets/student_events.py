"""
Student Socket Events — Podium interactions
"""
from flask import request
from flask_socketio import emit
from ..engine.game_state import game_state
from ..engine.lifelines import use_5050, use_audience_poll, submit_audience_vote, use_phone_a_friend


def register_student_events(socketio):

    @socketio.on('student_join')
    def handle_join(data):
        name = data.get('name', 'Anonymous')[:50]
        room_code = data.get('room_code', '').upper()
        token = data.get('token')
        sid = request.sid

        # Validate room code if one is set on server
        if game_state.room_code and room_code != game_state.room_code:
            emit('join_error', {'msg': 'Invalid Room Code'})
            return

        # Check if the player already exists to get their old sid (now using token if available)
        old_sid = None
        if token:
            for osid, p in list(game_state.players.items()):
                if p.get('token') == token:
                    old_sid = osid
                    break
        else:
            # Fallback to name-based join only if no token and player is inactive
            for osid, p in list(game_state.players.items()):
                if p['name'] == name and not p.get('active'):
                    old_sid = osid
                    break

        new_token = game_state.add_player(sid, name, token=token)

        if old_sid and old_sid != sid:
            # Broadcast player_left for old_sid first to clean up UI caches
            socketio.emit('player_left', {'sid': old_sid})

        player_data = game_state.players.get(sid, {})
        my_answer = game_state.answers.get(sid)

        # Emit the token back to the student so they can save it
        emit('join_success', {'token': new_token})

        # Notify admin of new player
        socketio.emit('player_joined', {
            'sid': sid,
            'name': name,
            'score': player_data.get('score', 0),
            'score_formatted': game_state.format_naira(player_data.get('score', 0)),
            'answer': my_answer.get('answer') if my_answer else None,
            'answer_time': my_answer.get('time') if my_answer else None,
            'is_eliminated': player_data.get('is_eliminated', False),
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

    @socketio.on('student_use_lifeline')
    def handle_use_lifeline(data):
        sid = request.sid
        ll_type = data.get('lifeline')

        if sid not in game_state.players or game_state.players[sid].get('is_eliminated'):
            return

        if ll_type in game_state.lifelines_used.get(sid, []):
            emit('admin_error', {'msg': 'Lifeline already used!'})
            return

        if ll_type == '5050':
            eliminated = use_5050(sid, socketio)
            if eliminated:
                game_state.lifelines_used[sid].append('5050')
                emit('lifeline_5050', {'eliminated': eliminated})

        elif ll_type == 'audience':
            # Ask the Audience triggers the poll for everyone
            use_audience_poll(socketio)
            game_state.lifelines_used[sid].append('audience')
            # The actual voting UI is handled via the audience_poll_started event broadcast

        elif ll_type == 'phone':
            # Phone a Friend picks a random audience member
            success = use_phone_a_friend(sid, socketio)
            if success:
                game_state.lifelines_used[sid].append('phone')
                emit('lifeline_used', {'lifeline': 'phone'})

    @socketio.on('disconnect')
    def handle_disconnect(*args, **kwargs):
        sid = request.sid
        game_state.remove_player(sid)
        socketio.emit('player_left', {'sid': sid})
