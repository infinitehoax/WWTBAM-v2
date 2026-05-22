from flask import Blueprint, render_template

audience_bp = Blueprint('audience', __name__, url_prefix='/audience')

@audience_bp.route('/')
def index():
    return render_template('audience/vote.html')
