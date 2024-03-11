
# @app.route('/<username>', methods=['GET', 'POST'])
# def userPost(username):
#     current_user = session.get('username')
#     Username = username
#     with db.cursor() as cursor:
#         try:
#             user_id = session.get('user_id')

#             cursor.execute(get_author_info(username), (username,))
#             user_info = cursor.fetchone()

#             cursor.execute(get_author_posts(username), (username,))
#             user_posts = cursor.fetchall()

#             db.commit()
#         except Exception as e:
#             # Handle the exception appropriately, e.g., log the error
#             print(f"Error fetching user information: {e}")
#             user_info = None
#             user_posts = []
#             db.rollback()

#     return render_template('account1.html', user_info=user_info, user_posts=user_posts, current_user=current_user, Username=Username)


# @app.route('/admin', methods=['GET', 'POST'])
# @login_required
# @requires_role(['Admin'])
# def admin():
#     if request.method == 'POST':
#         user_id = session.get('user_id')
#         if not user_id:
#             return redirect(url_for('login'))

#     return render_template('adminDashboard.html')
