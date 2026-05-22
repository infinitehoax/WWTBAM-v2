from app import create_app
from app.extensions import db
from app.models import Question
app = create_app()
with app.app_context():
    print(f"Questions: {Question.query.count()}")
