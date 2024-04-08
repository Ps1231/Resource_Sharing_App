from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from queries import *
from config import db
from util import *
import mysql.connector

users_bp = Blueprint('users', __name__, url_prefix='/users')

# Define your user-related routes here


def extract_categories():
    with db.cursor() as cursor:
        cursor.execute("DESCRIBE Posts")
        enum_definition = cursor.fetchall()
        categories = []
        for field in enum_definition:
            if field['Field'] == 'category':
                enum_values = field['Type']
                categories = enum_values[6:-2].replace("'", "").split(",")
                break
        return categories


def get_category_post_counts():
    try:
        with db.cursor() as cursor:
            # Fetch the list of categories
            categories = extract_categories()

            # Initialize a dictionary to store category post counts
            category_post_counts = {}

            # Iterate over each category
            for category in categories:
                # Query the database to count the number of posts in the category
                cursor.execute(
                    f"SELECT COUNT(*) AS post_count FROM Posts WHERE category = '{category}'")
                result = cursor.fetchone()
                post_count = result['post_count'] if result else 0

                # Store the category and its post count in the dictionary
                category_post_counts[category] = post_count

            return category_post_counts
    except mysql.connector.Error as error:
        print("Error:", error)
        return None


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
    with db.cursor() as cursor:
        cursor.execute(top_tags())
        get_top_tags = cursor.fetchall()
        cursor = db.cursor()
        cursor.execute(top_author())
        top_users = cursor.fetchall()
        cursor.execute(recent_posts())
        get_recent_posts = cursor.fetchall()
        cursor.execute(popular_posts())
        popularPosts = cursor.fetchall()
        cursor.execute(get_total_rows_query())
        posts = cursor.fetchone()['COUNT(*)']
        cursor.execute("select count(*)from Users")
        users = cursor.fetchone()['count(*)']

    return render_template('adminIndex.html', posts=posts, users=users, top_users=top_users, popularPosts=popularPosts, get_top_tags=get_top_tags, get_recent_posts=get_recent_posts)


@users_bp.route('/adminProfile', methods=['GET', 'POST'])
@login_required
@requires_role(['Admin'])
def adminProfile():
    return render_template('users-profile.html')


@users_bp.route('/adminAuthorStatus', methods=['GET', 'POST'])
@login_required
@requires_role(['Admin'])
def authorStatus():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        if user_id:
            with db.cursor() as cursor:
                sql = "UPDATE Users SET role='Admin' WHERE user_id=%s"
                cursor.execute(sql, (user_id,))
                db.commit()

    with db.cursor() as cursor:
        cursor.execute(author_status())
        users = cursor.fetchall()

    return render_template('tables-data.html', users=users)


def add_category_to_posts_table(new_category):
    try:
        with db.cursor() as cursor:
            # Alter the table to add the new category to the enum
            current_categories = extract_categories()
            if current_categories is None:
                print("Failed to fetch current categories.")
                return False
            current_categories.append(new_category)
            enum_values = "','".join(current_categories)
            enum_definition = f"ENUM('{enum_values}')"
            alter_query = f"ALTER TABLE Posts MODIFY category {enum_definition}"
            cursor.execute(alter_query)
            # Commit the changes
            db.commit()
            return True
    except mysql.connector.Error as error:
        print("Error:", error)
        return False


def delete_category_and_posts(category):
    try:
        with db.cursor() as cursor:
            cursor.execute("SET SQL_SAFE_UPDATES = 0")
            delete_posts_query = f"DELETE FROM Posts WHERE category = '{category}'"
            cursor.execute(delete_posts_query)

            # Fetch the updated list of categories
            categories = extract_categories()

            # Remove the category from the list of categories
            if category in categories:
                categories.remove(category)

            # Construct the new enum definition
            enum_values = "','".join(categories)
            enum_definition = f"ENUM('{enum_values}')"
            alter_query = f"ALTER TABLE Posts MODIFY category {enum_definition}"
            cursor.execute(alter_query)
            db.commit()

            return True
    except mysql.connector.Error as error:
        # Rollback changes if an error occurs

        print("Error:", error)
        return False


@users_bp.route('/adminPostCategories', methods=['GET', 'POST'])
@login_required
@requires_role(['Admin'])
def postCategories():
    category_post_counts = get_category_post_counts()

    if category_post_counts is None:
        flash('Failed to fetch category post counts', 'error')
        category_post_counts = {}
    if request.method == 'POST':

        if 'add' in request.form:
            new_category = request.form['add']
            if add_category_to_posts_table(new_category):
                # Redirect to the same page after adding the category
                return redirect(url_for('users.postCategories'))
            else:
                flash('Failed to add category', 'error')  # Flash error message
        elif 'delete' in request.form:
            category_to_delete = request.form['delete']
            if delete_category_and_posts(category_to_delete):
                # Redirect to the same page after deleting the category
                return redirect(url_for('users.postCategories'))
            else:
                # Flash error message
                flash('Failed to delete category', 'error')

    # # Fetch categories
    # with db.cursor() as cursor:
    #     cursor.execute(get_category())
    #     categories = cursor.fetchall()

    return render_template("post_categories.html",  category_post_counts=category_post_counts)


@users_bp.route('/adminReportrdPosts', methods=['GET', 'POST'])
@login_required
@requires_role(['Admin'])
def reportedPosts():
    if request.method == 'POST':
        # Handle post deletion here
        post_id_to_delete = request.form.get('post_id')
        if post_id_to_delete:
            with db.cursor() as cursor:
                delete_query = "DELETE FROM Posts WHERE post_id = %s"
                cursor.execute(delete_query, (post_id_to_delete,))
                db.commit()

    # Fetch all posts using the all_posts function
    with db.cursor() as cursor:
        cursor.execute(all_posts())
        posts = cursor.fetchall()

    return render_template("reported-posts.html", posts=posts)
