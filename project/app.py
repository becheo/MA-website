"""Main file for website program

Defines routing and performs backend functions for the website to host.

Part of master thesis: Entwicklung eines vernetzten Prüftands zur web-basierten
                       Validierung und Parametrierung von Simulationsmodellen
"""

# built-in modules
import os
import sys
import time
import math

# third party
from flask import Flask, render_template, flash, redirect, url_for, session, request, logging, Response, jsonify
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
from werkzeug.utils import secure_filename
import threading
try:
    from thread import get_ident
except ImportError:
    from _thread import get_ident


# local modules
if 'pytest' in sys.modules:
    # for pytest
    from Website.project import app_helpers as apph
    from Website.project import config as cfg
else:
    # for Apache Server
    import app_helpers as apph
    import config as cfg

# import matplotlib.pyplot as plt  # does not work with Apache Server currently

# TODO funktionen in externe datei schreiben und importieren (code uebersichtlicher machen)


app = Flask(__name__)

# app.secret_key = b'secret123'
app.secret_key = cfg.SECRET_KEY

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
@app.route('/ueber', methods=['GET', 'POST'])
def about():
    return render_template('about.html')

# Nutzung
@app.route('/nutzung-pruefstand')
def nutzung():

    return render_template('nutzung.html')


# Check if user is logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Nicht autorisiert, Bitte einloggen', 'danger')
            return redirect(url_for('login'))
    return wrap


@app.route('/get_queue_entries', methods=['GET'])
def get_queue_entries():
    """Get entries from queue table in website database"""

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM queue")
    entries = cur.fetchall()  # fetch in tuple form
    num_of_entries = len(entries)

    id = ['-'] * cfg.queue_table_length
    filename = ['-'] * cfg.queue_table_length
    test_duration = ['-'] * cfg.queue_table_length

    for i in range(num_of_entries):
        if i == cfg.queue_table_length:
            break
        entry = entries[i]
        id[i] = entry['id']
        filename[i] = entry['filename']
        test_duration[i] = entry['test_duration']

    return jsonify(id=id,
                   filename=filename,
                   num_of_entries=num_of_entries,
                   test_duration=test_duration)


@app.route('/testseite')
def testseite():

    return render_template('testseite.html')


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
        path = path[cfg.file_pathlength:]
        files[i]['path'] = path

        # result files with data from measurement
        if files[i]['status'] == 'executed':
            # download file name in html needs to be specified in order to
            #  download a .csv file. Without specification, the file is
            # downloaded as .xls file
            path = files[i]['name']
            download_path = 'results-' + path
            path = 'results/' + 'results-' + path

            files[i]['result_path'] = path  # path for JavaScript
            files[i]['download_path'] = download_path  # path for HTML

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


# Delete entry - only entry in database is deleted, not the file in 'uploads' folder
@app.route('/delete_entry/<string:id>', methods=['POST'])
@is_logged_in
def delete_entry(id):
    # Create Cursor
    cur = mysql.connection.cursor()

    # get file name
    cur.execute("SELECT * FROM files WHERE id = %s", [id])
    file = cur.fetchone()
    filename = file['name']
    filename_result = 'results-' + filename

    file_path_upload = os.path.join(cfg.folder_upload, filename)
    file_path_result = os.path.join(cfg.folder_results, filename_result)

    # delete files in folders
    os.remove(file_path_upload)

    if file['status'] == 'executed':
        os.remove(file_path_result)

    # delete from files table
    cur.execute("DELETE FROM files WHERE id = %s", [id])

    # Commit to db
    mysql.connection.commit()

    # delete from queue table
    cur.execute("DELETE FROM queue WHERE id = %s", [id])
    mysql.connection.commit()

    # Close connection
    cur.close()

    flash('Eintrag gelöscht', 'success')

    return redirect(url_for('dashboard'))


ALLOWED_EXTENSIONS = {'csv'}
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
            flash('No file part')  # TODO auf deutsch aendern
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
            # print("result.id = {}" .format(last_row_db['id']))

            # Add id and hyphen to beginning of filename for clear allocation
            filename = str(last_row_db['id']+1) + '-' + filename

            # TODO User-ID auch mit in Tabelle scheiben für eindeutige Zuordnung
            # TODO überprüfen ob die Lösung optimal ist. Wenn Dateien aus Ordner gelöscht werden, sind
            # die Daten in der Datenbank nicht mehr aktuell!
            file_directory = os.path.join(
                app.config['UPLOAD_FOLDER'], filename)
            file.save(file_directory)
            flash('Datei erfolgreich hochgeladen', 'success')

            # get duration of uploaded test
            import pandas
            data = pandas.read_csv(file_directory)
            data_time = data['time']
            test_duration = data_time.iloc[-1]

            # save to database
            cur.execute("INSERT INTO files(name, username, status, test_duration) VALUES(%s, %s, %s, %s)",
                        (filename, session['username'], 'uploaded', test_duration))

            # Commit to db
            mysql.connection.commit()

            # Close conneciton
            cur.close()

            return redirect(url_for('dashboard'))
        else:
            flash('Bitte korrektes Dateiformat hochalden (.csv-Datei)', 'danger')
            return redirect(url_for('dashboard'))


@app.route('/start_measurement/<int:id>', methods=['POST'])
@is_logged_in
def start_measurement(id):
    """Writes data about measurement in queue table"""

    # /C - Carries out the command specified by string and then terminates
    # /K - Carries out the command specified by string but remains
    # os.system("start cmd /K python project/start_measurement.py")

    # get filename from files table
    cur = mysql.connection.cursor()

    # get files in queue table from user
    cur.execute("SELECT * FROM queue WHERE user = %s", [session['username']])
    files_user = cur.fetchall()

    # check for number of files in queue
    if len(files_user) < (cfg.max_tests_in_queue):

        # get file to start from files table
        cur.execute("SELECT * FROM files WHERE id = %s", [id])
        file = cur.fetchone()
        filename = file['name']
        test_duration = file['test_duration']

        # save file to queue table
        # %s is a placeholder in this case, not a formatter
        cur.execute("INSERT INTO queue(id, filename, test_duration, user) VALUES(%s, %s, %s, %s)",
                    (id, filename, test_duration, session['username']))

        mysql.connection.commit()

        # update status
        cur.execute("UPDATE files SET status = 'in_queue' WHERE id = %s", [id])
        mysql.connection.commit()

        # get queue files to calculate waiting time
        cur.execute('SELECT * FROM queue')
        queue_files = cur.fetchall()
        waiting_time = 0
        for queue_file in queue_files:
            waiting_time = waiting_time + float(queue_file['test_duration'])

        # add some time per test to cover time in between tests
        waiting_time = waiting_time + (len(queue_files) * 10)

        # close database connection
        cur.close()

        # convert waiting time into 'minutes:seconds' format
        waiting_minutes = math.floor(waiting_time/60)
        waiting_seconds = math.floor(waiting_time - waiting_minutes * 60)
        if waiting_seconds == 0:
            waiting_seconds = '00'

        waiting_time = str(waiting_minutes) + ':' + str(waiting_seconds)

        # show success message with accumulated waiting time
        flash('Test erfolgreich gestartet. Geschätzte Dauer bis zur Ausführung: ' +
              waiting_time + ' min', 'success')

        return redirect('/dashboard')

    else:
        # max number of allowed tests in queue reached
        max_tests = str(cfg.max_tests_in_queue)
        flash('Nur maximal ' + max_tests +
              ' Tests zur gleichen Zeit in der Warteschlange erlaubt. Bitte warten Sie die Ausführung Ihrer Tests ab.', 'danger')
        return redirect('/dashboard')


class CameraEvent(object):
    """An Event-like class that signals all active clients when a new frame is
    available.
    """

    def __init__(self):
        self.events = {}

    def wait(self):
        """Invoked from each client's thread to wait for the next frame."""

        # get unique id for current thread
        ident = get_ident()

        if ident not in self.events:
            # this is a new client
            # add an entry for it in the self.events dict
            # each entry has two elements, a threading.Event() and a timestamp
            self.events[ident] = [threading.Event(), time.time()]

        return self.events[ident][0].wait()

    def set(self):
        """Invoked by the camera thread when a new frame is available."""

        now = time.time()
        remove = None
        for ident, event in self.events.items():
            if not event[0].isSet():
                # if this client's event is not set, then set it and update the
                # last timestamp to now
                event[0].set()
                event[1] = now
            else:
                # if the client's event is already set, it means the client
                # did not process a previous frame
                # if the event stays set for more than 5 seconds, then assume
                # the client is gone and remove it
                if now - event[1] > 5:
                    remove = ident
        if remove:
            del self.events[remove]

    def clear(self):
        """Invoked from each client's thread after a frame was processed."""

        self.events[get_ident()][0].clear()


class Camera(object):
    video_source = cfg.camera_selection  # set in config file
    video_number = 1
    video_time = 0

    thread = None  # background thread that reads frames from camera
    frame = None  # current frame is stored here by background thread
    last_access = 0  # time of last client access to the camera
    event = CameraEvent()
    image_brightness = 0

    def __init__(self):
        """Start the background camera thread if it isn't running yet."""

        # self.camera = cv2.VideoCapture(Camera.video_source)
        # # save img to vieo file
        # frame_width = int(self.camera.get(3))
        # frame_height = int(self.camera.get(4))

        # self.out = cv2.VideoWriter('CameraOutput.avi', cv2.VideoWriter_fourcc(
        #     'M', 'J', 'P', 'G'), 30, (frame_width, frame_height))

        if Camera.thread is None:
            Camera.last_access = time.time()
            Camera.video_time = time.time()

            # start background frame thread
            Camera.thread = threading.Thread(target=self._thread)
            Camera.thread.start()

            # wait until frames are available
            while self.get_frame() is None:
                time.sleep(0)

    @staticmethod
    def frames():
        import cv2
        import numpy as np

        # It is crucial that the import statement for the cv2 module is
        # located inside this function. Otherwise the Apache server will not
        # be able to start and serve the webpage

        camera = cv2.VideoCapture(Camera.video_source)

        if cfg.save_camera_to_file == True:

            # save img to vieo file
            frame_width = int(camera.get(3))
            frame_height = int(camera.get(4))

            # configure saving images as video to file
            video_name = cfg.folder_camera_recording + \
                'CameraOutput_' + str(Camera.video_number) + '.mp4'

            # out = cv2.VideoWriter(video_name,
            #                       cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'),
            #                       30, (frame_width, frame_height))
            # out = cv2.VideoWriter(video_name,
            #                       cv2.VideoWriter_fourcc(*'mp4v'),
            #                       30, (frame_width, frame_height))
            out = cv2.VideoWriter(video_name,
                                  cv2.VideoWriter_fourcc(*'avc1'),
                                  30, (frame_width, frame_height))

        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')

        while True:
            # read current frame
            _, img = camera.read()

            if time.time() - Camera.image_brightness > 10:
                Camera.image_brightness = time.time()
                histogram = cv2.calcHist([img], [0], None, [256], [0, 256])
                brightness = np.ndarray.mean(img.ravel())

                # create app context manually to be able to access database
                with app.app_context():
                    cur = mysql.connection.cursor()

                    if brightness < 25:
                        cur.execute(
                            "UPDATE status SET status = 'on' WHERE name = 'illumination'")
                        mysql.connection.commit()
                    else:
                        cur.execute(
                            "UPDATE status SET status = 'off' WHERE name = 'illumination'")
                        mysql.connection.commit()

            if cfg.save_camera_to_file == True:
                out.write(img)  # save img to file for video capturing

                # after 10 seconds, save new video snippet
                if time.time() - Camera.video_time > cfg.camera_file_recording_time:
                    Camera.video_number += 1
                    print("Camera video_number {}" .format(Camera.video_number))
                    Camera.video_time = time.time()

                    # set new video name to save new file
                    video_name = cfg.folder_camera_recording + \
                        'CameraOutput_' + str(Camera.video_number) + '.mp4'
                    out = cv2.VideoWriter(video_name,
                                          cv2.VideoWriter_fourcc(
                                              *'avc1'),
                                          30, (frame_width, frame_height))

            # encode as a jpeg image and return it
            yield cv2.imencode('.jpg', img)[1].tobytes()

    def get_frame(self):
        """Return the current camera frame."""

        # store time to check if camera is frequently accessed
        Camera.last_access = time.time()

        # wait for a signal from the camera thread
        Camera.event.wait()
        Camera.event.clear()

        return Camera.frame

    @classmethod
    def _thread(cls):
        """Camera background thread."""

        print('Starting camera thread.')

        # get frame from camera via cv2
        # frames_iterator_cls = cls()
        # frames_iterator = frames_iterator_cls.frames()
        frames_iterator = cls.frames()

        for frame in frames_iterator:
            Camera.frame = frame  # store frame from cv2 in class object
            Camera.event.set()  # send signal to clients
            time.sleep(0)

            # if there hasn't been any clients asking for frames in the last x
            # seconds then stop the thread
            if time.time() - Camera.last_access > cfg.camera_timeout:
                frames_iterator.close()
                print('Stopping camera thread due to inactivity.')
                break
        Camera.thread = None


def generate(camera):
    """Generate the data for video stream.

    Generate the data with the use of Python generator function. The concept of
    generators in python is explained in PEP 255.
    """

    while True:
        frame = camera.get_frame()

        # each yield expression is directly sent to the browser
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/webcam')
@is_logged_in
def webcam():

    import cv2
    import numpy as np

    # get files in queue to show which test is currently running
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM queue")
    entries = cur.fetchall()  # fetch in dictionary form
    mysql.connection.commit()

    # change light status depending on histogram from camera
    # cap = cv2.VideoCapture(0)
    # ret, frame = cap.read()
    # histogram = cv2.calcHist([frame], [0], None, [256], [0, 256])
    # brightness = np.ndarray.mean(frame.ravel())

    # if brightness < 30:
    #     cur.execute(
    #         "UPDATE status SET status = 'on' WHERE name = 'illumination'")
    #     mysql.connection.commit()
    # else:
    #     cur.execute(
    #         "UPDATE status SET status = 'off' WHERE name = 'illumination'")
    #     mysql.connection.commit()

    return render_template('webcam.html', entries=entries, table_len=cfg.queue_table_length)


@app.route('/video_feed')
def video_feed():
    """Route used by html to access video"""

    # with this multipart type, each part replaces the one before
    return Response(generate(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


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
    # app.run(host='192.168.1.12')  # Wohnung
    # app.run(host='141.23.138.2')  # TU-Berlin
    # app.run(threaded=True)
    # app.run()
