from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import re
import random
from queries import *
from config import *


from functools import wraps


auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/registration/', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        # Limit username to 50 characters
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        email = request.form['email']
        # Limit display name to 50 characters
        display_name = request.form['display_name']
        # Limit about me to 130 characters
        about_me = request.form['about_me']
        role = 'Regular User'
        AVATAR_FILES = ['avatar1.jpg', 'avatar2.png',
                        'avatar3.jpeg', 'avatar4.jpg']
        selected_avatar = random.choice(AVATAR_FILES)
        Gravatar_url = selected_avatar
        session['registration_form_data'] = request.form
        # Check if all fields are provided
        if not username or not password or not confirm_password or not email or not display_name or not Gravatar_url or not about_me:

            flash('Please fill the required fields', 'error')

        elif password != confirm_password:

            flash('Passwords do not match.', 'error')

        else:
            # Check if the username or email already exists
            with db.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM Users WHERE username = %s OR email = %s", (username, email))
                existing_user = cursor.fetchone()

                if existing_user:

                    flash(
                        'Username or email already exists. Please choose a different one.', 'error')

                else:
                    if not re.match(r"^[a-zA-Z0-9_]*$", username):
                        flash('Username should be alphanumeric ', 'error')
                    # Validate email format
                    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):

                        flash('Invalid email address.', 'error')
                    # if not re.match(r"^https:\/\/gravatar\.com\/[a-zA-Z0-9]+$", Gravatar_url):
                    #     flash('Invalid Gravatar Url', 'error')

                    if not re.match(r"^[a-zA-Z0-9\s_]*$", display_name):
                        flash('Display name should be alphanumeric too', 'error')

                        # Check password strength and provide suggestions

                    if len(password) < 8:

                        flash(
                            'Password must be at least 8 characters long.', 'error')

                    elif not any(char.isdigit() for char in password):
                        flash(
                            'Password must contain at least one digit.', 'error')
                    elif not any(char.isalpha() for char in password):
                        flash(
                            'Password must contain at least one letter.', 'error')
                    elif not any(char.isupper() for char in password):
                        flash(
                            'Password must contain at least one uppercase letter.', 'error')
                    else:
                        # Hash the password before storing in the database
                        hashed_password = generate_password_hash(password)

                        # Insert new user into the database
                        cursor.execute(insert_user(username, email, hashed_password,
                                                   display_name, about_me, role, Gravatar_url),
                                       (username, email, hashed_password, display_name, about_me, role, Gravatar_url))
                        db.commit()
                        session.pop('registration_form_data', None)
                        session['registered_username'] = username
                        session['registered_password'] = password

                        flash(
                            'Registration successful. You can now log in.', 'success')
                        return redirect(url_for('auth.login'))
    form_data = session.pop('registration_form_data', {})
    return render_template('registration.html', form_data=form_data)


@auth_bp.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            flash('Username and password are required.', 'error')
        else:
            with db.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM Users WHERE username = %s", (username,))
                user = cursor.fetchone()

                if user is None:
                    flash('User not found', 'error')
                elif 'password_hash' not in user:
                    flash('Password information not found for the user', 'error')
                elif not check_password_hash(user['password_hash'], password):
                    flash('Invalid password', 'error')
                else:
                    session.clear()
                    session['user_id'] = user['user_id']
                    session['username'] = user['username']
                    session['display_name'] = user['display_name']
                    session['current_user'] = user
                    session['role'] = user['role']
                    session['avatar'] = user['Gravatar_url']
                    if session['role'] == 'Admin':
                        return redirect(url_for('users.admin'))
                    return redirect(url_for('posts.get_posts_and_tags'))

    # Return the template even if the login attempt fails
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
