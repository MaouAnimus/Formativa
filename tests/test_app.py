from app import app


def test_hello_shows_name():
    response = app.test_client().get("/hello?name=TEST")

    assert response.status_code == 200
    assert b"Hola, TEST" in response.data


def test_hello_escapes_html():
    response = app.test_client().get("/hello?name=%3Cscript%3Ealert(1)%3C/script%3E")

    assert response.status_code == 200
    assert b"&lt;script&gt;" in response.data
    assert b"<script>" not in response.data