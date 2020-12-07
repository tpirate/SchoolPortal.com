# Imports
from flask import Flask, render_template, session, redirect, request, flash, url_for, abort
from flask_session import Session
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from cs50 import SQL
import os
import markdown
from time import sleep

from new import login_required

# App Config
app = Flask(__name__)
db = SQL("sqlite:///school.db")
app.debug = True
app.secret_key = b'\xb3\xaaS\xdf\xc0\x1fBc\x9b\x84\x9a\xfaCd\xc3\xd9'

app.static_folder = 'static'
app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Session Config
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
app.config.from_object(__name__)



# Routes
@app.route('/')
def index():
    if session.get("id"):
        return redirect(url_for('home'))
    return  render_template("index.html")

@app.route('/account')
@login_required
def account():
    user = db.execute("SELECT * FROM users WHERE id = :id", id=session['id'])[0]
    return render_template('account.html', user=user)

@app.route('/changemail', methods=['GET', 'POST'])
@login_required
def mailc():
    if request.method == 'POST':
        if not request.form.get('mail'):
            flash(u'Please fill every credentials.', 'sorry')
            return redirect(request.url)
        rows2 = db.execute("SELECT * FROM users WHERE mail = :schoolname", schoolname=request.form.get('mail').lower())
        if len(rows2) != 0: 
            flash(u'This mail is already registered.', 'sorry')
            return redirect(request.url)
        db.execute('UPDATE users SET mail = :mail WHERE id = :id', mail=request.form.get('mail'), id=session['id'])
        return redirect(url_for('home'))
    else:
        return render_template('mail.html')

@app.route('/changepass', methods=['GET', 'POST'])
@login_required
def passc():
    if request.method == 'POST':
        if not request.form.get('password'):
            flash(u'Please fill every credentials.', 'sorry')
            return redirect(request.url)
        if request.form.get("password") != request.form.get("confirmation"):
            flash(u'Passwords do not match.', 'sorry')
            return redirect(request.url)
        db.execute('UPDATE users SET hash = :passw WHERE id = :id', passw=generate_password_hash(request.form.get('password')), id=session['id'])
        return redirect(url_for('home'))
    else:
        return render_template('pass.html')

@app.route('/changename', methods=['GET', 'POST'])
@login_required
def namec():
    if request.method == 'POST':
        if not request.form.get('username'):
            flash(u'Please fill every credentials.', 'sorry')
            return redirect(request.url)
        rows = db.execute("SELECT * FROM users WHERE schoolname = :schoolname", schoolname=request.form.get('username').lower())
        if len(rows) != 0: 
            flash(u'This school name is already registered.', 'sorry')
            return redirect(request.url)
        db.execute('UPDATE users SET schoolname = :name WHERE id = :id', name=request.form.get('username'), id=session['id'])
        return redirect(url_for('home'))
    else:
        return render_template('name.html')

@app.route('/home')
@login_required
def home():
    sites = db.execute("SELECT * FROM sites WHERE user_id = :id", id=session['id'])
    user = db.execute("SELECT * FROM users WHERE id = :id", id=session['id'])[0]
    return render_template('home.html', sites=sites, user=user)

@app.route('/page/<urlheader>')
def pages(urlheader):
    if len(db.execute("SELECT * FROM sites WHERE header = :header", header=urlheader)) == 0:
        abort(404)
    else:
        sites = db.execute("SELECT * FROM sites WHERE header = :header", header=urlheader)
        file = open('templates/temp.html', 'w')
        file.write(sites[0]['content'])
        sleep(0.1)
        file.close()
        return render_template('pages.html')

@app.route('/pages', methods=['GET', 'POST'])
@login_required
def page():
    sites = db.execute("SELECT * FROM sites WHERE user_id = :id", id=session['id'])
    return render_template('page.html', sites=sites)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get("id"):
        return redirect(url_for('home'))
    if request.method == 'POST':
        if not request.form.get("username") or not request.form.get("password"):
            flash(u'Please fill every credentials.', 'sorry')
            return redirect(request.url)
        rows = db.execute("SELECT * FROM users WHERE schoolname = :schoolname", schoolname=request.form.get('username').lower())
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get('password')):
            flash(u'Invalid username and/or password.', 'sorry')
            return redirect(request.url)
        session['id'] = rows[0]['id']
        flash(u'Logged In!', 'okay')
        return redirect(url_for('home'))
    else:
        return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if session.get("id"):
        return redirect(url_for('home'))
    if request.method == 'POST':
        # Ensure username was submitted
        if not request.form.get("username") or not request.form.get("password") or not request.form.get("mail"):
            flash(u'Please fill every credentials.', 'sorry')
            return redirect(request.url)
        if request.form.get("password") != request.form.get("confirmation"):
            flash(u'Passwords do not match.', 'sorry')
            return redirect(request.url)
        rows = db.execute("SELECT * FROM users WHERE schoolname = :schoolname", schoolname=request.form.get('username').lower())
        rows2 = db.execute("SELECT * FROM users WHERE mail = :schoolname", schoolname=request.form.get('mail').lower())
        if len(rows) != 0:
            flash(u'This school name is already taken.', 'sorry')
            return redirect(request.url)
        if len(rows2) != 0: 
            flash(u'This mail is already registered.', 'sorry')
            return redirect(request.url)
        # Ensure password was submitted
        db.execute("INSERT INTO users (schoolname, mail, hash) VALUES (:name, :mail, :hash)", name=request.form.get("username").lower(), mail=request.form.get("mail").lower() , hash=generate_password_hash(request.form.get("password")))
        rows = db.execute("SELECT * FROM users WHERE schoolname = :schoolname", schoolname=request.form.get('username').lower())
        session["user_id"] = rows[0]["id"]
        # Redirect user to home page
        os.mkdir('dirs\\' + str(session["user_id"]))
        flash(u"Registered!", 'okay')
        return redirect(url_for('login'))
    else:
        return render_template("register.html")


@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/learnmore')
def learnmore():
    return render_template('learn.html')

@app.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    if request.method == 'POST':
        if not request.form.get('header') or not request.form.get('desc') or not request.form.get('content'):
            flash('Please fill everything.', 'sorry')
            return redirect(url_for('new'))
        if len(db.execute("SELECT * FROM sites WHERE header = :header", header=request.form.get('header').lower())) != 0:
            flash('Header already exists.', 'sorry')
            return redirect(url_for('new'))

        db.execute("INSERT INTO sites (header, desc, content, user_id) VALUES (:header, :desc, :content, :id)", header=request.form.get('header'), desc=request.form.get('desc'), content=markdown.markdown(request.form.get('content')), id=session['id'])
        flash(u'Created!', 'okay')
        return redirect(url_for('home'))
    else:
        return render_template('new.html')


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html')



if __name__ == "__main__":
    app.run(debug=True)
