from fastapi import HTTPException,status,Depends,APIRouter,Query
from sqlalchemy.orm import Session
from ..import models,schemas,oauth2
from ..database import get_db
from typing import Optional
from sqlalchemy import desc

router = APIRouter(
    prefix = "/events",
    tags = ["Events"]
)

@router.post('',status_code=status.HTTP_201_CREATED)
def create_events(event:schemas.Event,db:Session=Depends(get_db),curr_user:int=Depends(oauth2.get_current_user)):

    existing_event = db.query(models.Event).filter(
        models.Event.title == event.title,
        models.Event.location == event.location,
        models.Event.event_datetime == event.event_datetime
    ).first()

    if curr_user.role!="admin":
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Only admins can create events")
    
    if existing_event:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Event already registered")
    
    new_event = models.Event(owner_id=curr_user.id,**event.model_dump())
    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    new_event_dict = new_event.__dict__.copy()
    new_event_dict["owner"] = new_event.user.__dict__.copy()
    new_pydantic_event = schemas.GetEventsAdmin(**new_event_dict)

    return new_pydantic_event

@router.get("/getall")
def get_all_events(db:Session = Depends(get_db),
    limit: int = Query(10, description="Limit the number of users returned"),
    title: Optional[str] = Query(None, description="Search users by title"),
    location: Optional[str] = Query(None, description="Filter users by location"),
    min_price: Optional[int] = Query(None, description="Minimum price filter"),
    max_price: Optional[int] = Query(None, description="Maximum price filter"),
    curr_user:int=Depends(oauth2.get_current_user)):
    
    query = db.query(models.Event)

    if title:
        query = query.filter(models.Event.title.contains(title))
    
    if location:
        query = query.filter(models.Event.location.contains(location))
    
    if min_price is not None:
        query = query.filter(models.Event.price >= min_price)
    
    if max_price is not None:
        query = query.filter(models.Event.price <= max_price)

    query = query.order_by(desc(models.Event.event_datetime))

    results = query.limit(limit).all()
    
    
    if curr_user.role == "admin":
        all_events = []
        for event in results:
            event_dict = event.__dict__.copy()
            event_dict['owner']=event.user.__dict__.copy()
            all_events.append(schemas.GetEventsAdmin(**event_dict))
    else:
        all_events = []
        for event in results:
            event_dict = event.__dict__.copy()
            event_dict['owner']=event.user.__dict__.copy()
            all_events.append(schemas.GetEventsUser(**event_dict))

    return all_events

@router.put("/{id}")
def update_event(id: int, updated_event: schemas.Event, db: Session = Depends(get_db), curr_user: int = Depends(oauth2.get_current_user)):
    event_query = db.query(models.Event).filter(models.Event.id == id)
    event = event_query.first()

    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Event with id {id} does not exist")
    
    if curr_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can update events")
    
    event_query.update(updated_event.model_dump(), synchronize_session=False)
    db.commit()
    db.refresh(event)

    event_dict = event.__dict__.copy()
    event_dict["owner"] = event.user.__dict__.copy()
    updated_pydantic_event = schemas.GetEventsAdmin(**event_dict)

    return updated_pydantic_event


    
