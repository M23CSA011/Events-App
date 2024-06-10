from fastapi import HTTPException , status , Response , Depends , APIRouter
from sqlalchemy.orm import Session, joinedload
from .. import models , schemas , oauth2
from ..database import get_db
from typing import Optional
from sqlalchemy import func

router = APIRouter(
    prefix="/posts",
    tags = ["Posts"]
)

@router.get("")
def get_posts(db:Session = Depends(get_db),curr_user:int = Depends(oauth2.get_current_user),limit:int=10,skip:int=0,search:Optional[str]=""): 
    # cursor.execute("""SELECT * FROM public."Posts" """)
    # posts = cursor.fetchall()

    # posts = db.query(models.Post).all()
    # new_pydantic_post = []
    # print(posts[0].__dict__)
    # new_pydantic_post = [schemas.Post(**post.__dict__) for post in posts]

    # posts = db.query(models.Post).options(joinedload(models.Post.owner)).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    
    results = db.query(models.Post,func.count(models.Vote.post_id).label("votes")).join(
        models.Vote,models.Vote.post_id == models.Post.id,isouter=True).group_by(
            models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    
    posts_with_post = []
    for post ,votes in results:
        post_dict = post.__dict__.copy()
        post_dict['owner'] = post.owner.__dict__.copy()
        post_dict['votes'] = votes
        posts_with_post.append(schemas.Post_Votes(**post_dict))

    return posts_with_post

@router.get("/{id}")
def get_post(id:int,db:Session = Depends(get_db),curr_user:int = Depends(oauth2.get_current_user)):
    # cursor.execute(""" SELECT * FROM public."Posts" WHERE id = %s""",(str(id),))
    # post = cursor.fetchone() 
    result = db.query(models.Post,func.count(models.Vote.post_id).label("votes")).join(
        models.Vote,models.Vote.post_id == models.Post.id,isouter=True).group_by(
            models.Post.id).filter(models.Post.id == id).first()
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with id {id} was not found")
    
    post,votes = result
    post_dict = post.__dict__.copy()
    post_dict['owner'] = post.owner.__dict__.copy()
    post_dict['votes'] = votes
    new_pydantic_post = schemas.Post_Votes(**post_dict)

    return new_pydantic_post

@router.post('',status_code=status.HTTP_201_CREATED)
def create_posts(post:schemas.PostCreate,db:Session = Depends(get_db),curr_user:int = Depends(oauth2.get_current_user)):
    # cursor.execute("""INSERT INTO public."Posts" (title,content,published) VALUES (%s,%s,%s) RETURNING *""",
    #                (post.title,post.content,post.published))
    # new_post = cursor.fetchone()
    # conn.commit()
    new_post = models.Post(owner_id=curr_user.id,**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    new_post_dict = new_post.__dict__.copy()
    new_post_dict['owner'] = new_post.owner.__dict__.copy()
    new_pydantic_post = schemas.Post(**new_post_dict)

    return new_pydantic_post

# @app.get('/posts/latest')
# def get_latest_post():
#     return {"latest post": my_posts[len(my_posts)-1]}

@router.delete("/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id:int,db:Session = Depends(get_db),curr_user:int = Depends(oauth2.get_current_user)):
    # cursor.execute(""" DELETE FROM public."Posts" WHERE id = %s RETURNING *""",(str(id),))
    # deleted_post = cursor.fetchone()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)
    
    if post_query.first()==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with id {id} was not found")
    
    if post_query.first().owner_id!=curr_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not Authorized to perform requested action")
    
    
   
    post_query.delete(synchronize_session=False)
    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}")
def update_post(id:int,post:schemas.PostCreate,db:Session = Depends(get_db),curr_user:int = Depends(oauth2.get_current_user)):
    # cursor.execute("""UPDATE public."Posts" SET title = %s,content = %s,published = %s WHERE id = %s RETURNING *""",(post.title,post.content,post.published,str(id)))
    # updated_post = cursor.fetchone()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post2 = post_query.first()
    if post2==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with id {id} was not found")
    
    if post2.owner_id!=curr_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not Authorized to perform requested action")
    
    post_query.update(post.model_dump(),synchronize_session=False)
    db.commit()
    
    post2 = post_query.first()
    post_dict = post2.__dict__.copy()
    post_dict['owner'] = post2.owner.__dict__.copy()
    new_pydantic_post = schemas.Post(**post_dict)

    return new_pydantic_post