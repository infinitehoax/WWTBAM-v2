from flask import Blueprint, jsonify
from ...models import Question
from ...engine.game_state import game_state

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/questions')
def get_questions():
    qs = Question.query.order_by(Question.difficulty).all()
    return jsonify([q.to_dict() for q in qs])


@api_bp.route('/state')
def get_state():
    return jsonify(game_state.get_snapshot())


@api_bp.route('/leaderboard')
def get_leaderboard():
    return jsonify(game_state.get_leaderboard())
