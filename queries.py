import pymysql
from config import DATABASE_CONFIG
db = pymysql.connect(**DATABASE_CONFIG, cursorclass=pymysql.cursors.DictCursor)


def all_posts(limit=None, offset=None):
    query = '''SELECT
    p.post_id,
    u.gravatar_url as user_image,
    u.display_name as display_name,
    p.title as post_title,
    p.body AS post_content,
    p.category as category,
    p.create_date as create_date,
    (select count(*) from Votes where post_id=p.post_id and vote_type='upvote' ) as upvote_count,
    (select count(*) from Votes where post_id=p.post_id and vote_type='downvote' ) as downvote_count,
    (SELECT COUNT(*) FROM Comments WHERE post_id = p.post_id) as comment_count,
    GROUP_CONCAT(t.tag_name) as tags
FROM
    Posts p
    INNER JOIN Users u ON p.user_id = u.user_id
    LEFT JOIN Votes v ON p.post_id = v.post_id
    INNER JOIN PostTags pt ON p.post_id = pt.post_id
    INNER JOIN Tags t ON pt.tag_id = t.tag_id
GROUP BY
    p.post_id
ORDER BY
    p.create_date DESC
'''

    if limit is not None:
        query += f" LIMIT {limit}"
    if offset is not None:
        query += f" OFFSET {offset}"

    return query


def get_total_rows_query():
    return f"SELECT COUNT(*) FROM ({all_posts()}) AS subquery"


def search_posts(search_query, limit=None, offset=None):
    query = f'''
        SELECT
            p.post_id,
            u.gravatar_url AS user_image,
            u.display_name AS display_name,
            p.title AS post_title,
            p.body AS post_content,
            p.category AS category,
            p.create_date AS create_date,
            (SELECT COUNT(*) FROM Votes WHERE post_id = p.post_id AND vote_type = 'upvote') AS upvote_count,
            (SELECT COUNT(*) FROM Votes WHERE post_id = p.post_id AND vote_type = 'downvote') AS downvote_count,
            (SELECT COUNT(*) FROM Comments WHERE post_id = p.post_id) AS comment_count,
            GROUP_CONCAT(t.tag_name) AS tags
        FROM
            Posts p
            INNER JOIN Users u ON p.user_id = u.user_id
            LEFT JOIN Votes v ON p.post_id = v.post_id
            INNER JOIN PostTags pt ON p.post_id = pt.post_id
            INNER JOIN Tags t ON pt.tag_id = t.tag_id
        WHERE
            p.title LIKE '%{search_query}%' OR
            p.title LIKE '{search_query}%' OR
            p.title LIKE '%{search_query}'

        GROUP BY
            p.post_id
        ORDER BY
            p.create_date DESC
    '''
    return query


def search_posts_by_category(category, limit=None, offset=None):
    query = f'''
        SELECT
            p.post_id,
            u.gravatar_url AS user_image,
            u.display_name AS display_name,
            p.title AS post_title,
            p.body AS post_content,
            p.category AS category,
            p.create_date AS create_date,
            (SELECT COUNT(*) FROM Votes WHERE post_id = p.post_id AND vote_type = 'upvote') AS upvote_count,
            (SELECT COUNT(*) FROM Votes WHERE post_id = p.post_id AND vote_type = 'downvote') AS downvote_count,
            (SELECT COUNT(*) FROM Comments WHERE post_id = p.post_id) AS comment_count,
            GROUP_CONCAT(t.tag_name) AS tags
        FROM
            Posts p
            INNER JOIN Users u ON p.user_id = u.user_id
            LEFT JOIN Votes v ON p.post_id = v.post_id
            LEFT JOIN PostTags pt ON p.post_id = pt.post_id
            LEFT JOIN Tags t ON pt.tag_id = t.tag_id
        WHERE
            p.category = '{category}'
        GROUP BY
            p.post_id
        ORDER BY
            p.create_date DESC
    '''
    return query


def search_posts_by_tag(tag, limit=None, offset=None):
    query = f'''
        SELECT
            p.post_id,
            u.gravatar_url AS user_image,
            u.display_name AS display_name,
            p.title AS post_title,
            p.body AS post_content,
            p.category AS category,
            p.create_date AS create_date,
            (SELECT COUNT(*) FROM Votes WHERE post_id = p.post_id AND vote_type = 'upvote') AS upvote_count,
            (SELECT COUNT(*) FROM Votes WHERE post_id = p.post_id AND vote_type = 'downvote') AS downvote_count,
            (SELECT COUNT(*) FROM Comments WHERE post_id = p.post_id) AS comment_count,
            GROUP_CONCAT(t.tag_name) AS tags
        FROM
            Posts p
            INNER JOIN Users u ON p.user_id = u.user_id
            LEFT JOIN Votes v ON p.post_id = v.post_id
            left JOIN PostTags pt ON p.post_id = pt.post_id
            left JOIN Tags t ON pt.tag_id = t.tag_id
        WHERE
            t.tag_name = '{tag}'
        GROUP BY
            p.post_id
        ORDER BY
            p.create_date DESC
    '''

    if limit is not None:
        query += f" LIMIT {limit}"
    if offset is not None:
        query += f" OFFSET {offset}"

    return query


def all_tags():
    return '''SELECT
    Tags.tag_name as name,
    COUNT(PostTags.post_id) AS tag_count
FROM
    Tags
JOIN
    PostTags ON Tags.tag_id = PostTags.tag_id
GROUP BY
    Tags.tag_name
ORDER BY
    tag_count DESC
LIMIT 5;'''


def popular_posts():
    return '''SELECT
    p.post_id as post_id,
    p.title as title,
    p.body as post_body, -- Corrected alias name for p.body
    DATE_FORMAT(p.create_date, '%e %b %Y') as date,
    (SELECT COUNT(*) FROM Votes WHERE post_id = p.post_id AND vote_type = 'upvote') as upvote_count
FROM
    Posts p
    LEFT JOIN Votes v ON p.post_id = v.post_id
WHERE
    v.vote_type = 'upvote' OR v.vote_type IS NULL
GROUP BY
    p.post_id
ORDER BY
    upvote_count DESC
LIMIT
    5;
'''


# queries.py


def get_post_details(post_id):
    query = '''
        SELECT
            p.post_id as post_id,
            p.user_id as user_id,
            u.gravatar_url as user_image,
            u.about_me as about,
            u.role,
            u.display_name as display_name,
            p.title as post_title,
            p.body AS post_content,
            p.category as category,
            p.create_date as create_date,
             (select count(*) from Votes where post_id=p.post_id and vote_type='upvote' ) as upvote_count,
            (select count(*) from Votes where post_id=p.post_id and vote_type='downvote' ) as downvote_count,
            (SELECT COUNT(*) FROM Comments WHERE post_id = p.post_id) as comment_count,
            GROUP_CONCAT(t.tag_name) as tags
        FROM
            Posts p
            INNER JOIN Users u ON p.user_id = u.user_id
            LEFT JOIN Votes v ON p.post_id = v.post_id
            left JOIN PostTags pt ON p.post_id = pt.post_id
            left JOIN Tags t ON pt.tag_id = t.tag_id
        WHERE
            p.post_id = %s
        GROUP BY
            p.post_id
        ORDER BY
            p.create_date DESC
    '''

    return query, (post_id,)  # returning a tuple with the query and parameters


def get_comments(post_id):
    query = '''
    SELECT
        Comments.comment_id as comment_id,
        Comments.text AS Comment_Text,
        Comments.user_id as user_id,
        Users.display_name AS Commenter_Name,
        Comments.create_date AS Comment_DateTime,
        (select count(*) from CommentScore where Comments.comment_id = CommentScore.comment_id )  AS Comment_Score
    
    FROM
        Comments
    JOIN
        Users ON Comments.user_id = Users.user_id
    LEFT JOIN
        CommentScore ON Comments.comment_id = CommentScore.comment_id
    WHERE
        Comments.post_id = %s
    GROUP BY
        Comments.comment_id
    ORDER BY
        Comment_DateTime DESC
    '''
    return query, (post_id,)


def get_category():
    return '''SELECT
    category as name,
    COUNT(post_id) AS post_count
FROM
    Posts
GROUP BY
    category;
'''


def get_user_by_username(username):
    return "SELECT * FROM Users WHERE username = %s"


def insert_user(username, email, password, display_name, about_me, role, Gravatar_url):
    return """
    INSERT INTO Users (username, email, password_hash, display_name, about_me, role, Gravatar_url, creation_date)
    VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
    """
# Upvote query


def upvote_post(post_id, username):
    upvote_query = """
        INSERT INTO Votes (post_id, user_id, vote_type, create_date)
        VALUES (%s, (SELECT user_id FROM Users WHERE username = %s), 'upvote', CURRENT_TIMESTAMP)
        ON DUPLICATE KEY UPDATE vote_type = 'upvote', create_date = CURRENT_TIMESTAMP
    """

    return upvote_query, (post_id, username)

# Downvote query


def downvote_post(post_id, username):
    downvote_query = """
        INSERT INTO Votes (post_id, user_id, vote_type, create_date)
        VALUES (%s, (SELECT user_id FROM Users WHERE username = %s), 'downvote', CURRENT_TIMESTAMP)
        ON DUPLICATE KEY UPDATE vote_type = 'downvote', create_date = CURRENT_TIMESTAMP
    """

    return downvote_query, (post_id, username)
# queries.py


def get_user_info(user_id):
    return f"""
    SELECT user_id, username, email, display_name,about_me,role
    FROM Users
    WHERE user_id = {user_id}
    """


def get_user_posts(user_id):
    return f"""
    	SELECT 
		p.post_id, 
		p.title as title, 
		p.body as body, 
		p.create_date as create_date,
		
        (SELECT COUNT(*) FROM Votes WHERE post_id = p.post_id AND vote_type = 'upvote') as upvote_count,
		(SELECT COUNT(*) FROM Votes WHERE post_id = p.post_id AND vote_type = 'downvote') as downvote_count,
		(SELECT COUNT(*) FROM Comments WHERE post_id = p.post_id) as comment_count
	FROM 
		Posts p
	JOIN 
		Users u ON p.user_id = u.user_id
	WHERE 
		u.user_id = {user_id}
	ORDER BY 
		p.create_date DESC;
    """


def get_author_posts(username):
    return """
        SELECT 
            p.post_id, 
            p.title as title, 
            p.body as body, 
            p.create_date as create_date,
            (SELECT COUNT(*) FROM Votes WHERE post_id = p.post_id AND vote_type = 'upvote') as upvote_count,
            (SELECT COUNT(*) FROM Votes WHERE post_id = p.post_id AND vote_type = 'downvote') as downvote_count,
            (SELECT COUNT(*) FROM Comments WHERE post_id = p.post_id) as comment_count
        FROM 
            Posts p
        JOIN 
            Users u ON p.user_id = u.user_id
        WHERE 
            u.username = %s
        ORDER BY 
            p.create_date DESC;
    """


def get_author_info(username):
    return """
        SELECT user_id, username, email, display_name, about_me, role
        FROM Users
        WHERE username = %s
    """
