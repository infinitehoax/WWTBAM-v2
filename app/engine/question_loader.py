"""
Question Loader — Loads questions from DB or seeds from JSON
"""
import json
import os


def load_questions_from_list(questions_list, db, Question):
    """Seed questions into DB from a list of question dictionaries."""
    count = 0
    for q in questions_list:
        existing = Question.query.filter_by(question_text=q['question_text']).first()
        if not existing:
            obj = Question(
                category=q.get('category', 'General'),
                difficulty=q.get('difficulty', 1),
                question_text=q['question_text'],
                question_image=q.get('question_image'),
                use_latex=q.get('use_latex', False),
                option_a=q['options']['A'],
                option_b=q['options']['B'],
                option_c=q['options']['C'],
                option_d=q['options']['D'],
                option_a_image=q.get('option_images', {}).get('A') if q.get('option_images') else None,
                option_b_image=q.get('option_images', {}).get('B') if q.get('option_images') else None,
                option_c_image=q.get('option_images', {}).get('C') if q.get('option_images') else None,
                option_d_image=q.get('option_images', {}).get('D') if q.get('option_images') else None,
                correct_answer=q['correct_answer'],
                time_limit=q.get('time_limit', 30),
                prize_value=q.get('prize_value', '₦1,000'),
            )
            db.session.add(obj)
            count += 1
    db.session.commit()
    return count


def load_questions_from_json(filepath, db, Question):
    """Seed questions into DB from a JSON file."""
    if not os.path.exists(filepath):
        return 0
    with open(filepath, 'r', encoding='utf-8') as f:
        questions = json.load(f)
    return load_questions_from_list(questions, db, Question)


def get_question_order(db, Question, count=None):
    """Returns list of question IDs ordered by difficulty."""
    qs = Question.query.order_by(Question.difficulty.asc()).all()
    if count:
        qs = qs[:count]
    return [q.id for q in qs]
