from fastapi import FastAPI, Request, HTTPException, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
from starlette.middleware.sessions import SessionMiddleware

# ======================
# init DB
# ======================
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    SessionMiddleware,
    secret_key="0819"
)

templates = Jinja2Templates(directory="templates")


# ======================
# DB dependency
# ======================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ======================
# auth check
# ======================
def require_admin(request: Request):
    if not request.session.get("is_admin"):
        raise HTTPException(status_code=403, detail="Not authorized")


# ======================
# schema
# ======================
class PostCreate(BaseModel):
    title: str
    content: str


ADMIN_PASSWORD = "0819"


# ======================
# login
# ======================
@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={}
    )


@app.post("/login")
def login(request: Request, password: str = Form(...)):
    if password == ADMIN_PASSWORD:
        request.session["is_admin"] = True
        return RedirectResponse(url="/", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"error": "Wrong password"}
    )


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)


# ======================
# homepage
# ======================
@app.get("/")
def homepage(request: Request, db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "posts": posts,
            "is_admin": request.session.get("is_admin", False)
        }
    )


# ======================
# search
# ======================
@app.get("/search")
def search(q: str, request: Request, db: Session = Depends(get_db)):
    posts = db.query(models.Post).filter(
        models.Post.title.contains(q) |
        models.Post.content.contains(q)
    ).all()

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "posts": posts,
            "is_admin": request.session.get("is_admin", False)
        }
    )


# ======================
# tag page ⭐
# ======================
@app.get("/tag/{tag}")
def get_by_tag(tag: str, request: Request, db: Session = Depends(get_db)):
    posts = db.query(models.Post).filter(
        models.Post.tags.contains(tag)
    ).all()

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "posts": posts,
            "is_admin": request.session.get("is_admin", False)
        }
    )


# ======================
# create page
# ======================
@app.get("/posts/create")
def create_post_page(request: Request):
    require_admin(request)

    return templates.TemplateResponse(
        request=request,
        name="create.html",
        context={}
    )


# ======================
# create post
# ======================
@app.post("/posts")
def create_post(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    tags: str = Form(""),
    db: Session = Depends(get_db)
):
    require_admin(request)

    post = models.Post(
        title=title,
        content=content,
        tags=tags
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    return RedirectResponse(url="/", status_code=303)


# ======================
# edit page
# ======================
@app.get("/posts/{post_id}/edit")
def edit_post_page(post_id: int, request: Request, db: Session = Depends(get_db)):
    require_admin(request)

    post = db.query(models.Post).filter(models.Post.id == post_id).first()

    if not post:
        raise HTTPException(status_code=404, detail="article not found")

    return templates.TemplateResponse(
        request=request,
        name="edit.html",
        context={"post": post}
    )


# ======================
# edit post
# ======================
@app.post("/posts/{post_id}/edit")
def edit_post(
    request: Request,
    post_id: int,
    title: str = Form(...),
    content: str = Form(...),
    tags: str = Form(""),
    db: Session = Depends(get_db)
):
    require_admin(request)

    post = db.query(models.Post).filter(models.Post.id == post_id).first()

    if not post:
        raise HTTPException(status_code=404, detail="article not found")

    post.title = title
    post.content = content
    post.tags = tags

    db.commit()

    return RedirectResponse(url="/", status_code=303)


# ======================
# single post
# ======================
@app.get("/posts/{post_id}")
def get_post(post_id: int, request: Request, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()

    if not post:
        raise HTTPException(status_code=404, detail="article not found")

    return templates.TemplateResponse(
        request=request,
        name="post.html",
        context={"post": post}
    )


# ======================
# delete
# ======================
@app.delete("/posts/{post_id}")
def delete_post(request: Request, post_id: int, db: Session = Depends(get_db)):
    require_admin(request)

    post = db.query(models.Post).filter(models.Post.id == post_id).first()

    if not post:
        raise HTTPException(status_code=404, detail="article not found")

    db.delete(post)
    db.commit()

    return {"msg": "deleted successfully"}


# ======================
# api update (optional)
# ======================
@app.put("/posts/{post_id}")
def update_post(post_id: int, post: PostCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Post).filter(models.Post.id == post_id).first()

    if not existing:
        raise HTTPException(status_code=404, detail="article not found")

    existing.title = post.title
    existing.content = post.content

    db.commit()
    db.refresh(existing)

    return existing