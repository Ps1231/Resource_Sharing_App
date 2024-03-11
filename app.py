from flask import Flask, render_template,   session,  url_for
from queries import *
from auth import auth_bp
from singlepost import singlepost_bp
from posts import posts_bp
from users import users_bp
# from models import Users, Base


app = Flask(__name__, template_folder='template')
app.secret_key = '#qwertyuiop!!!!234567$$'


app.register_blueprint(auth_bp)
app.register_blueprint(posts_bp)
app.register_blueprint(singlepost_bp)
app.register_blueprint(users_bp)


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


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
