from flask import Flask
from sqlalchemy import Column, Integer, String, Text, Enum, TIMESTAMP, ForeignKey, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import datetime
from flask_sqlalchemy import SQLAlchemy
Base = declarative_base()


class Users(Base):
    __tablename__ = 'Users'

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255))
    display_name = Column(String(255))
    creation_date = Column(TIMESTAMP, default=datetime.utcnow)

    about_me = Column(Text)
    City = Column(String(100), nullable=False)
    State = Column(String(100), nullable=False)
    Country = Column(String(100), nullable=False)
    Gravatar_url = Column(String(255))

    role = Column(Enum('Admin', 'Moderator', 'Regular User'), nullable=False)


class Posts(Base):
    __tablename__ = 'Posts'

    post_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('Users.user_id'))
    title = Column(String(255))
    body = Column(Text)
    create_date = Column(TIMESTAMP)
    last_edit_date = Column(TIMESTAMP)
    last_activity_date = Column(TIMESTAMP)
    deletion_date = Column(TIMESTAMP)
    category = Column(Enum('Class Notes & Study Materials', 'Textbooks & References',
                      'Internship & Job Opportunities', 'Events & Hackathons', 'Study Groups & Tutoring'))

    user = relationship('Users', back_populates='posts')
    comments = relationship('Comments', back_populates='post')


class Comments(Base):
    __tablename__ = 'Comments'

    comment_id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey('Posts.post_id'))
    user_id = Column(Integer, ForeignKey('Users.user_id'))
    text = Column(Text)
    create_date = Column(TIMESTAMP)

    post = relationship('Posts', back_populates='comments')
    user = relationship('Users', back_populates='comments')
    scores = relationship('CommentScore', back_populates='comment')


class Votes(Base):
    __tablename__ = 'Votes'

    vote_id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey('Posts.post_id'))
    user_id = Column(Integer, ForeignKey('Users.user_id'))
    vote_type = Column(Enum('upvote', 'downvote'))
    create_date = Column(TIMESTAMP)

    post = relationship('Posts', back_populates='votes')
    user = relationship('Users', back_populates='votes')


class Tags(Base):
    __tablename__ = 'Tags'

    tag_id = Column(Integer, primary_key=True, autoincrement=True)
    tag_name = Column(String(8), unique=True)


class PostTags(Base):
    __tablename__ = 'PostTags'
    __table_args__ = (
        UniqueConstraint('tag_id', 'post_id', name='uq_tag_post'),
    )

    tag_id = Column(Integer, ForeignKey('Tags.tag_id'), primary_key=True)
    post_id = Column(Integer, ForeignKey('Posts.post_id'), primary_key=True)

    tag = relationship('Tags', back_populates='post_tags')
    post = relationship('Posts', back_populates='post_tags')


class ReportedContent(Base):
    __tablename__ = 'ReportedContent'

    report_id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey('Posts.post_id'))
    reporter_user_id = Column(Integer, ForeignKey('Users.user_id'))
    report_Type = Column(
        Enum('Off Topic', 'Content Dispute', 'Risky / Unsafe Lnks', 'Others'))

    post = relationship('Posts', back_populates='reports')
    reporter_user = relationship('Users', back_populates='reports')


class CommentScore(Base):
    __tablename__ = 'CommentScore'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('Users.user_id'))
    comment_id = Column(Integer, ForeignKey('Comments.comment_id'))
    voted = Column(Enum('true', 'false'))

    user = relationship('Users', back_populates='comment_scores')
    comment = relationship('Comments', back_populates='scores')


# Define relationships between tables
Users.posts = relationship('Posts', back_populates='user')
Users.comments = relationship('Comments', back_populates='user')
Posts.comments = relationship('Comments', back_populates='post')
Posts.votes = relationship('Votes', back_populates='post')
Posts.tags = relationship('PostTags', back_populates='post')
Posts.reports = relationship('ReportedContent', back_populates='post')
Comments.scores = relationship('CommentScore', back_populates='comment')
Tags.post_tags = relationship('PostTags', back_populates='tag')

# Add any other models and relationships as needed
