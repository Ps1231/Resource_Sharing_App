from flask import Flask, render_template, request, flash
import pymysql

from werkzeug.security import check_password_hash, generate_password_hash
from config import DATABASE_CONFIG
from queries import all_posts, all_tags, recent_posts, get_post_details, search_posts, get_comments, get_category
from queries import get_user_by_username,  insert_user
from flask import redirect, url_for
from flask import session as flask_session
# from models import Users, Base
import datetime


app = Flask(__name__, template_folder='template')
app.secret_key = '#qwertyuiop!!!!234567$$'
db = pymysql.connect(**DATABASE_CONFIG, cursorclass=pymysql.cursors.DictCursor)

# engine = create_engine("mysql+pymysql://root:rashi@2003@localhost/resource")
# Base.metadata.create_all(engine)  # Create tables if they don't exist
# Session = sessionmaker(bind=engine)
# ss = Session()

# Number of posts to display per page
POSTS_PER_PAGE = 10


@app.route('/posts')
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


@app.route('/post/<int:post_id>')
def view_post(post_id):
    with db.cursor() as cursor:
        query, params = get_post_details(post_id)
        cursor.execute(query, params)
        post = cursor.fetchone()

        query, params = get_comments(post_id)  # Separate query and params
        cursor.execute(query, params)
        comments = cursor.fetchall()

        cursor.execute(recent_posts())
        recentPosts = cursor.fetchall()

        cursor.execute(all_tags())
        tags = cursor.fetchall()

        cursor.execute(get_category())
        categories = cursor.fetchall()

    return render_template('singlepost.html', post=post, comments=comments, recentPosts=recentPosts, categories=categories, tags=tags)


@app.route('/registration/', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        email = request.form['email']
        display_name = request.form['display_name']
        City = request.form['City']
        State = request.form['State']
        Country = request.form['Country']
        about_me = request.form['about_me']
        role = 'Regular User'
        Gravatar_url = request.form['Gravatar_url']

        with db.cursor() as cursor:
            # Check if the username or email already exists
            cursor.execute(
                "SELECT * FROM Users WHERE username = %s OR email = %s", (username, email))
            existing_user = cursor.fetchone()

            if existing_user:
                flash(
                    'Username or email already exists. Please choose a different one.', 'error')
            else:
                # Insert new user into the database

                cursor.execute(insert_user(username, email, password,
                               display_name, City, State, Country, about_me, role, Gravatar_url))
                db.commit()

                flash('Registration successful. You can now log in.', 'success')
                return redirect(url_for('login'))

    return render_template('registration.html')


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with db.cursor() as cursor:
            # Retrieve user information by username
            cursor.execute(get_user_by_username(username), (username,))
            user = cursor.fetchone()

            if user is None:
                flash('User not found', 'error')
            # elif not check_password_hash(user['password'], password):
            elif (user['password_hash'] != password):
                flash('Invalid password', 'error')
            else:
                # Store user information in session
                flask_session['user_id'] = user['user_id']
                flash('Login successful!', 'success')
                return redirect(url_for('get_posts_and_tags'))

    return render_template('login.html')


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         user = session.query(Users).filter_by(username=username).first()

#         if user is None:
#             flash('User not found', 'error')
#         elif not check_password_hash(user.password_hash, password):
#             flash('Invalid password', 'error')
#         else:
#             # Use 'user_id' for session key
#             flask_session['user_id'] = user.user_id
#             flash('Login successful!', 'success')
#             return redirect(url_for('index'))

#     return render_template('login.html')


# @app.route('/registration/', methods=['POST', 'GET'])
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

#         if session.query(Users).filter_by(username=username).first() or session.query(Users).filter_by(email=email).first():
#             flash(
#                 'Username or email already exists. Please choose a different one.', 'error')

#         else:
#             user = Users(username=username, password_hash=password, email=email, display_name=display_name,
#                          City=City,
#                          State=State,
#                          Country=Country,
#                          about_me=about_me,
#                          role=role,
#                          Gravatar_url=Gravatar_url,
#                          creation_date=datetime.utcnow())

#             session.add(user)
#             session.commit()

#             flash('Registration successful. You can now log in.', 'success')
#             return redirect(url_for('login'))

#     return render_template('registration.html')


if __name__ == '__main__':
    app.run(debug=True)
