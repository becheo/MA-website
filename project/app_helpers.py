"""Functions to use in app.py"""

import sys
import os
import time
import threading
try:
    from thread import get_ident
except ImportError:
    from _thread import get_ident

if 'pytest' in sys.modules:
    from Website.project import config as cfg  # for pytest
else:
    import config as cfg  # for Apache Server


# Path variables
UPLOAD_FOLDER = cfg.folder_upload
RESULTS_FOLDER = cfg.folder_results
accesslog = cfg.file_accesslog
errorlog = cfg.file_errorlog

# Parameters
samplerate_write = 500

# Config MySQL


def init_db(app):
    """Initialize database."""

    app.config['MYSQL_HOST'] = cfg.MYSQL_HOST
    app.config['MYSQL_USER'] = cfg.MYSQL_USER
    app.config['MYSQL_PASSWORD'] = cfg.MYSQL_PASSWORD
    app.config['MYSQL_DB'] = cfg.MYSQL_DB
    app.config['MYSQL_CURSORCLASS'] = cfg.MYSQL_CURSORCLASS


def read_txt_by_lines(path):
    """Read textfile line by line

    Reads textfile with splitlines attribute. Returns a list with the
    contents of the textfile, every row contains one entry.

    Args:
        path (str): path to the file to read

    Returns:
        buffer (list): content of textfile
    """

    with open(path, "r") as f:
        buffer = f.read().splitlines()
        f.close()
    return buffer


def read_results_by_lines(path):
    """Reads result-textfile line by line

    Reads results-textfile with splitlines attribute. Returns a list with the
    measured values (voltage, current, rpm, temperature).

    Args:
        path (str): path to the file to read

    Returns:
        buffer (list): Measured values from testbench (convertet to float)
                        list[0]: Index
                        list[1]: Time [s]
                        list[2]: Generator speed [1/min]
                        list[3]: Generator voltage [V]
                        list[4]: Motor voltage [V]
                        list[5]: Current [A]
                        list[6]: Temperature [°C]
    """

    with open(path, "r") as f:
        buffer_textfile = f.read().splitlines()
        for i in range(len(buffer_textfile)):
            if buffer_textfile[i][0:5] == "Index":
                startline_data = i+1
                break
    f.close()

    number_of_dataseries = buffer_textfile[startline_data].count(',') + 1
    buffer_textfile = buffer_textfile[startline_data:len(buffer_textfile)]

    # split up data
    data_str = [[] for i in range(number_of_dataseries)]
    data = data_str
    for word in buffer_textfile:
        word = word.split(", ")
        for i in range(len(word)):
            data_str[i].append(word[i])

    # string to float
    for i in range(len(data_str)):
        data[i] = [float(i) for i in data_str[i]]

    return data


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
                # if this client's event is not set, then set it
                # also update the last set timestamp to now
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

    thread = None  # background thread that reads frames from camera
    frame = None  # current frame is stored here by background thread
    last_access = 0  # time of last client access to the camera
    event = CameraEvent()

    def __init__(self):
        """Start the background camera thread if it isn't running yet."""
        if Camera.thread is None:
            Camera.last_access = time.time()

            # start background frame thread
            Camera.thread = threading.Thread(target=self._thread)
            Camera.thread.start()

            # wait until frames are available
            while self.get_frame() is None:
                time.sleep(0)

    @staticmethod
    def frames():
        # It is crucial that the import statement for the cv2 module is
        # located inside this function. Otherwise the Apache server will not
        # be able to start and serve the webpage
        import cv2

        camera = cv2.VideoCapture(Camera.video_source)
        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')

        while True:
            # read current frame
            _, img = camera.read()

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
        frames_iterator = cls.frames()

        for frame in frames_iterator:
            Camera.frame = frame
            Camera.event.set()  # send signal to clients
            time.sleep(0)

            # if there hasn't been any clients asking for frames in
            # the last 60 seconds then stop the thread
            if time.time() - Camera.last_access > 60:
                frames_iterator.close()
                print('Stopping camera thread due to inactivity.')
                break
        Camera.thread = None


# class BaseCamera(object):

#     @staticmethod
#     def frames():
#         """"Generator that returns frames from the camera."""
#         raise RuntimeError('Must be implemented by subclasses.')


def generate(camera):
    """Generate the data for video stream.

    Generate the data with the use of Python generator function. The concept of
    generator in python is explained in PEP 255.
    """

    while True:
        frame = camera.get_frame()

        # each yield expression is directly sent to the browser
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
