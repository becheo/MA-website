
import os
import tempfile

import pytest
from flask import g
from flask import session

from Website.project import app


@pytest.fixture
def client():
    """The client can trigger test requests to the application.

    Will be called by each test.
    The testing config flag is activated to create better reports.
    tempfile is used to create a temporary database for testing.
    """

    db_fd, app.app.config['DATABASE'] = tempfile.mkstemp()
    app.app.config['TESTING'] = True

    with app.app.test_client() as client:
        with app.app.app_context():
            app.app_helpers.init_db(app.app)
        yield client

    os.close(db_fd)
    os.unlink(app.app.config['DATABASE'])


def test_home(client):
    # assert client.get("/").status_code == 200

    # Alternative:
    result = client.get("/").status_code
    assert result == 200


def login(client, username, password):
    return client.post('/login',
                       data=dict(username=username,
                                 password=password),
                       follow_redirects=True)


def test_login(client):
    username = 'Oliver'

    # assert client.get("/login").status_code == 200

    response = login(client, username, 'Oliver')

    # check for status code 200 (success, OK)
    assert response.status_code == 200

    # check for text in html page that is shown after login
    assert b'Dashboard' in response.data

    # check if login was successfull and session is set
    assert session['logged_in'] == True
    assert session['username'] == username

    # assert result.headers["Location"] == "http://localhost/dashboard"

    # with client:
    #     client.get("/")
    #     assert session['logged_in'] == True
    # assert session['username'] == username
