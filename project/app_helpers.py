
"""Functions to use in app.py"""

# Path variables
#  TODO change to TU PC paths
UPLOAD_FOLDER = 'C:/Users/Oliver/Desktop/Masterarbeit/03_Software/Website/project/static/uploads'
RESULTS_FOLDER = 'C:/Users/Oliver/Desktop/Masterarbeit/03_Software/Website/project/static/results'
accesslog = 'C:/Users/Oliver/Desktop/Masterarbeit/03_Software/Website/logs/access.log'
errorlog = 'C:/Users/Oliver/Desktop/Masterarbeit/03_Software/Website/logs/error.log'

# Parameters
samplerate_write = 500

# Config MySQL


def init_db(app):
    """Initialize database."""

    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = 'aligator3'  #
    app.config['MYSQL_DB'] = 'website'  # TODO ändern auf TU database (?)
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'


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
