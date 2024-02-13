from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, flash, session, redirect, url_for, jsonify, abort
import pymysql
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
from config import DATABASE_CONFIG
from queries import *
import re
from math import ceil

# from models import Users, Base
import datetime


app = Flask(__name__, template_folder='template')
app.secret_key = '#qwertyuiop!!!!234567$$'
db = pymysql.connect(**DATABASE_CONFIG, cursorclass=pymysql.cursors.DictCursor)


@app.route('/registration/', methods=['GET', 'POST'])
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
        Gravatar_url = request.form['Gravatar_url']

        # Check if all fields are provided
        if not username or not password or not confirm_password or not email or not display_name:
            session['registration_form_data'] = request.form
            flash('Please fill the required fields', 'error')

        elif password != confirm_password:
            session['registration_form_data'] = request.form
            flash('Passwords do not match.', 'error')

        else:
            # Check if the username or email already exists
            with db.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM Users WHERE username = %s OR email = %s", (username, email))
                existing_user = cursor.fetchone()

                if existing_user:
                    session['registration_form_data'] = request.form
                    flash(
                        'Username or email already exists. Please choose a different one.', 'error')

                else:
                    # Validate email format
                    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                        session['registration_form_data'] = request.form
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
                            session.pop('registration_form_data', None)
                            session['registered_username'] = username
                            session['registered_password'] = password

                            flash(
                                'Registration successful. You can now log in.', 'success')
                            return redirect(url_for('login'))
    form_data = session.pop('registration_form_data', {})
    return render_template('registration.html', form_data=form_data)


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
    user_id = session.get('user_id')
    background_image_url = url_for('static', filename='hero-bg.jpg')
    return render_template('index.html', background_image_url=background_image_url, user_id=user_id)


@app.route('/posts')
@login_required
def get_posts_and_tags():
    # Get the page parameter from the URL, default to 1 if not provided
    page = request.args.get('page', 1, type=int)
    if page < 1:
        abort(403)

    # Calculate the offset based on the page number
    offset = (page - 1) * POSTS_PER_PAGE

    with db.cursor() as cursor:
        # Fetch posts with LIMIT and OFFSET
        cursor.execute(all_posts(limit=POSTS_PER_PAGE, offset=offset))
        posts = cursor.fetchall()

        # Count the total number of posts for pagination
        cursor.execute(get_total_rows_query())
        total_posts = cursor.fetchone()["COUNT(*)"]
        total_pages = ceil(total_posts / POSTS_PER_PAGE)
        if page > total_pages:
            abort(403)

        # Fetch additional data (popularPosts, tags, categories) as needed
        cursor.execute(popular_posts())
        popularPosts = cursor.fetchall()

        cursor.execute(all_tags())
        tags = cursor.fetchall()

        cursor.execute(get_category())
        categories = cursor.fetchall()

    return render_template('post.html', posts=posts, popularPosts=popularPosts, tags=tags,
                           current_page=page, total_pages=total_pages, categories=categories)


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


def handle_like(user_id, comment_id):
    with db.cursor() as cursor:
        # Check if the user has already liked the comment
        query = "SELECT * FROM CommentScore WHERE user_id = %s AND comment_id = %s"
        cursor.execute(query, (user_id, comment_id))
        existing_like = cursor.fetchone()

        if existing_like:
            # User already liked, remove the like
            query = "DELETE FROM CommentScore WHERE user_id = %s AND comment_id = %s"
            cursor.execute(query, (user_id, comment_id))
        else:
            # User hasn't liked yet, add the like
            query = "INSERT INTO CommentScore (user_id, comment_id) VALUES (%s, %s)"
            cursor.execute(query, (user_id, comment_id))

        db.commit()


@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def view_post(post_id):
    if request.method == 'POST':
        user_id = session.get('user_id')

        if user_id:
            if 'action' in request.form:
                action = request.form['action']
            # Fetch the user's vote status for the post
                if action in ('upvote', 'downvote'):
                    handle_vote(post_id, user_id, action)
            if 'like' in request.form:
                comment_id = request.form.get('like')
                handle_like(user_id, comment_id)

            if 'comment' in request.form:
                comment_text = request.form['comment']
                if comment_text:
                    # Store the comment in the database
                    with db.cursor() as cursor:
                        query = "INSERT INTO Comments (post_id, user_id, text, create_date) VALUES (%s, %s, %s, NOW())"
                        cursor.execute(query, (post_id, user_id, comment_text))
                        db.commit()

                    flash('Comment posted successfully', 'success')
                    return redirect(url_for('view_post', post_id=post_id))

    with db.cursor() as cursor:
        query, params = get_post_details(post_id)
        cursor.execute(query, params)
        post = cursor.fetchone()

        query, params = get_comments(post_id)
        cursor.execute(query, params)
        comments = cursor.fetchall()

        cursor.execute(popular_posts())
        popularPosts = cursor.fetchall()

        cursor.execute(all_tags())
        tags = cursor.fetchall()

        cursor.execute(get_category())
        categories = cursor.fetchall()

        return render_template('singlepost.html', post=post, comments=comments, popularPosts=popularPosts, categories=categories, tags=tags, post_id=post_id, )


@app.route('/delete-comment', methods=['POST'])
@login_required
def delete_comment():
    user_id = session.get('user_id')
    comment_id = request.form.get('comment_id')

    # Fetch the comment from the database
    with db.cursor() as cursor:
        query = "SELECT user_id FROM Comments WHERE comment_id = %s"
        cursor.execute(query, (comment_id,))
        comment = cursor.fetchone()

        if comment and (comment['user_id'] == user_id or session.get('role') == 'admin'):
            # Delete the comment
            delete_query = "DELETE FROM Comments WHERE comment_id = %s"
            cursor.execute(delete_query, (comment_id,))
            db.commit()
            flash('Comment deleted successfully', 'success')
        else:
            flash('You are not authorized to delete this comment', 'error')

    return redirect(request.referrer)


@app.route('/update-comment', methods=['POST'])
@login_required
def update_comment():
    user_id = session.get('user_id')
    comment_id = request.form.get('comment_id')
    updated_comment_text = request.form.get('updated_comment_text')

    # Fetch the comment from the database
    with db.cursor() as cursor:
        query = "SELECT user_id FROM Comments WHERE comment_id = %s"
        cursor.execute(query, (comment_id,))
        comment = cursor.fetchone()

        if comment and comment['user_id'] == user_id:
            # Update the comment
            update_query = "UPDATE Comments SET text = %s WHERE comment_id = %s"
            cursor.execute(update_query, (updated_comment_text, comment_id))
            db.commit()
            flash('Comment updated successfully', 'success')
        else:
            flash('You are not authorized to update this comment', 'error')

    return redirect(request.referrer)


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


def get_tag_id(tag_name):
    with db.cursor() as cursor:
        cursor.execute(
            "SELECT tag_id FROM Tags WHERE tag_name = %s", (tag_name,))
        result = cursor.fetchone()
        return result[0] if result else None


@app.route('/delete-post', methods=['POST'])
@login_required
def delete_post():
    user_id = session.get('user_id')
    post_id = request.form.get('post_id')

    # Fetch the post from the database
    with db.cursor() as cursor:
        query = "SELECT user_id FROM Posts WHERE post_id = %s"
        cursor.execute(query, (post_id,))
        post = cursor.fetchone()

        if post and post['user_id'] == user_id:
            # Delete the post
            delete_query = "DELETE FROM Posts WHERE post_id = %s"
            cursor.execute(delete_query, (post_id,))
            db.commit()
            flash('Post deleted successfully', 'success')
        else:
            flash('You are not authorized to delete this post', 'error')

    return redirect(request.referrer)


@app.route('/edit-post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    # Fetch the post details from the database
    with db.cursor() as cursor:
        # Execute a SELECT query to fetch the post details by its ID
        query = "SELECT * FROM Posts WHERE post_id = %s"
        cursor.execute(query, (post_id,))
        post_data = cursor.fetchone()

        if post_data is None:
            # If no post is found with the given ID, return a 404 error
            abort(404)

        if request.method == 'POST':
            title = request.form.get('title')
            body = request.form.get('body')
            category = request.form.get('category')
            cursor.execute(get_category())
            categories = cursor.fetchall()

            if title and body and category:
                # Update the post details in the database
                update_query = "UPDATE Posts SET title = %s, body = %s, category = %s WHERE post_id = %s"
                cursor.execute(update_query, (title, body, category, post_id))
                db.commit()
                flash('Post updated successfully', 'success')
                return redirect(url_for('view_post', post_id=post_id))
            else:
                flash('Please fill in all fields', 'error')

    return render_template('edit_post.html', post=post_data, categories=categories)


@app.route('/newPost', methods=['GET', 'POST'])
@login_required
def newPost():
    with db.cursor() as cursor:
        cursor.execute(get_category())
        categories = cursor.fetchall()

        if request.method == 'POST':
            user_id = session.get('user_id')
            title = request.form['title']
            body = request.form['content']
            category = request.form['category']
            tags = request.form.get('tags', '').split(',')

            cursor.execute(
                "INSERT INTO Posts (title, body, category,  user_id,create_date) VALUES (%s, %s, %s, %s, NOW())",
                (title, body, category,  user_id)
            )
            post_id = cursor.lastrowid

            for tag_name in tags:
                cursor.execute(
                    "INSERT INTO Tags (tag_name) VALUES (%s) ON DUPLICATE KEY UPDATE tag_name=tag_name", (
                        tag_name,)
                )
                tag_id = cursor.lastrowid if cursor.rowcount == 1 else get_tag_id(
                    tag_name)
                cursor.execute(
                    "INSERT INTO PostTags (post_id, tag_id) VALUES (%s, %s)", (
                        post_id, tag_id)
                )

            db.commit()
            cursor.close()

    return render_template('insertPost.html', categories=categories)


@app.route('/<username>', methods=['GET', 'POST'])
def userPost(username):
    current_user = session.get('username')
    Username = username
    with db.cursor() as cursor:
        try:
            user_id = session.get('user_id')

            cursor.execute(get_author_info(username), (username,))
            user_info = cursor.fetchone()

            cursor.execute(get_author_posts(username), (username,))
            user_posts = cursor.fetchall()

            db.commit()
        except Exception as e:
            # Handle the exception appropriately, e.g., log the error
            print(f"Error fetching user information: {e}")
            user_info = None
            user_posts = []
            db.rollback()

    return render_template('account1.html', user_info=user_info, user_posts=user_posts, current_user=current_user, Username=Username)


@app.route('/admin', methods=['GET', 'POST'])
@login_required
@requires_role(['Admin'])
def admin():
    if request.method == 'POST':
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('login'))

    return render_template('adminDashboard.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
