from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
from flask_login import UserMixin, LoginManager, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
# from flask_ckeditor import CKEditor, CKEditorField


from datetime import datetime
from faker import Faker
import os


app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or 'default_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///twitter.db'
app.jinja_env.filters['strftime'] = datetime.strftime

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)

login_manager.login_view = u"login"

# ckeditor = CKEditor(app)

"""
    MODEL
"""

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    following = db.relationship('User', 
                               secondary='followers',
                               primaryjoin='user.c.id==followers.c.follower_id', 
                               secondaryjoin='user.c.id==followers.c.followed_id',
                               backref='follower',
    )

    tweet = db.relationship('Tweet', backref='author')
    comments = db.relationship('Comment', backref='author')


    def count_follower(self):
        return len(self.follower) 
    
    def count_following(self):
        return len(self.following)
    
    def is_followed_by(self,user_id):
        return any(user.id == user_id for user in self.follower)

    def __repr__(self) -> str:
        return f'<USER : {self.username}>'

followers = db.Table('followers',
                      db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                      db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

likes = db.Table('likes', 
                 db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                 db.Column('tweet_id', db.Integer, db.ForeignKey('tweet.id'))
)

class Tweet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String, nullable=False)
    like = db.relationship('User',
                           secondary='likes',
                           backref='liked'
    )
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    comments = db.relationship('Comment', backref='tweet')

    def count_likes(self):
        return len(self.like)
    
    def count_comments(self):
        return len(self.comments)

    def is_liked(self, user_id):
        return any(user.id == user_id for user in self.like)



class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    tweet_id = db.Column(db.Integer, db.ForeignKey('tweet.id'))

with app.app_context():
    db.create_all()

"""
    FORMS
"""

class RegisterForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    email = EmailField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField('register')

class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField('login')

class TweetForm(FlaskForm):
    # body = CKEditorField('Body')
    body = TextAreaField(validators=[DataRequired()])
    submit = SubmitField('Musk')

class CommentForm(FlaskForm):
    body = StringField("comment", validators=[DataRequired()])

    submit = SubmitField("comment")

@app.route('/')
def home():
    return render_template('index.html')

"""
    AUTHENTICATION
"""

# REGISTER
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():

        if User.query.filter_by(username=form.username.data).first() or User.query.filter_by(email=form.email.data).first():
            flash('User already exist !')
            return redirect(url_for('login'))

        user = User(
            username=form.username.data,
            email=form.email.data,
            password=generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=16)
        )

        db.session.add(user)
        db.session.commit()

        login_user(user)

        return redirect(url_for('show_all_tweet'))

    return render_template('authentication/register.html', form=form)

# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if not user:
            flash("User doesn't exist !")
            return redirect(url_for('login'))
        
        if check_password_hash(user.password, form.password.data):
            login_user(user)
            flash(f"Welcome back, {user.username}")
            return redirect(url_for('show_all_tweet'))
        
        flash('Wrong Credentials !')

    
    return render_template('authentication/login.html', form=form)

# LOGOUT
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# FORGET PASSWORD
@app.route('/forgot-password')
@login_required
def forget_password():
    return 'Yet to come !'

# SHOW USER PROFILE 
@app.route('/user/<string:username>')
def profile(username):
    user = User.query.filter_by(username=username).first()

    if user == current_user:
        return render_template('show_my_profile_page.html', user=user)

    return render_template('show_user_profile_page.html', user=user)

"""
    TWEET
"""

# ADD TWEET
@app.route('/tweet/add', methods=['GET', 'POST'])
@login_required
def add_tweet():
    form = TweetForm()

    if form.validate_on_submit():
        tweet = Tweet(
            body=form.body.data,
            author_id = current_user.id
        )

        db.session.add(tweet)
        db.session.commit()

        flash('You just musk 🎉')

        return redirect(url_for('show_all_tweet'))

    return render_template('tweet/add_tweet_page.html', form=form)

# SHOW ALL TWEET
@app.route('/musks', methods=['GET', 'POST'])
@login_required
def show_all_tweet():
    tweets = db.session.query(Tweet).order_by(Tweet.created_at.desc()).all()
    musk_form = TweetForm()

    if musk_form.validate_on_submit():
        tweet = Tweet(
            body=musk_form.body.data,
            author_id = current_user.id
        )

        db.session.add(tweet)
        db.session.commit()

        return redirect(url_for('show_all_tweet'))

    return render_template('tweet/show_all_tweet_page.html', tweets=tweets, musk_form=musk_form)

# SHOW TWEET DETAILS
@app.route('/tweet/<int:id>', methods=['GET', 'POST'])
@login_required
def show_tweet_details(id):
    tweet = db.session.get(Tweet, id)
    comment_form = CommentForm()
    return render_template('tweet/show_tweet_details_page.html', tweet=tweet, comment_form=comment_form)

# ADD LIKE
@app.route('/api/tweet/add-like', methods=['PUT'])
@login_required
def add_like():

    tweet_id = request.args.get('id')
    tweet = db.session.get(Tweet, tweet_id)
    user = db.session.get(User, current_user.id)

    new_like = likes.insert().values(user_id=user.id , tweet_id=tweet.id)
    
    db.session.execute(new_like)
    db.session.commit()

    return jsonify(success=True, message="Like added")


# REMOVE LIKE
@app.route('/api/tweet/remove-like', methods=['PUT'])
@login_required
def remove_like():

    tweet_id = request.args.get('id')
    tweet = db.session.get(Tweet, tweet_id)
    user = db.session.get(User, current_user.id)

    delete_obj = likes.delete().where(likes.c.user_id==user.id, likes.c.tweet_id==tweet.id)
    db.session.execute(delete_obj)
    db.session.commit()

    return jsonify(success=True, message="Like removed")
# FOLLOW USER
@app.route('/api/follow', methods=['PUT'])
@login_required
def follow():
    username = request.args.get('username')

    follower_id = current_user.__getattr__('id')
    followed_id = User.query.filter_by(username=username).first().id

    new_follower = followers.insert().values(follower_id=follower_id, followed_id=followed_id)
    db.session.execute(new_follower)
    db.session.commit()

    flash('You just followed a musker 🎉')
    return jsonify(success=True, message="Following user")

# UNFOLLOW USER
@app.route('/api/unfollow', methods=['PUT'])
@login_required
def unfollow():
    username = request.args.get('username')

    follower_id = current_user.__getattr__('id')
    followed_id = User.query.filter_by(username=username).first().id

    delete_obj = followers.delete().where(followers.c.follower_id==follower_id, followers.c.followed_id==followed_id)
    db.session.execute(delete_obj)
    db.session.commit()

    flash('You unfollowed a musker 💔')
    return jsonify(success=True, message="Unfloowing user")

# ADD COMMENTS
@app.route('/tweet/<int:id>/add-comment', methods=['POST'])
@login_required
def add_comment(id):
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(
            body = form.body.data,
            author_id = current_user.id,
            tweet_id = id
        )

        db.session.add(comment)
        db.session.commit()
    return redirect(f'/tweet/{id}')

# DELETE COMMENTS
@app.route('/comment/<int:id>/delete-comment')
@login_required
def delete_comment(id):
    comment = Comment.query.filter_by(id=id).first()

    if not comment.author.id == current_user.__getattr__('id'):
        return 'NOT AUTHORIZE'
    
    
    db.session.delete(comment)
    db.session.commit()

    return redirect(f'/tweet/{id}')

# DELETE TWEET
@app.route('/tweet/<int:id>/delete')
@login_required
def delete_tweet(id):
    tweet = db.session.get(Tweet, id)
    
    if current_user == tweet.author:
        db.session.delete(tweet)
        db.session.commit()
        flash('Your musk has been deleted !')
    
    return redirect(url_for('show_all_tweet'))

if __name__ == '__main__':
    app.run(debug=True)