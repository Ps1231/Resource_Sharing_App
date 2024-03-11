from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, flash,  make_response, session, redirect, url_for, jsonify, abort
import pymysql
from functools import wraps
from config import *
from queries import *
import re
from math import ceil
from auth import auth_bp

# from models import Users, Base
import datetime


app = Flask(__name__, template_folder='template')
app.secret_key = '#qwertyuiop!!!!234567$$'
# db = pymysql.connect(**DATABASE_CONFIG, cursorclass=pymysql.cursors.DictCursor)

app.register_blueprint(auth_bp)


# @app.route('/registration/', methods=['GET', 'POST'])
# def registration():
#     if request.method == 'POST':
#         # Limit username to 50 characters
#         username = request.form['username']
#         password = request.form['password']
#         confirm_password = request.form['confirm_password']
#         email = request.form['email']
#         # Limit display name to 50 characters
#         display_name = request.form['display_name']
#         # Limit about me to 130 characters
#         about_me = request.form['about_me']
#         role = 'Regular User'
#         Gravatar_url = request.form['Gravatar_url']
#         session['registration_form_data'] = request.form
#         # Check if all fields are provided
#         if not username or not password or not confirm_password or not email or not display_name or not Gravatar_url or not about_me:

#             flash('Please fill the required fields', 'error')

#         elif password != confirm_password:

#             flash('Passwords do not match.', 'error')

#         else:
#             # Check if the username or email already exists
#             with db.cursor() as cursor:
#                 cursor.execute(
#                     "SELECT * FROM Users WHERE username = %s OR email = %s", (username, email))
#                 existing_user = cursor.fetchone()

#                 if existing_user:

#                     flash(
#                         'Username or email already exists. Please choose a different one.', 'error')

#                 else:
#                     if not re.match(r"^[a-zA-Z0-9_]*$", username):
#                         flash('Username should be alphanumeric ', 'error')
#                     # Validate email format
#                     if not re.match(r"[^@]+@[^@]+\.[^@]+", email):

#                         flash('Invalid email address.', 'error')
#                     if not re.match(r"^https?:\/\/(www\.)?gravatar\.com\/avatar\/[a-zA-Z0-9]+(\?s=[0-9]+)?$", Gravatar_url):
#                         flash('Invalid Gravatar Url', 'error')

#                     if not re.match(r"^[a-zA-Z0-9_]*$", display_name):
#                         flash('Display name should be alphanumeric too', 'error')

#                         # Check password strength and provide suggestions

#                     if len(password) < 8:

#                         flash(
#                             'Password must be at least 8 characters long.', 'error')

#                     elif not any(char.isdigit() for char in password):
#                         flash(
#                             'Password must contain at least one digit.', 'error')
#                     elif not any(char.isalpha() for char in password):
#                         flash(
#                             'Password must contain at least one letter.', 'error')
#                     elif not any(char.isupper() for char in password):
#                         flash(
#                             'Password must contain at least one uppercase letter.', 'error')
#                     else:
#                         # Hash the password before storing in the database
#                         hashed_password = generate_password_hash(password)

#                         # Insert new user into the database
#                         cursor.execute(insert_user(username, email, hashed_password,
#                                                    display_name, about_me, role, Gravatar_url),
#                                        (username, email, hashed_password, display_name, about_me, role, Gravatar_url))
#                         db.commit()
#                         session.pop('registration_form_data', None)
#                         session['registered_username'] = username
#                         session['registered_password'] = password

#                         flash(
#                             'Registration successful. You can now log in.', 'success')
#                         return redirect(url_for('login'))
#     form_data = session.pop('registration_form_data', {})
#     return render_template('registration.html', form_data=form_data)


# @app.route('/login/', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         if not username or not password:
#             flash('Username and password are required.', 'error')
#         else:
#             with db.cursor() as cursor:
#                 cursor.execute(
#                     "SELECT * FROM Users WHERE username = %s", (username,))
#                 user = cursor.fetchone()

#                 if user is None:
#                     flash('User not found', 'error')
#                 elif 'password_hash' not in user:
#                     flash('Password information not found for the user', 'error')
#                 elif not check_password_hash(user['password_hash'], password):
#                     flash('Invalid password', 'error')
#                 else:
#                     session.clear()
#                     session['user_id'] = user['user_id']
#                     session['username'] = user['username']
#                     session['display_name'] = user['display_name']
#                     session['current_user'] = user
#                     session['role'] = user['role']

#                     return redirect(url_for('get_posts_and_tags'))

#     # Return the template even if the login attempt fails
#     return render_template('login.html')


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


# @app.route('/logout')
# def logout():
#     session.clear()
#     return redirect(url_for('index'))


# Number of posts to display per page
POSTS_PER_PAGE = 10


@app.route('/')
def index():
    user_id = session.get('user_id')
    with db.cursor() as cursor:
        cursor.execute(get_total_rows_query())
        posts = cursor.fetchone()['COUNT(*)']
        cursor.execute("select count(*)from Users")
        users = cursor.fetchone()['count(*)']
    background_image_url = url_for('static', filename='hero-bg.jpg')
    return render_template('index.html', background_image_url=background_image_url, user_id=user_id, posts=posts, users=users)


@app.route('/posts', methods=['GET', 'POST'])
@login_required
def get_posts_and_tags():
    search_query = request.values.get('search', '')
    selected_category = request.args.get('category')
    selected_tag = request.values.get('tag', '')

    page = request.args.get('page', 1, type=int)
    if page < 1:
        abort(404)

    offset = (page - 1) * POSTS_PER_PAGE

    with db.cursor() as cursor:
        if search_query:
            cursor.execute(search_posts(
                search_query, limit=POSTS_PER_PAGE, offset=offset))
        elif selected_category:
            cursor.execute(search_posts_by_category(
                selected_category, limit=POSTS_PER_PAGE, offset=offset))
        elif selected_tag:
            cursor.execute(search_posts_by_tag(
                selected_tag, limit=POSTS_PER_PAGE, offset=offset))
        else:
            cursor.execute(all_posts(limit=POSTS_PER_PAGE, offset=offset))
        posts = cursor.fetchall()

        if not search_query and not selected_category and not selected_tag:
            cursor.execute(get_total_rows_query())
            total_posts = cursor.fetchone()["COUNT(*)"]

        else:
            total_posts = len(posts)
        total_pages = ceil(total_posts / POSTS_PER_PAGE)
        if page > total_pages:
            abort(404)

        cursor.execute(popular_posts())
        popularPosts = cursor.fetchall()

        cursor.execute(all_tags())
        tags = cursor.fetchall()

        cursor.execute(get_category())
        categories = cursor.fetchall()

    return render_template('post.html', posts=posts, popularPosts=popularPosts, tags=tags, clicked_tag=selected_tag,
                           current_page=page, total_pages=total_pages, categories=categories, search_query=search_query, clicked_category=selected_category)


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

                    # flash('Comment posted successfully', 'success')
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

        return render_template('singlepost.html', post=post, comments=comments, popularPosts=popularPosts, categories=categories, tags=tags, post_id=post_id)


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
        session.pop('_flashes', [])
        if comment and (comment['user_id'] == user_id or session.get('role') == 'admin'):
            # Delete the comment
            delete_query = "DELETE FROM Comments WHERE comment_id = %s"
            cursor.execute(delete_query, (comment_id,))
            db.commit()
        #     flash('Comment deleted successfully', 'success')
        # else:
        #     flash('You are not authorized to delete this comment', 'error')

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

        # else:
        #     flash('You are not authorized to update this comment', 'error')

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
        session.pop('_flashes', [])
        if post and post['user_id'] == user_id:
            # Delete the post
            delete_query = "DELETE FROM Posts WHERE post_id = %s"
            cursor.execute(delete_query, (post_id,))
            db.commit()
            flash('Post deleted successfully', 'success')
        else:
            flash('You are not authorized to delete this post', 'error')
        session.pop('_flashes', [])

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

        tags_query = "SELECT t.tag_name FROM Tags t INNER JOIN PostTags pt ON t.tag_id = pt.tag_id WHERE pt.post_id = %s"
        cursor.execute(tags_query, (post_id,))
        tags_data = cursor.fetchall()
        tags = [tag['tag_name'] for tag in tags_data]

        if request.method == 'POST':
            title = request.form.get('title')
            body = request.form.get('body')
            category = request.form.get('category')
            new_tags = request.form.getlist('tag[]')

            cursor.execute(get_category())
            categories = cursor.fetchall()
            session.pop('_flashes', [])
            if title and body and category:
                # Update the post details in the database
                update_query = "UPDATE Posts SET title = %s, body = %s, category = %s WHERE post_id = %s"
                cursor.execute(update_query, (title, body, category, post_id))

                # Delete existing tags for the post
                delete_tags_query = "DELETE FROM PostTags WHERE post_id = %s"
                cursor.execute(delete_tags_query, (post_id,))

                if new_tags:
                    for tag in new_tags:
                        # Check if the tag already exists
                        cursor.execute(
                            "SELECT tag_id FROM Tags WHERE tag_name = %s", (tag,))
                        existing_tag = cursor.fetchone()
                        if existing_tag:
                            tag_id = existing_tag['tag_id']
                        else:
                            # If tag does not exist, insert it
                            cursor.execute(
                                "INSERT INTO Tags (tag_name) VALUES (%s)", (tag,))
                            tag_id = cursor.lastrowid
                        # Insert the tag-post relationship
                        cursor.execute(
                            "INSERT INTO PostTags (post_id, tag_id) VALUES (%s, %s)", (post_id, tag_id))

                db.commit()

                flash('Post updated successfully', 'success')

            else:
                flash('Please fill in all fields', 'error')

    return render_template('edit_post.html', post=post_data, tags=tags, categories=categories)


def get_tag_id(tag_name):
    with db.cursor() as cursor:
        try:
            cursor.execute(
                "SELECT tag_id FROM Tags WHERE tag_name = %s", (tag_name,))
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                return None
        except Exception as e:
            print("Error fetching tag_id:", e)
            return None


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
            tags = request.form.getlist('tag[]')
            session['post_form_data'] = request.form
            errors = []
            if not re.match(r"^[a-zA-Z0-9_ ]+$", title):
                errors.append('Title should be alphanumeric')
            if not all(re.match(r"[a-zA-Z]", tag) for tag in tags):
                errors.append('Tags must contain letters only.')
            # Check if the body contains at least one letter
            if not re.search(r"[a-zA-Z]", body):
                errors.append('Body content is not valid; contains no letters')
            # Retrieve tags list directly from the request object
            if not title or not body or not category or not tags:
                errors.append('Please fill in all fields.')
            if errors:
                for error in errors:
                    flash(error, 'error')
                return redirect(url_for('newPost'))
            else:
                cursor.execute(
                    "INSERT INTO Posts (title, body, category,  user_id, create_date) VALUES (%s, %s, %s, %s, NOW())",
                    (title, body, category,  user_id)
                )
                post_id = cursor.lastrowid

                for tag_name in tags:
                    # Check if the tag already exists in the Tags table
                    cursor.execute(
                        "SELECT tag_id FROM Tags WHERE tag_name = %s", (tag_name,))
                    tag_row = cursor.fetchall()

                    if tag_row:
                        # If tag exists, get its tag_id
                        tag_id = tag_row[0]['tag_id']
                    else:
                        # If tag doesn't exist, insert it into Tags table
                        cursor.execute(
                            "INSERT INTO Tags (tag_name) VALUES (%s)", (tag_name,))
                        tag_id = cursor.lastrowid

                    # Insert entry into PostTags table
                    cursor.execute(
                        "INSERT INTO PostTags (post_id, tag_id) VALUES (%s, %s)", (post_id, tag_id))
                    session.pop('post_form_data', None)
                db.commit()
                cursor.close()
                session.pop('_flashes', [])
                flash('Post created successfully', 'success')

                # return redirect(url_for('account'))
    form_data = session.pop('post_form_data', {})
    return render_template('insertPost.html', categories=categories, form_data=form_data)


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
