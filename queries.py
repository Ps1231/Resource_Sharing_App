def all_posts(limit=None, offset=None):
    query = '''SELECT
    p.post_id,
    u.gravatar_url as user_image,
    u.display_name as display_name,
    p.title as post_title,
    p.body AS post_content,
    p.category as category,
    p.create_date as create_date,
    COUNT(v.vote_type = 'upvote') as upvote_count,
    COUNT(v.vote_type = 'downvote') as downvote_count,
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


def search_posts(search_query, limit=None, offset=None):
    query = '''
        SELECT
            u.gravatar_url as user_image,
            u.display_name as display_name,
            p.title as post_title,
            p.body AS post_content,
            p.category as category,
            p.create_date as create_date,
            COUNT(CASE WHEN v.vote_type = 'upvote' THEN 1 END) as upvote_count,
            COUNT(CASE WHEN v.vote_type = 'downvote' THEN 1 END) as downvote_count,
            (SELECT COUNT(*) FROM Comments WHERE post_id = p.post_id) as comment_count,
            GROUP_CONCAT(t.tag_name) as tags
        FROM
            Posts p
            INNER JOIN Users u ON p.user_id = u.user_id
            LEFT JOIN Votes v ON p.post_id = v.post_id
            INNER JOIN PostTags pt ON p.post_id = pt.post_id
            INNER JOIN Tags t ON pt.tag_id = t.tag_id
        WHERE
            p.title LIKE %s
        GROUP BY
            p.post_id
        ORDER BY
            p.create_date DESC
    '''

    search_query_param = f"%{search_query}%"

    if limit is not None:
        query += f" LIMIT {limit}"
    if offset is not None:
        query += f" OFFSET {offset}"

    return query, (search_query_param,)


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


def recent_posts():
    return '''SELECT post_id  , title, DATE_FORMAT(create_date, '%e %b %Y') AS date
              FROM Posts ORDER BY create_date DESC LIMIT 5;'''

# queries.py


def get_post_details(post_id):
    query = '''
        SELECT
            p.post_id,
            u.gravatar_url as user_image,
            u.about_me as about,
            u.role,
            u.display_name as display_name,
            p.title as post_title,
            p.body AS post_content,
            p.category as category,
            p.create_date as create_date,
            COUNT(v.vote_type = 'upvote') as upvote_count,
            COUNT(v.vote_type = 'downvote') as downvote_count,
            (SELECT COUNT(*) FROM Comments WHERE post_id = p.post_id) as comment_count,
            GROUP_CONCAT(t.tag_name) as tags
        FROM
            Posts p
            INNER JOIN Users u ON p.user_id = u.user_id
            LEFT JOIN Votes v ON p.post_id = v.post_id
            INNER JOIN PostTags pt ON p.post_id = pt.post_id
            INNER JOIN Tags t ON pt.tag_id = t.tag_id
        WHERE
            p.post_id = %s
        GROUP BY
            p.post_id
        ORDER BY
            p.create_date DESC
    '''

    return query, (post_id,)  # returning a tuple with the query and parameters


def get_comments(post_id):
    query = '''SELECT
        Comments.text AS Comment_Text,
        Users.display_name AS Commenter_Name,
        Comments.create_date AS Comment_DateTime
    FROM
        Comments
    JOIN
        Users ON Comments.user_id = Users.user_id
    WHERE
        Comments.post_id = %s '''
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
