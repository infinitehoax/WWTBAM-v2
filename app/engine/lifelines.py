"""
Lifeline Logic
"""
from .game_state import game_state


def use_5050(sid, socketio):
    """Activate 50:50 for a specific player."""
    q = game_state.current_question
    if not q:
        return False
    correct = q.get('correct_answer')
    eliminated = game_state.apply_5050(correct)
    return eliminated


def use_audience_poll(socketio):
    """Start an audience vote on the big screen."""
    game_state.start_audience_poll()
    socketio.emit('audience_poll_started', {'question': game_state.current_question})


def submit_audience_vote(option, socketio):
    """Record an audience vote and broadcast updated results."""
    game_state.vote_audience(option)
    socketio.emit('audience_votes_update', {
        'votes': game_state.audience_votes
    })


def use_phone_a_friend(sid, socketio):
    """Pick a random audience member and ask them for help."""
    friend_sid = game_state.pick_random_friend()
    if friend_sid:
        # Notify the friend
        socketio.emit('you_are_the_friend', {
            'question': game_state.current_question,
            'student_name': game_state.players.get(sid, {}).get('name', 'The contestant')
        }, room=friend_sid)

        # Notify the student
        socketio.emit('friend_called', {'success': True}, room=sid)
        return True
    else:
        # No audience members available
        socketio.emit('friend_called', {
            'success': False,
            'msg': "No audience members available to call!"
        }, room=sid)
        return False


def get_phone_hint(socketio):
    """Give a hint (admin writes it manually in dashboard and it's emitted)."""
    pass  # Handled manually via admin dashboard emit
