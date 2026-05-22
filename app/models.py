from .extensions import db
from datetime import datetime
import json


class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), default='General')
    difficulty = db.Column(db.Integer, default=1)  # 1-15 like WWTBAM levels
    question_text = db.Column(db.Text, nullable=False)
    question_image = db.Column(db.String(500), nullable=True)  # URL or base64
    use_latex = db.Column(db.Boolean, default=False)
    option_a = db.Column(db.Text, nullable=False)
    option_b = db.Column(db.Text, nullable=False)
    option_c = db.Column(db.Text, nullable=False)
    option_d = db.Column(db.Text, nullable=False)
    option_a_image = db.Column(db.String(500), nullable=True)
    option_b_image = db.Column(db.String(500), nullable=True)
    option_c_image = db.Column(db.String(500), nullable=True)
    option_d_image = db.Column(db.String(500), nullable=True)
    correct_answer = db.Column(db.String(1), nullable=False)  # 'A', 'B', 'C', or 'D'
    time_limit = db.Column(db.Integer, default=30)
    prize_value = db.Column(db.String(50), default='₦0')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self, reveal_answer=False):
        d = {
            'id': self.id,
            'category': self.category,
            'difficulty': self.difficulty,
            'question_text': self.question_text,
            'question_image': self.question_image,
            'use_latex': self.use_latex,
            'options': {
                'A': {'text': self.option_a, 'image': self.option_a_image},
                'B': {'text': self.option_b, 'image': self.option_b_image},
                'C': {'text': self.option_c, 'image': self.option_c_image},
                'D': {'text': self.option_d, 'image': self.option_d_image},
            },
            'time_limit': self.time_limit,
            'prize_value': self.prize_value,
        }
        if reveal_answer:
            d['correct_answer'] = self.correct_answer
        return d


class GameSession(db.Model):
    __tablename__ = 'game_sessions'
    id = db.Column(db.Integer, primary_key=True)
    room_code = db.Column(db.String(10), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    scores = db.relationship('Score', backref='session', lazy=True)


class Score(db.Model):
    __tablename__ = 'scores'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('game_sessions.id'))
    player_name = db.Column(db.String(100), nullable=False)
    sid = db.Column(db.String(100))  # Socket ID
    total_score = db.Column(db.Integer, default=0)
    questions_correct = db.Column(db.Integer, default=0)
    questions_answered = db.Column(db.Integer, default=0)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'player_name': self.player_name,
            'total_score': self.total_score,
            'questions_correct': self.questions_correct,
            'questions_answered': self.questions_answered,
        }
