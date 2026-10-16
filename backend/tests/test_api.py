from fastapi.testclient import TestClient
from app.main import create_app


def test_health_and_persistence(tmp_path):
    path = tmp_path / 'academy.sqlite3'
    with TestClient(create_app(path)) as client:
        assert client.get('/api/health').json() == {'status': 'ok', 'database': 'ok', 'phase': 3}
        assert client.get('/api/settings').json()['welcome_message']
        message = "Let's build worlds! 'quoted'"
        assert client.put('/api/settings', json={'welcome_message': message}).status_code == 200
    with TestClient(create_app(path)) as client:
        assert client.get('/api/settings').json()['welcome_message'] == message


def test_validation(tmp_path):
    with TestClient(create_app(tmp_path / 'test.sqlite3')) as client:
        original = client.get('/api/settings').json()
        for payload in ({}, {'welcome_message': ''}, {'welcome_message': 'x' * 201}):
            assert client.put('/api/settings', json=payload).status_code == 422
        assert client.get('/api/settings').json() == original


def test_newer_schema_rejected(tmp_path):
    import sqlite3
    import pytest
    path = tmp_path / 'new.sqlite3'
    with sqlite3.connect(path) as db:
        db.execute('PRAGMA user_version = 5')
    with pytest.raises(RuntimeError, match='newer'):
        with TestClient(create_app(path)):
            pass
