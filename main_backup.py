from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

app = FastAPI()
templates = Jinja2Templates(directory="templates")

class Post(BaseModel):
    title: str
    content: str


posts = [
    {"id":1, "title": "first article", "content": "content1"},
    {"id":2, "title": "second article", "content": "content2"},
]

@app.get("/")
def homepage(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


@app.get("/posts/{post_id}")
def get_post(post_id:int):
    for post in posts:
        if post["id"] == post_id:
            return post
    raise HTTPException(status_code=404, detail="article not found")

@app.get("/posts", status_code=200)
def get_posts():
    return posts

@app.post("/posts", status_code=201)
def create_post(post:Post):
    new_post = {
        "id": len(posts) + 1,
        "title": post.title,
        "content": post.content
    }
    posts.append(new_post)
    return new_post
    


@app.delete("/posts/{post_id}", status_code=200)
def delete_post(post_id:int):
    for index, post in enumerate(posts):
        if post["id"] == post_id:
            posts.pop(index)
            return {"msg": "successful!"}
    raise HTTPException(status_code=404, detail="article not found")

@app.put("/posts/{post_id}", status_code=200)
def update_post(post_id:int, post:Post):
    for index, p in enumerate(posts):
        if p["id"] == post_id:
            posts[index]["title"] = post.title
            posts[index]["content"] = post.content
            return posts[index]
    raise HTTPException(status_code=404, detail="article not found")      
