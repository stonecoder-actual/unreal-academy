import pytest


@pytest.fixture(autouse=True)
def isolated_catalogue(monkeypatch):
    # Core local/import tests exercise their own fixtures; bundled tests opt in.
    monkeypatch.setenv('ACADEMY_BUNDLED_CURRICULUM', '0')
    monkeypatch.setenv('ACADEMY_UDEMY_ONLY', '0')
