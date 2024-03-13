from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from queries import *
from config import db
from util import *


users_bp = Blueprint('users', __name__, url_prefix='/users')

# Define your user-related routes here


@users_bp.route('/account')
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


@users_bp.route('/<username>', methods=['GET', 'POST'])
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


@users_bp.route('/admin', methods=['GET', 'POST'])
@login_required
@requires_role(['Admin'])
def admin():
    if request.method == 'POST':
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('auth.login'))

    return render_template('adminIndex.html')


@users_bp.route('/adminProfile', methods=['GET', 'POST'])
@login_required
@requires_role(['Admin'])
def adminProfile():
    return render_template('users-profile.html')


@users_bp.route('/adminAuthorStatus', methods=['GET', 'POST'])
@login_required
@requires_role(['Admin'])
def authorStatus():
    return render_template('tables-data.html')


@users_bp.route('/adminPostCategories', methods=['GET', 'POST'])
@login_required
@requires_role(['Admin'])
def postCategories():
    return render_template("pages-contact.html")


@users_bp.route('/adminReportrdPosts', methods=['GET', 'POST'])
@login_required
@requires_role(['Admin'])
def reportedPosts():
    return render_template("reported-posts.html")
