
"""Functions to use in app.py"""

# Path variables:
#  TODO change to TU PC paths
UPLOAD_FOLDER = 'C:/Users/Oliver/Desktop/Masterarbeit/03_Software/Website/uploads'
accesslog = 'C:/Users/Oliver/Desktop/Masterarbeit/03_Software/Website/logs/access.log'
errorlog = 'C:/Users/Oliver/Desktop/Masterarbeit/03_Software/Website/logs/error.log'

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
