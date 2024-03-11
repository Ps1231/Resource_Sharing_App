from flask import Blueprint, render_template, request, flash, session, redirect, url_for, abort
from math import ceil
from queries import *
from config import db
from util import login_required
import re

posts_bp = Blueprint('posts', __name__, url_prefix='/posts')
POSTS_PER_PAGE = 10


@posts_bp.route('/posts', methods=['GET', 'POST'])
@login_required
def get_posts_and_tags():
    search_query = request.values.get('search', '')
    selected_category = request.args.get('category')
    selected_tag = request.values.get('tag', '')

    page = request.args.get('page', 1, type=int)
    if page < 1:
        return render_template('error.html')

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
            if total_posts == 0:
                return render_template('error.html')
        else:
            total_posts = len(posts)
        total_pages = ceil(total_posts / POSTS_PER_PAGE)
        if page > total_pages:
            return render_template('error.html')

        cursor.execute(popular_posts())
        popularPosts = cursor.fetchall()

        cursor.execute(all_tags())
        tags = cursor.fetchall()

        cursor.execute(get_category())
        categories = cursor.fetchall()

    return render_template('post.html', posts=posts, popularPosts=popularPosts, tags=tags, clicked_tag=selected_tag,
                           current_page=page, total_pages=total_pages, categories=categories, search_query=search_query, clicked_category=selected_category)


@posts_bp.route('/delete-post', methods=['POST'])
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


@posts_bp.route('/edit-post/<int:post_id>', methods=['GET', 'POST'])
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


@posts_bp.route('/newPost', methods=['GET', 'POST'])
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
                return redirect(url_for('posts.newPost'))
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
