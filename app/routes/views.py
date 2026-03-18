from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Redirect to Monitor Center or show Dashboard"""
    return render_template('dashboard.html')

@main_bp.route('/review')
def review():
    return render_template('review.html')

@main_bp.route('/batch_lab')
def batch_lab():
    return render_template('batch_lab.html')

@main_bp.route('/config')
def config_page():
    return render_template('config.html')
