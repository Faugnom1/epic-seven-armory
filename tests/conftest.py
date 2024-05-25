import pytest
from app import app, db

@pytest.fixture(scope='module')
def test_client():
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite://",
        "WTF_CSRF_ENABLED": False,  
        "SQLALCHEMY_TRACK_MODIFICATIONS": False
    })

    with app.app_context():
        db.create_all() 

    testing_client = app.test_client()

    ctx = app.app_context()
    ctx.push()

    yield testing_client

    ctx.pop()
