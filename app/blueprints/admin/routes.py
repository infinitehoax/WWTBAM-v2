from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, current_app
from ...extensions import db
from ...models import Question, GameSession, Score
from ...engine.game_state import game_state
from ...engine.question_loader import load_questions_from_json, get_question_order
import os, random, string

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def require_admin(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('is_admin'):
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        pwd = request.form.get('password', '')
        if pwd == current_app.config.get('ADMIN_PASSWORD', 'admin123'):
            session['is_admin'] = True
            return redirect(url_for('admin.dashboard'))
        error = 'Wrong password, try again.'
    return render_template('admin/login.html', error=error)


@admin_bp.route('/logout')
def logout():
    session.pop('is_admin', None)
    return redirect(url_for('admin.login'))


@admin_bp.route('/')
@admin_bp.route('/dashboard')
@require_admin
def dashboard():
    questions = Question.query.order_by(Question.difficulty).all()
    room_code = game_state.room_code or ''
    return render_template('admin/dashboard.html',
                           questions=questions,
                           room_code=room_code,
                           prize_ladder=game_state.prize_ladder)


@admin_bp.route('/questions', methods=['GET'])
@require_admin
def questions():
    qs = Question.query.order_by(Question.difficulty).all()
    return render_template('admin/questions.html', questions=qs)


@admin_bp.route('/questions/new', methods=['GET', 'POST'])
@require_admin
def new_question():
    if request.method == 'POST':
        q = Question(
            category=request.form.get('category', 'General'),
            difficulty=int(request.form.get('difficulty', 1)),
            question_text=request.form.get('question_text', ''),
            question_image=request.form.get('question_image') or None,
            use_latex=request.form.get('use_latex') == 'on',
            option_a=request.form.get('option_a', ''),
            option_b=request.form.get('option_b', ''),
            option_c=request.form.get('option_c', ''),
            option_d=request.form.get('option_d', ''),
            option_a_image=request.form.get('option_a_image') or None,
            option_b_image=request.form.get('option_b_image') or None,
            option_c_image=request.form.get('option_c_image') or None,
            option_d_image=request.form.get('option_d_image') or None,
            correct_answer=request.form.get('correct_answer', 'A').upper(),
            time_limit=int(request.form.get('time_limit', 30)),
            prize_value=request.form.get('prize_value', '₦1,000'),
        )
        db.session.add(q)
        db.session.commit()
        return redirect(url_for('admin.questions'))
    return render_template('admin/question_form.html', question=None, prize_ladder=game_state.prize_ladder)


@admin_bp.route('/questions/<int:q_id>/edit', methods=['GET', 'POST'])
@require_admin
def edit_question(q_id):
    q = Question.query.get_or_404(q_id)
    if request.method == 'POST':
        q.category = request.form.get('category', q.category)
        q.difficulty = int(request.form.get('difficulty', q.difficulty))
        q.question_text = request.form.get('question_text', q.question_text)
        q.question_image = request.form.get('question_image') or None
        q.use_latex = request.form.get('use_latex') == 'on'
        q.option_a = request.form.get('option_a', q.option_a)
        q.option_b = request.form.get('option_b', q.option_b)
        q.option_c = request.form.get('option_c', q.option_c)
        q.option_d = request.form.get('option_d', q.option_d)
        q.option_a_image = request.form.get('option_a_image') or None
        q.option_b_image = request.form.get('option_b_image') or None
        q.option_c_image = request.form.get('option_c_image') or None
        q.option_d_image = request.form.get('option_d_image') or None
        q.correct_answer = request.form.get('correct_answer', q.correct_answer).upper()
        q.time_limit = int(request.form.get('time_limit', q.time_limit))
        q.prize_value = request.form.get('prize_value', q.prize_value)
        db.session.commit()
        return redirect(url_for('admin.questions'))
    return render_template('admin/question_form.html', question=q, prize_ladder=game_state.prize_ladder)


@admin_bp.route('/questions/<int:q_id>/delete', methods=['POST'])
@require_admin
def delete_question(q_id):
    q = Question.query.get_or_404(q_id)
    db.session.delete(q)
    db.session.commit()
    return redirect(url_for('admin.questions'))


@admin_bp.route('/scores')
@require_admin
def scores():
    lb = game_state.get_leaderboard()
    return render_template('admin/live_scores.html', leaderboard=lb)


@admin_bp.route('/spy')
@require_admin
def spy_view():
    players = [p for p in game_state.players.values() if p.get('active')]
    answers = game_state.answers
    current_q = game_state.current_question
    return render_template('admin/spy_view.html',
                           players=players,
                           answers=answers,
                           current_q=current_q)


@admin_bp.route('/generate-room')
@require_admin
def generate_room():
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    game_state.room_code = code
    return jsonify({'code': code})


@admin_bp.route('/seed-questions')
@require_admin
def seed_questions():
    from ...engine.question_loader import load_questions_from_json
    path = os.path.join(current_app.root_path, '..', 'data', 'questions.json')
    count = load_questions_from_json(path, db, Question)
    return jsonify({'seeded': count})
