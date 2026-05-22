from flask import Blueprint, render_template
from ...engine.game_state import game_state

projector_bp = Blueprint('projector', __name__, url_prefix='/screen')


@projector_bp.route('/')
def main_screen():
    return render_template('projector/main_screen.html',
                           prize_ladder=game_state.prize_ladder,
                           safe_havens=game_state.safe_havens)


@projector_bp.route('/leaderboard')
def leaderboard():
    lb = game_state.get_leaderboard()
    return render_template('projector/leaderboard.html', leaderboard=lb)
