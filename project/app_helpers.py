
"""Functions to use in app.py"""


# Config MySQL
def init_db(app):
    """Initialize database."""

    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = 'aligator3'  #
    app.config['MYSQL_DB'] = 'website'  # TODO ändern auf TU database (?)
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
