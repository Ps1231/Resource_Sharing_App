from flask import Flask, render_template, request
import pymysql
from config import DATABASE_CONFIG
from queries import all_posts, all_tags, recent_posts, get_post_details, search_posts, get_comments, get_category
from flask import redirect, url_for
app = Flask(__name__, template_folder='template')
db = pymysql.connect(**DATABASE_CONFIG, cursorclass=pymysql.cursors.DictCursor)

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

    return render_template('singlepost.html', post=post, comments=comments)


if __name__ == '__main__':
    app.run(debug=True)
# @app.route('/', methods=['GET', 'POST'])
# def index():
#     result = None
#     if request.method == 'POST':
#         person_name = request.form.get('person_name')
#         if person_name:
#             with db.cursor() as cursor:
#                 cursor.execute(get_user_details(person_name), (person_name,))

#                 result = cursor.fetchone()
#     return render_template('index.html', result=result)

# def tags():
#     with db.cursor() as cursor:
#         cursor.execute('''select * from Tags''')
#         tags = cursor.fetchall()
#         return render_template('post.html', tags=tags)

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     result = None
#     if request.method == 'POST':
#         person_name = request.form.get('person_name')
#         if person_name:
#             with db.cursor() as cursor:
#                 cursor.execute(get_user_details(person_name), (person_name,))

#                 result = cursor.fetchone()
#     return render_template('index.html', result=result)


# @app.route('/User')
# def user_list():
#     with db.cursor() as cursor:
#         cursor.execute(get_users_from_database())
#         users = cursor.fetchall()

#     return render_template('user_list.html', users=users)
