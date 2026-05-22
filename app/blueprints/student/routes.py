from flask import Blueprint, render_template

student_bp = Blueprint('student', __name__, url_prefix='/play')


@student_bp.route('/')
@student_bp.route('/join')
def join():
    return render_template('student/join.html')


@student_bp.route('/waiting')
def waiting():
    return render_template('student/waiting.html')


@student_bp.route('/podium')
def podium():
    return render_template('student/podium.html')
