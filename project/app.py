"""Main file for website program

Defines routing and performs backend functions for the website to host.

Part of master thesis: Entwicklung eines vernetzten Prüftands zur web-basierten
                       Validierung und Parametrierung von Simulationsmodellen
"""

# built-in modules
import os
import sys

# third party
from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
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
@app.route('/')
def index():
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


# webcam stream
@app.route('/webcam')
@is_logged_in
def webcam():

    # <!-- <img src="{{ url_for('video_feed') }}"> -->

    return render_template('webcam.html')


@app.route('/testseite')
def testseite():

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM queue")
    entries = cur.fetchall()  # fetch in dictionary form

    xdata = [1, 2, 3, 4, 5]
    ydata = [1, 2, 10, 12, 16]

    return render_template('testseite.html', entries=entries, xdata=xdata, ydata=ydata)


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
    email = StringField('EMail', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')


# User register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
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

        flash('You are now registered and can log in', 'success')

        return redirect(url_for('login'))

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

                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            # Close connection
            cur.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')


# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))


# TODO Funktion für laden eines Plots schreiben

# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    cur = mysql.connection.cursor()  # creates database cursor

    # Get file entries from database
    # TODO select all from files wher user is session['username']
    result = cur.execute("SELECT * FROM files")
    files = cur.fetchall()  # fetches in dictionary form

    voltage_curve = 'USB6009-Messung.png'  # TODO ID o.ä übergeben

    # für plot: IDs die aktuell in DB sind anzeigen lassen
    # ID an render_template übergeben damit die richtigen plots angezeigt werden können

    # remove id from filename for presentation on dashboard
    for i in range(len(files)):
        name = files[i]['name']
        name = name.split('-', 1)[1]  # split(seperator, maxsplit)[element]
        files[i]['name'] = name

    # for i in range(len(files)):
    #     print(files[i])

    if result > 0:  # if there are rows
        return render_template('dashboard.html', files=files, Spannungsverlauf=voltage_curve)

    else:
        msg = 'Keine Dateien vorhanden'
        return render_template('dashboard.html', msg=msg)

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

# TODO Modal hinzufügen und nachfragen, ob wirklich gelöscht werden soll
# erst wenn ein Button im Modal bestätigt wird die Daten löschen
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


def plot_voltage(filename_saved):
    # TODO filename_web ersetzten und nach ID suchen
    filename_web = filename_saved
    mypath = os.listdir('uploads')
    for i in range(0, len(mypath)):
        if filename_web == mypath[i]:
            filename = mypath[i]

    # Datei auslesen:
    print("Folgende Datei wird geöffnet: ", filename)
    with open(filename, "r") as f:
        buffer_textfile = f.read().splitlines()
        f.close()

    data_AO = [float(i) for i in buffer_textfile]  # Konvertierung in float
    plt.title('Spannung Vorgabe')
    # TODO Zeit zum plot hinzufügen
    # TODO plot so erstellen, sodass Verlauf bei kleinem Plot gut erkennbar (z.B. Linewidth dicker)
    plt.plot(data_AO)
    plt.xlabel('Zeit in s')
    plt.ylabel('Spannung in V')
    plt.grid(True)
    plt.savefig("static/plots/Spannungsvorgabe.png", bbox_inches='tight')


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

            # TODO Create plot here or at dashboard site with plotly dash or some other visualization tool
            # plot_voltage(filename)

            # write data to database:
            # Create cursor
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

            cur.execute("INSERT INTO files(name, username) VALUES(%s, %s)",
                        (filename, session['username']))

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

    # TODO Button auf dashboard nun für die entsprechende Zeile entfernen/aendern
    #  -> evtl in dashboard() queue database auch auslesen
    #  3. table mit tests die durchgefuert wurden?
    #  -> Oder in files neues feld mit status (status kann sein: waiting, in queue, done oder aehnlich)
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

    return redirect('/dashboard')


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
    # app.run()
