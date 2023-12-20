# from flask import Flask, render_template, request, flash
# import pymysql

# from werkzeug.security import check_password_hash, generate_password_hash
# from config import DATABASE_CONFIG
# from queries import all_posts, all_tags, recent_posts, get_post_details, search_posts, get_comments, get_category
# from queries import get_user_by_username,  insert_user
# from flask import redirect, url_for
# from flask import session as flask_session


# @app.route('/registration/', methods=['GET', 'POST'])
# def registration():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = generate_password_hash(request.form['password'])
#         email = request.form['email']
#         display_name = request.form['display_name']
#         City = request.form['City']
#         State = request.form['State']
#         Country = request.form['Country']
#         about_me = request.form['about_me']
#         role = 'Regular User'
#         Gravatar_url = request.form['Gravatar_url']

#         with db.cursor() as cursor:
#             # Check if the username or email already exists
#             cursor.execute(
#                 "SELECT * FROM Users WHERE username = %s OR email = %s", (username, email))
#             existing_user = cursor.fetchone()

#             if existing_user:
#                 flash(
#                     'Username or email already exists. Please choose a different one.', 'error')
#             else:
#                 # Insert new user into the database

#                 cursor.execute(insert_user(username, email, password,
#                                display_name, City, State, Country, about_me, role, Gravatar_url))
#                 db.commit()

#                 flash('Registration successful. You can now log in.', 'success')
#                 return redirect(url_for('login'))

#     return render_template('registration.html')


# @app.route('/login/', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']

#         with db.cursor() as cursor:
#             # Retrieve user information by username
#             cursor.execute(get_user_by_username(username), (username,))
#             user = cursor.fetchone()

#             if user is None:
#                 flash('User not found', 'error')
#             # elif not check_password_hash(user['password'], password):
#             elif (user['password_hash'] != password):
#                 flash('Invalid password', 'error')
#             else:
#                 # Store user information in session
#                 flask_session['user_id'] = user['user_id']
#                 flash('Login successful!', 'success')
#                 return redirect(url_for('get_posts_and_tags'))

#     return render_template('login.html')
