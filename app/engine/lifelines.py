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
    socketio.emit('lifeline_5050', {
        'eliminated': eliminated,
        'for_sid': sid
    }, broadcast=True)
    return eliminated


def use_audience_poll(socketio):
    """Start an audience vote on the big screen."""
    game_state.start_audience_poll()
    socketio.emit('audience_poll_started', {}, broadcast=True)


def submit_audience_vote(option, socketio):
    """Record an audience vote and broadcast updated results."""
    game_state.vote_audience(option)
    socketio.emit('audience_votes_update', {
        'votes': game_state.audience_votes
    }, broadcast=True)


def get_phone_hint(socketio):
    """Give a hint (admin writes it manually in dashboard and it's emitted)."""
    pass  # Handled manually via admin dashboard emit
