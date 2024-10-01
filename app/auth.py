from flask import Blueprint, flash, redirect, url_for, session, request, render_template
from stream import get_frames


auth_routes = Blueprint('auth', __name__)
@auth_routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # Handle authentication with Firebase or other service
        return redirect(url_for('main.dashboard'))
    return render_template('login.html')