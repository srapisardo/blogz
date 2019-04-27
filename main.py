from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:launchcode@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'sjr719cpnohis'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'blog', 'index', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/blog', methods=['GET', 'POST'])
def blog():
    posts = Blog.query.all()

    if "id" in request.args:
        id = request.args.get('id')
        post = Blog.query.get(id)
        
        return render_template('blogpost.html', post=post)

    if "user" in request.args:
        owner_id = request.args.get('user')
        userEntries = Blog.query.filter_by(owner_id=owner_id)
        username = User.query.get(owner_id)

        return render_template('singleUser.html', user=username)

    return render_template('blog.html', posts=posts)

@app.route('/login', methods=['POST', 'GET'])
def login():
    username_error = ""
    password_error = ""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            return redirect('/newpost')
        if not user:
            return render_template('login.html', username_error="Username does not exist.")
        else:
            return render_template('login.html', password_error="Your username or password was incorrect.")

    return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    username_error = ''
    password_error = ''
    verify_error = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()
        
        if existing_user:
            username_error = "Username already exist." 
        
        if username == "":
            username_error = "Invalid username"
        elif len(username) < 3:
            username = ''
            username_error = "Invalid username"
        elif " " in username: 
            username = ''
            username_error = "Invalid username"

        if password == "":
            password_error = "Invalid password" 
        elif len(password) < 3:
            password = ""
            password_error = "Invalid password"
        elif " " in password:
            password = ""
            password_error = "Invalid password"

        if verify != password:
            password = ""
            verify = ""
            verify_error = "Passwords do not match"
        elif verify == "":
            password = ""
            verify = ""
            verify_error = "Passwords do not match"

        if not existing_user and not username_error and not password_error and not verify_error:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')

        else:
            return render_template('signup.html', username_error=username_error, password_error=password_error, verify_error=verify_error,
            username=username, password=password, verify=verify)

    return render_template('signup.html')

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    if request.method == 'POST':
        blog_title = request.form['blog-title']
        blog_entry = request.form['blog-entry']
        owner = User.query.filter_by(username=session['username']).first()
        title_error = ''
        entry_error = ''

        if not blog_title:
            title_error = "Please input a blog title"
        if not blog_entry:
            entry_error = "Please input a blog entry"

        if not entry_error and not title_error:
            new_entry = Blog(blog_title, blog_entry, owner)     
            db.session.add(new_entry)
            db.session.commit()        
            return redirect('/blog?id={}'.format(new_entry.id)) 
        else:
            return render_template('newpost.html', title='New Entry', title_error=title_error, entry_error=entry_error, 
                blog_title=blog_title, blog_entry=blog_entry)
    
    return render_template('newpost.html', title='New Entry')


@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')


if  __name__ == "__main__":
    app.run()