from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, flash, session, redirect, url_for
import pymysql
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
from config import DATABASE_CONFIG
from queries import *
import re

# from models import Users, Base
import datetime


app = Flask(__name__, template_folder='template')
app.secret_key = '#qwertyuiop!!!!234567$$'
db = pymysql.connect(**DATABASE_CONFIG, cursorclass=pymysql.cursors.DictCursor)


@app.route('/registration/', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        # Limit username to 50 characters
        username = request.form['username'][:50]
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        email = request.form['email']
        # Limit display name to 50 characters
        display_name = request.form['display_name'][:50]
        # Limit about me to 130 characters
        about_me = request.form['about_me'][:130]
        role = 'Regular User'
        Gravatar_url = request.form['Gravatar_url']

        # Check if all fields are provided
        if not username or not password or not confirm_password or not email or not display_name:
            flash('All fields are required.', 'error')
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
                    # Validate email format
                    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                        flash('Invalid email address.', 'error')
                    else:
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

                            flash(
                                'Registration successful. You can now log in.', 'success')
                            return redirect(url_for('login'))

    return render_template('registration.html')


@app.route('/login/', methods=['GET', 'POST'])
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
                    session['current_user'] = user
                    session['role'] = user['role']
                    flash('Login successful!', 'success')
                    return redirect(url_for('get_posts_and_tags'))

    # Return the template even if the login attempt fails
    return render_template('login.html')


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if 'username' in session:
            # User is authenticated, execute the original view function
            return view(*args, **kwargs)
        else:
            # User is not authenticated, redirect to the login page
            flash("You are not logged in. Please log in to access this page.", 'error')
            return redirect(url_for('login'))

    return wrapped_view


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# Number of posts to display per page
POSTS_PER_PAGE = 10


@app.route('/')
def index():
    background_image_url = url_for('static', filename='hero-bg.jpg')
    return render_template('index.html', background_image_url=background_image_url)


@app.route('/posts')
@login_required
def get_posts_and_tags():
    # Get the page parameter from the URL, default to 1 if not provided
    page = int(request.args.get('page', 1))

    # Get the search query from the URL parameters
    search_query = request.args.get('search_query', '')

    # Calculate the offset based on the page number
    offset = (page - 1) * POSTS_PER_PAGE

    with db.cursor() as cursor:
        if search_query:
            # Remove limit and offset from the search_posts call
            cursor.execute(search_posts(search_query))
        else:
            cursor.execute(all_posts(limit=POSTS_PER_PAGE, offset=offset))
        posts = cursor.fetchall()

        # Count the total number of posts for pagination
        if search_query:
            cursor.execute(
                "SELECT COUNT(*) FROM Posts WHERE title LIKE %s OR content LIKE %s", (search_query, search_query))
        else:
            cursor.execute("SELECT COUNT(*) FROM Posts")
        total_posts = cursor.fetchone()["COUNT(*)"]
        total_pages = (total_posts + POSTS_PER_PAGE - 1) // POSTS_PER_PAGE

        cursor.execute(recent_posts())
        recentPosts = cursor.fetchall()

        cursor.execute(all_tags())
        tags = cursor.fetchall()

        cursor.execute(get_category())
        categories = cursor.fetchall()
    return render_template('post.html', posts=posts, recentPosts=recentPosts, tags=tags, current_page=page, total_pages=total_pages, categories=categories)


@app.route('/search', methods=['GET'])
def search_redirect():
    # Get the search query from the URL parameters
    search_query = request.args.get('search_query', '')

    # Redirect to the main posts route with the search query
    return redirect(url_for('get_posts_and_tags', search_query=search_query))


def handle_vote(post_id, user_id, vote_type):
    with db.cursor() as cursor:
        # Check if the user has already voted on this post
        cursor.execute(
            "SELECT vote_type FROM Votes WHERE post_id = %s AND user_id = %s",
            (post_id, user_id)
        )
        existing_vote = cursor.fetchone()

        if existing_vote:
            # User has already voted, check if the same vote_type is selected
            if existing_vote['vote_type'] == vote_type:
                # Same vote_type, revert the vote
                cursor.execute(
                    "DELETE FROM Votes WHERE post_id = %s AND user_id = %s",
                    (post_id, user_id)
                )
            else:
                # Different vote_type, update the vote
                cursor.execute(
                    "UPDATE Votes SET vote_type = %s WHERE post_id = %s AND user_id = %s",
                    (vote_type, post_id, user_id)
                )
        else:
            # Insert the new vote
            cursor.execute(
                "INSERT INTO Votes (post_id, user_id, vote_type, create_date) VALUES (%s, %s, %s, NOW())",
                (post_id, user_id, vote_type)
            )

        db.commit()


def check_user_vote(post_id, user_id, vote_type):
    with db.cursor() as cursor:
        cursor.execute(
            "SELECT vote_type FROM Votes WHERE post_id = %s AND user_id = %s",
            (post_id, user_id)
        )
        existing_vote = cursor.fetchone()

        if existing_vote and existing_vote['vote_type'] == vote_type:
            return True
        else:
            return False


@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def view_post(post_id):
    if request.method == 'POST':
        action = request.form['action']
        user_id = session.get('user_id')

        if user_id:
            # Fetch the user's vote status for the post

            if action in ('upvote', 'downvote'):
                handle_vote(post_id, user_id, action)

    with db.cursor() as cursor:
        query, params = get_post_details(post_id)
        cursor.execute(query, params)
        post = cursor.fetchone()

        query, params = get_comments(post_id)
        cursor.execute(query, params)
        comments = cursor.fetchall()

        cursor.execute(recent_posts())
        recentPosts = cursor.fetchall()

        cursor.execute(all_tags())
        tags = cursor.fetchall()

        cursor.execute(get_category())
        categories = cursor.fetchall()

        return render_template('singlepost.html', post=post, comments=comments, recentPosts=recentPosts, categories=categories, tags=tags)


def requires_role(roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(*args, **kwargs):
            if session.get('role') in roles:
                return view_func(*args, **kwargs)
            else:
                return 'Access Denied'

        return wrapped_view

    return decorator


@app.route('/account')
@login_required
@requires_role(['Regular User'])
def account():
    with db.cursor() as cursor:
        try:
            # Fetch user information
            user_id = session.get('user_id')
            cursor.execute(get_user_info(user_id))
            user_info = cursor.fetchone()
            # Fetch posts of the current user
            cursor.execute(get_user_posts(user_id))
            user_posts = cursor.fetchall()
            db.commit()
        except Exception as e:
            # Handle the exception appropriately, e.g., log the error
            print(f"Error fetching user information: {e}")
            user_info = None
            user_posts = []

    return render_template('account1.html', user_info=user_info, user_posts=user_posts)


@app.route('/newPost')
@login_required
@requires_role(['Regular User'])
def newPost():
    return render_template('insertPost.html')


if __name__ == '__main__':
    app.run(debug=True)
