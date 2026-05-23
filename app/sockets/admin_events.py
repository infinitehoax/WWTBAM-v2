"""
Admin Socket Events — Full control room
"""
from flask import request
from flask_socketio import emit
from ..engine.game_state import game_state
from ..engine.lifelines import use_5050, use_audience_poll, submit_audience_vote


def register_admin_events(socketio):

    @socketio.on('admin_push_question')
    def handle_push_question(data):
        """Admin pushes a question to all clients."""
        from ..models import Question
        from .. import db

        q_id = data.get('question_id')
        q_index = data.get('index', 0)

        q = Question.query.get(q_id)
        if not q:
            emit('admin_error', {'msg': f'Question {q_id} not found'})
            return

        q_dict = q.to_dict(reveal_answer=True)
        game_state.set_question(q_dict, q_index)

        # Send to students WITHOUT correct answer
        student_dict = q.to_dict(reveal_answer=False)
        student_dict['time_limit'] = q.time_limit

        # Format prize from integer ladder
        prize_int = game_state.prize_ladder[q_index] if q_index < len(game_state.prize_ladder) else 0
        student_dict['prize'] = game_state.format_naira(prize_int)

        student_dict['q_index'] = q_index
        student_dict['eliminated_options'] = []
        student_dict['timer_started'] = False

        socketio.emit('new_question', student_dict)

    @socketio.on('admin_start_timer')
    def handle_start_timer():
        """Admin starts the countdown."""
        success = game_state.start_timer()
        if success:
            socketio.emit('timer_started', {
                'time_limit': game_state.time_limit
            })

    @socketio.on('admin_reveal_answer')
    def handle_reveal_answer(data):
        """Admin triggers answer reveal."""
        q = game_state.current_question
        if not q:
            return
        correct = q.get('correct_answer')
        game_state.reveal_answer(correct)
        stats = game_state.get_answer_stats()

        # Leaderboard with formatted scores
        lb = game_state.get_leaderboard()

        socketio.emit('answer_revealed', {
            'correct_answer': correct,
            'answer_stats': stats,
            'leaderboard': lb,
        })

    @socketio.on('admin_show_leaderboard')
    def handle_show_leaderboard():
        lb = game_state.get_leaderboard()
        socketio.emit('show_leaderboard', {'leaderboard': lb})

    @socketio.on('admin_play_sound')
    def handle_play_sound(data):
        """Trigger a sound on the projector."""
        sound = data.get('sound')
        loop = data.get('loop', False)
        socketio.emit('play_sound', {'sound': sound, 'loop': loop})

    @socketio.on('admin_use_5050')
    def handle_5050(data):
        sid = data.get('sid', '')
        use_5050(sid, socketio)

    @socketio.on('admin_audience_poll')
    def handle_audience_poll():
        use_audience_poll(socketio)

    @socketio.on('admin_phone_hint')
    def handle_phone_hint(data):
        hint = data.get('hint', '')
        socketio.emit('phone_hint', {'hint': hint})

    @socketio.on('admin_reset_game')
    def handle_reset():
        game_state.reset()
        socketio.emit('game_reset', {})

    @socketio.on('admin_set_phase')
    def handle_phase(data):
        phase = data.get('phase', 'lobby')
        game_state.phase = phase
        socketio.emit('phase_change', {'phase': phase})

    @socketio.on('admin_get_state')
    def handle_get_state():
        emit('state_snapshot', game_state.get_snapshot())

    @socketio.on('admin_kick_player')
    def handle_kick(data):
        sid = data.get('sid')
        game_state.remove_player(sid)
        socketio.emit('player_kicked', {'sid': sid})

    @socketio.on('admin_kick_all_players')
    def handle_kick_all():
        game_state.kick_all_players()
        socketio.emit('all_players_kicked', {})
