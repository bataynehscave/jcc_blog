from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, Table, ForeignKey, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
metadata = MetaData()

# Define the many-to-many relationship for tags
blog_tags = Table(
    "blog_tags",
    Base.metadata,
    Column("blog_id", Integer, ForeignKey("blogs.id")),
    Column("tag_id", Integer, ForeignKey("tags.id"))
)

news_tags = Table(
    "news_tags",
    Base.metadata,
    Column("news_id", Integer, ForeignKey("news.id")),
    Column("tag_id", Integer, ForeignKey("tags.id"))
)

class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

class Blog(Base):
    __tablename__ = "blogs"
    id = Column(Integer, primary_key=True, index=True)
    author = Column(String, index=True)
    title = Column(String, index=True)
    body = Column(String, index=True)
    tags = relationship("Tag", secondary=blog_tags, back_populates="blogs")

class News(Base):
    __tablename__ = "news"
    id = Column(Integer, primary_key=True, index=True)
    author = Column(String, index=True)
    title = Column(String, index=True)
    body = Column(String, index=True)
    tags = relationship("Tag", secondary=news_tags, back_populates="news")

Tag.blogs = relationship("Blog", secondary=blog_tags, back_populates="tags")
Tag.news = relationship("News", secondary=news_tags, back_populates="tags")

Base.metadata.create_all(bind=engine)

class BlogCreate(BaseModel):
    author: str
    title: str
    body: str
    tags: List[str] = []

class NewsCreate(BaseModel):
    author: str
    title: str
    body: str
    tags: List[str] = []

class BlogRead(BlogCreate):
    id: int

    class Config:
        orm_mode = True

class NewsRead(NewsCreate):
    id: int

    class Config:
        orm_mode = True

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/blogs/", response_model=BlogRead)
def create_blog(blog: BlogCreate, db: Session = Depends(get_db)):
    db_blog = Blog(author=blog.author, title=blog.title, body=blog.body)
    db.add(db_blog)
    db.commit()
    db.refresh(db_blog)
    for tag_name in blog.tags:
        tag = db.query(Tag).filter(Tag.name == tag_name).first()
        if tag is None:
            tag = Tag(name=tag_name)
            db.add(tag)
            db.commit()
            db.refresh(tag)
        db_blog.tags.append(tag)
    db.commit()
    db.refresh(db_blog)
    return db_blog

@app.get("/blogs/", response_model=List[BlogRead])
def read_blogs(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    blogs = db.query(Blog).offset(skip).limit(limit).all()
    return blogs

@app.post("/news/", response_model=NewsRead)
def create_news(news: NewsCreate, db: Session = Depends(get_db)):
    db_news = News(author=news.author, title=news.title, body=news.body)
    db.add(db_news)
    db.commit()
    db.refresh(db_news)
    for tag_name in news.tags:
        tag = db.query(Tag).filter(Tag.name == tag_name).first()
        if tag is None:
            tag = Tag(name=tag_name)
            db.add(tag)
            db.commit()
            db.refresh(tag)
        db_news.tags.append(tag)
    db.commit()
    db.refresh(db_news)
    return db_news

@app.get("/news/", response_model=List[NewsRead])
def read_news(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    news = db.query(News).offset(skip).limit(limit).all()
    return news

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
