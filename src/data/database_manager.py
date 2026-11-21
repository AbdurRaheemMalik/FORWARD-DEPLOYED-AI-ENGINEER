import os
from contextlib import contextmanager
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker


class DatabaseManager:
    def __init__(self, url: str | None = None):
        url = url or f"sqlite:///{os.getenv('DB_PATH', 'docs/database/bank.db')}"
        self.engine = create_engine(url)
        event.listen(self.engine, "connect",
                     lambda conn, _: conn.execute("PRAGMA foreign_keys = ON"))
        self._sessions = sessionmaker(bind=self.engine)

    @contextmanager
    def transaction(self):
        session = self._sessions()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
