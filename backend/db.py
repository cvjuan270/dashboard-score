from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker 

from collections.abc import Generator
from sqlm

engine = create_engine('postgresql://odoo16:odoo16@localhost:5432/db_dashbaord_score')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
