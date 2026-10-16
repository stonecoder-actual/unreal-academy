import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel, Field
from .database import connect, initialize
from .library import create_library_router
from .guided import create_guided_router, publish_existing_guides
from .external import create_external_router


def create_app(database_path: Path | None = None, courses_root: Path | None = None):
    path = database_path or Path(os.getenv('DATABASE_PATH', '/data/academy.sqlite3'))

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        initialize(path)
        publish_existing_guides(path)
        yield

    app = FastAPI(title='Unreal Academy', lifespan=lifespan)
    app.include_router(create_library_router(path, courses_root or Path(os.getenv('COURSES_ROOT', '/courses'))))
    app.include_router(create_guided_router(path, courses_root or Path(os.getenv('COURSES_ROOT', '/courses'))))
    app.include_router(create_external_router(path))

    @app.get('/api/health')
    def health():
        with connect(path) as db:
            db.execute('SELECT value FROM settings LIMIT 1').fetchone()
        return {'status': 'ok', 'database': 'ok', 'phase': 3}

    @app.get('/api/settings')
    def settings():
        with connect(path) as db:
            return dict(db.execute('SELECT key, value FROM settings').fetchall())

    class SettingsUpdate(BaseModel):
        welcome_message: str = Field(min_length=1, max_length=200)

    @app.put('/api/settings')
    def update_settings(payload: SettingsUpdate):
        with connect(path) as db:
            db.execute('UPDATE settings SET value = ? WHERE key = ?',
                       (payload.welcome_message, 'welcome_message'))
        return settings()

    return app


app = create_app()
