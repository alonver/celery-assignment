from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float, Text
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# In a production system, this will be in an env file or a secret store
DATABASE_URL = "postgresql://postgres:password@localhost:5432/celery"
db_engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=db_engine)
Base = declarative_base()


class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    region = Column(String)
    type = Column(String)
    files = relationship("ExcelFile", back_populates="category")


class ExcelFile(Base):
    __tablename__ = 'excelfiles'
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    filepath = Column(String)
    category_id = Column(Integer, ForeignKey('categories.id'))
    category = relationship("Category", back_populates="files")
    num_sum = Column(Float)
    text = Column(Text)


def create_db():
    Base.metadata.create_all(bind=db_engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    finally:
        db.close()
