import sqlalchemy as sql
import sqlalchemy.orm as orm
import sqlalchemy.ext.declarative as declarative

DATABASE_URL = "sqlite:///./database.db"

engine = sql.create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative.declarative_base()