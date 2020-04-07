"""Main file for website program

Defines routing and performs backend functions for the website to host.

Part of master thesis: Entwicklung eines vernetzten Prüftands zur web-basierten
                       Validierung und Parametrierung von Simulationsmodellen
"""

# built-in modules
import os
import sys

# third party
from flask import Flask, render_template, flash, redirect, url_for, session, request, logging, Response
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
from werkzeug.utils import secure_filename

# local modules
if 'pytest' in sys.modules:
    from Website.project import app_helpers as apph  # for pytest
else:
    import app_helpers as apph  # for Apache Server

# import matplotlib.pyplot as plt  # does not work with Apache Server currently

# TODO funktionen in externe datei schreiben und importieren (code uebersichtlicher machen)


app = Flask(__name__)

app.secret_key = b'secret123'

apph.init_db(app)
mysql = MySQL(app)  # init MySQL

# render_template: brings in the template, to create a page
# redirect : page already there, just want to point to that page

# Index
@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']

        cur = mysql.connection.cursor()
        result = cur.execute(
            "SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['password']

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['username'] = username

                flash('Login erfolgreich', 'success')

                cur.close()
                return redirect(url_for('dashboard'))
            else:
                error = 'Passwort inkorrekt'

                cur.close()
                return render_template('home.html', error=error)
        else:
            error = 'Benutzername nicht gefunden'

            cur.close()
            return render_template('home.html', error=error)
    return render_template('home.html')

# About
@app.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('about.html')

# Nutzung
@app.route('/nutzung-pruefstand')
def nutzung():

    # Create Cursor
    # cur = mysql.connection.cursor()
    # Get articles
    # result = cur.execute("SELECT * FROM articles")
    # articles = cur.fetchall()  # fetch in dictionary form
    # if result > 0:  # if there are rows
    #     return render_template('articles.html', articles=articles)
    # else:
    #     msg = 'No Articles Found'
    #     return render_template('articles.html', msg=msg)
    # Close connection
    # cur.close()

    return render_template('nutzung.html')


# Check if user is logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap


@app.route('/testseite')
def testseite():

    return render_template('testseite.html')


# Single Article
@app.route('/article/<string:id>/')  # id: dynamic value
def article(id):
    # Create Cursor
    cur = mysql.connection.cursor()

    # Get article
    result = cur.execute("SELECT * FROM articles WHERE id = %s", [id])

    article = cur.fetchone()  # fetch in dictionary form

    return render_template('article.html', article=article)


# Register Form Class
class RegisterForm(Form):
    # name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=3, max=25)])
    email = StringField('E-Mail', [validators.Length(min=6, max=50)])
    password = PasswordField('Passwort', [
        validators.DataRequired(),
        validators.EqualTo(
            'confirm', message='Passwörter stimmen nicht überein')
    ])
    confirm = PasswordField('Passwort bestätigen')


# User register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    cur.close()

    # check if user already exists
    result = next(
        (item for item in users if item['username'] == str(form.username.data)), None)

    if result == None:
        if request.method == 'POST' and form.validate():

            # handle submission:
            # name = form.name.data
            email = form.email.data
            username = form.username.data
            password = sha256_crypt.encrypt(str(form.password.data))

            # Create cursor
            cur = mysql.connection.cursor()

            cur.execute("INSERT INTO users(email, username, password) VALUES(%s, %s, %s)",
                        (email, username, password))

            # Commit to db
            mysql.connection.commit()

            # Close conneciton
            cur.close()

            flash('Registrierung erfolgreich. Sie können sich nun einloggen.', 'success')

            return redirect(url_for('login'))
    else:
        # username already registered
        flash('Dieser Benutzername ist bereits vergeben und kann nicht verwendet werden.', 'danger')

    return render_template('register.html', form=form)

# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']

        # Create Cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute(
            "SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['password']

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # app.logger.info('PASSWORD MATCHED')  # log to console
                # Passed
                session['logged_in'] = True
                session['username'] = username

                flash('Login erfolgreich', 'success')

                cur.close()
                return redirect(url_for('dashboard'))
            else:
                error = 'Passwort inkorrekt'

                cur.close()
                return render_template('login.html', error=error)
            # Close connection
            # cur.close()
        else:
            error = 'Benutzername nicht gefunden'

            cur.close()
            return render_template('login.html', error=error)

    return render_template('login.html')


# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('Logout erfolgreich', 'success')
    return redirect(url_for('login'))


# TODO Funktion für laden eines Plots schreiben

# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():

    # get data from database
    cur = mysql.connection.cursor()  # creates database cursor
    cur.execute("SELECT * FROM files WHERE username = %s",
                [session['username']])
    files = cur.fetchall()  # fetches in dictionary form
    cur.close()

    # get data for files
    for i in range(len(files)):
        # user voltage specifications
        path = apph.UPLOAD_FOLDER + '/' + files[i]['name']
        # TODO hier wieder anpassen, wenn Datien normal schon in csv sind
        path = path[72:-3]
        path = path + 'csv'
        # print(path)
        files[i]['path'] = path

        # result files with data from measurement
        if files[i]['status'] == 'executed':
            # path = apph.RESULTS_FOLDER + '/' + 'results-' + files[i]['name']
            path = files[i]['name']
            path = path[0:-3]
            path = 'results/' + 'results-' + path + 'csv'
            # print(path)
            files[i]['result_path'] = path

        # remove id from filename for presentation on dashboard
        name = files[i]['name']
        name = name.split('-', 1)[1]  # split(seperator, maxsplit)[element]
        files[i]['name'] = name
        files[i]['index'] = str(i)

    if len(files) > 0:  # if there are rows
        return render_template('dashboard.html', files=files)

    else:
        msg = 'Keine Dateien vorhanden'
        return render_template('dashboard.html', no_files=msg)

    # Close connection
    cur.close()

    return render_template('dashboard.html')


# Article Form Class
class ArticleForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=200)])
    body = TextAreaField('Body', [validators.Length(min=30)])

# Add Article
@app.route('/add_article', methods=['GET', 'POST'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data

        # Create Cursor
        cur = mysql.connection.cursor()

        # Execute
        cur.execute("INSERT INTO articles(title, body, author) VALUES(%s, %s, %s)",
                    (title, body, session['username']))

        # Commit
        mysql.connection.commit()

        # Close conneciton
        cur.close()

        flash('Article Created', 'success')

        return redirect(url_for('dashboard'))

    return render_template('add_article.html', form=form)

# Edit Article
# TODO _ durch - ersetzen und gucken ob Zugriff funktionniert und wie es im Browser angezeigt wird
@app.route('/edit_article/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_article(id):
    # Create Cursor
    cur = mysql.connection.cursor()

    # Get article by id
    result = cur.execute("SELECT * FROM articles WHERE id = %s", [id])

    article = cur.fetchone()

    # Get form
    form = ArticleForm(request.form)

    # Populate article from fields
    form.title.data = article['title']  # article was fetched from database
    form.body.data = article['body']

    if request.method == 'POST' and form.validate():
        title = request.form['title']
        body = request.form['body']

        # Create Cursor
        cur = mysql.connection.cursor()

        # Execute
        cur.execute(
            "UPDATE articles SET title=%s, body=%s WHERE id = %s", (title, body, id))

        # Commit
        mysql.connection.commit()

        # Close conneciton
        cur.close()

        flash('Article Updated', 'success')

        return redirect(url_for('dashboard'))

    return render_template('edit_article.html', form=form)

# Delete entry - only entry in database is deleted, not the file in 'uploads' folder
@app.route('/delete_entry/<string:id>', methods=['POST'])
@is_logged_in
def delete_entry(id):
    # Create Cursor
    cur = mysql.connection.cursor()

    # Execute
    cur.execute("DELETE FROM files WHERE id = %s", [id])

    # Commit to db
    mysql.connection.commit()

    # Close connection
    cur.close()

    flash('Eintrag gelöscht', 'success')

    return redirect(url_for('dashboard'))


ALLOWED_EXTENSIONS = {'txt'}
app.config['UPLOAD_FOLDER'] = apph.UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024    # 16 MB
# TODO Textausgabe (Warnung) für größere Dateien als hier spezifiziert hinzufügen
# -> aktuell "bricht" Seite zusammen


def allowed_filename(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Datei hochladen und in Ordner speichern
@app.route('/dashboard', methods=['GET', 'POST'])
@is_logged_in
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(url_for('dashboard'))

        file = request.files['file']

        if file.filename == '':
            flash('Keine Datei ausgewählt', 'danger')
            return redirect(url_for('dashboard'))

        if file and allowed_filename(file.filename):
            filename = secure_filename(file.filename)

            # write data to database:
            cur = mysql.connection.cursor()

            # get last entry in db
            cur.execute("SELECT * FROM files ORDER BY id DESC LIMIT 1")
            last_row_db = cur.fetchone()
            print("result.id = {}" .format(last_row_db['id']))

            # Add id and hyphen to beginning of filename for clear allocation
            filename = str(last_row_db['id']+1) + '-' + filename

            # TODO User-ID auch mit in Tabelle scheiben für eindeutige Zuordnung
            # TODO überprüfen ob die Lösung optimal ist. Wenn Dateien aus Ordner gelöscht werden, sind
            # die Daten in der Datenbank nicht mehr aktuell!

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('Datei erfolgreich hochgeladen', 'success')

            cur.execute("INSERT INTO files(name, username, status) VALUES(%s, %s, %s)",
                        (filename, session['username'], 'uploaded'))

            # Commit to db
            mysql.connection.commit()

            # Close conneciton
            cur.close()

            return redirect(url_for('dashboard'))
        else:
            flash('Bitte korrektes Dateiformat hochalden (.txt-Datei)', 'danger')
            return redirect(url_for('dashboard'))


@app.route('/start_measurement/<int:id>', methods=['POST'])
@is_logged_in
def start_measurement(id):
    """Writes data about measurement in queue table"""

    print("Test mit folgender ID wird der Warteschlange hinzufgefügt, ID: {}" .format(id))

    # /C - Carries out the command specified by string and then terminates
    # /K - Carries out the command specified by string but remains
    # os.system("start cmd /K python project/start_measurement.py")

    # TODO evtl. weitere Informationen uebergeben wie z.B. Testdauer (aus Vorgabe bestimmt)

    # get filename from files table
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM files WHERE id = %s", [id])
    file = cur.fetchone()
    filename = file['name']

    # save file to queue table
    cur = mysql.connection.cursor()
    # %s is a placeholder, not a formatter in this case
    cur.execute("INSERT INTO queue(id, filename) VALUES(%s, %s)",
                (id, filename))
    mysql.connection.commit()
    cur.close()

    # update status
    cur = mysql.connection.cursor()
    cur.execute("UPDATE files SET status = 'in_queue' WHERE id = %s", [id])
    mysql.connection.commit()
    cur.close()

    return redirect('/dashboard')


# webcam stream
@app.route('/webcam')
@is_logged_in
def webcam():
    # <!-- <img src="{{ url_for('video_feed') }}"> -->

    return render_template('webcam.html')


def generate(camera):
    """Generate the data for video stream."""

    while True:
        frame = camera.get_frame()

        # each yield expression is directly sent to the browser
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Route used by html to access video"""

    return Response(generate(apph.Camera()), mimetype='multipart/x-mixed-replace; boundary=frame')


def mdt_user(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        # if 'logged_in' in session:
        if session['username'] == 'mdt':
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login as mdt', 'danger')
            return redirect(url_for('login'))
    return wrap


# Page for settings administered through chair of mdt
@app.route('/mdt-settings', methods=['GET', 'POST'])
@is_logged_in
@mdt_user
def mdt_settings():

    # get queue entries
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM queue")
    entries = cur.fetchall()  # fetch in dictionary form

    # get access-log entries
    buffer_accesslog = apph.read_txt_by_lines(apph.accesslog)
    buffer_accesslog.reverse()

    # get error-log entries
    buffer_errorlog = apph.read_txt_by_lines(apph.errorlog)
    buffer_errorlog.reverse()

    return render_template('mdt-settings.html',
                           entries=entries,
                           accesslog=buffer_accesslog[:20],
                           errorlog=buffer_errorlog[:20])


if __name__ == '__main__':
    app.run(debug=True, port=80)  # damit man app nicht immer neu starten muss
    # TODO ipv4 adresse automatisch herausfinden und hier einfügen
    # app.run(host='192.168.1.12')  # Wohnung
    # app.run(host='141.23.138.2')  # TU-Berlin
    # app.run(threaded=True)
    # app.run()
