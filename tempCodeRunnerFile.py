
@app.route('/newPost', methods=['GET', 'POST'])
@login_required
def newPost():
    with db.cursor() as cursor:
        cursor.execute(get_category())
        categories = cursor.fetchall()

        if request.method == 'POST':
            data = request.json
            user_id = session.get('user_id')
            title = request.form['title']
            body = request.form['content']
            category = request.form['category']

            # Retrieve tags list directly from the request object
            tags = data.get('tagIds')

            cursor.execute(
                "INSERT INTO Posts (title, body, category,  user_id, create_date) VALUES (%s, %s, %s, %s, NOW())",
                (title, body, category,  user_id)
            )
            post_id = cursor.lastrowid

            for tag_name in tags:
                # Check if the tag already exists in the Tags table
                cursor.execute(
                    "SELECT tag_id FROM Tags WHERE tag_name = %s", (tag_name,))
                tag_row = cursor.fetchone()

                if tag_row:
                    # If tag exists, get its tag_id
                    tag_id = tag_row[0]
                else:
                    # If tag doesn't exist, insert it into Tags table
                    cursor.execute(
                        "INSERT INTO Tags (tag_name) VALUES (%s)", (tag_name,))
                    tag_id = cursor.lastrowid

                # Insert entry into PostTags table
                cursor.execute(
                    "INSERT INTO PostTags (post_id, tag_id) VALUES (%s, %s)", (post_id, tag_id))

            db.commit()
            cursor.close()

    return render_template('insertPost.html', categories=categories)
