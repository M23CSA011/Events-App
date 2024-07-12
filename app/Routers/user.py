from fastapi import HTTPException , status , Depends , APIRouter,Query
from sqlalchemy.orm import Session
from .. import models , schemas , utils
from ..database import get_db
from .. import models,schemas,oauth2 
from typing import Optional

router = APIRouter(
    prefix="/users",
    tags=['Users']
)

@router.post('/user',status_code=status.HTTP_201_CREATED)
def create_users(user:schemas.UserCreate,db:Session = Depends(get_db)):
    
    existing_user = db.query(models.User).filter(models.User.email==user.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Email already registered")

    hashed_passwored = utils.hash(user.password)
    user.password = hashed_passwored
    new_user = models.User(**user.model_dump())
    new_user.role = "user"
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    new_pydantic_user = schemas.UserOut(**new_user.__dict__) 

    return new_pydantic_user

@router.post('/admin',status_code=status.HTTP_201_CREATED)
def create_admins(admin:schemas.UserCreate,db:Session = Depends(get_db)):
    
    existing_admin = db.query(models.User).filter(models.User.email==admin.email).first()
    if existing_admin:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Email already registered")

    hashed_passwored = utils.hash(admin.password)
    admin.password = hashed_passwored
    new_user = models.User(**admin.model_dump())
    new_user.role = "admin"
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    new_pydantic_user = schemas.UserOut(**new_user.__dict__) 

    return new_pydantic_user

@router.get("/{email}")
def get_user(email:str,db:Session = Depends(get_db),curr_user:int=Depends(oauth2.get_current_user)):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"User with id {id} was not found")
    
    if user.id!=curr_user.id and curr_user.role!="admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not authorized to access this resource")

    new_pydantic_user = schemas.UserOut(**user.__dict__)

    return new_pydantic_user 

@router.get("")
def get_alluser(db:Session = Depends(get_db),
    limit: int = Query(10, description="Limit the number of users returned"),
    email: Optional[str] = Query(None, description="Search users by email"),
    role: Optional[str] = Query(None, description="Filter users by role ('user' or 'admin')"),
    curr_user:int=Depends(oauth2.get_current_user)):
    
    query = db.query(models.User)
    
    if curr_user.role!="admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not authorized to access this resource")
    
    if email:
        query = query.filter(models.User.email.contains(email))

    if role:
        query = query.filter(models.User.role == role)

    users = query.limit(limit).all()
    
    new_pydantic_users = []
    for user in users:
        new_pydantic_user = schemas.UserOut(**user.__dict__)
        new_pydantic_users.append([new_pydantic_user])
    return new_pydantic_users 