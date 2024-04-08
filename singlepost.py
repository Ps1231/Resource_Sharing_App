from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from queries import *
from config import db
from util import login_required

singlepost_bp = Blueprint('singlepost', __name__, url_prefix='/singlepost')


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


@singlepost_bp.route('/post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def view_post(post_id):
    category_post_counts = get_category_post_counts()
    if category_post_counts is None:
        flash('Failed to fetch category post counts', 'error')
        category_post_counts = {}
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
                    return redirect(url_for('singlepost.view_post', post_id=post_id))

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

        return render_template('singlepost.html', post=post, comments=comments, popularPosts=popularPosts, categories=categories, tags=tags, post_id=post_id, category_post_counts=category_post_counts)


@singlepost_bp.route('/delete-comment', methods=['POST'])
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


@singlepost_bp.route('/update-comment', methods=['POST'])
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
