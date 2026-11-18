import os
from contextlib import contextmanager

from sqlalchemy import URL, create_engine, event
from sqlalchemy.orm import Session, sessionmaker


engine = create_engine(f"sqlite:///{os.getenv('DB_PATH', 'docs/database/bank.db')}")
event.listen(engine, "connect", lambda conn, _: conn.execute("PRAGMA foreign_keys = ON"))
SessionLocal = sessionmaker(bind=engine)


@contextmanager
def get_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()