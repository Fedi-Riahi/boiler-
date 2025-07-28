from fastapi import APIRouter
from fastapi import Depends
from app.database import get_db
from app.schemas.schema import UserCreate,UserResponse
from sqlalchemy.orm import Session
from app.models.models import User
from app.redis_cache import r
from typing import Optional
from fastapi.encoders import jsonable_encoder
import json

router = APIRouter(prefix="/users", tags=["Users"])




# Create a new user
@router.post('/add-user', response_model=UserResponse)
def add_test(test: UserCreate, db: Session = Depends(get_db)):
    new_test = User(id=test.id, name=test.name, email=test.email)
    db.add(new_test)
    db.commit()
    db.refresh(new_test)
    r.delete('users')
    return new_test

# Get all users with optional filtering
@router.get('/users', response_model=list[UserResponse])
def get_users(
    name: Optional[str] = None,
    email: Optional[str] = None,
    db: Session = Depends(get_db)
):
    cache_key = f'users:{name}:{email}'
    cache = r.get(cache_key)

    if cache:
        print('Serving filtered users from cache')
        return json.loads(cache)

    print('Serving filtered users from database')
    query = db.query(User)
    if name:
        query = query.filter(User.name.
        ilike(f'%{name}%')) 
    if email:
        query = query.filter(User.email.ilike(f'%{email}%'))

    users = query.all()
    result = jsonable_encoder(users)
    r.set(cache_key, json.dumps(result), ex=60)
    return users

# Get a user by ID
@router.get('/user/{user_id}', response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"error": "User not found"}
    return user


# Delete a user by ID
@router.delete('/user/{user_id}', response_model=dict)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"error": "User not found"}
    db.delete(user)
    db.commit()
    r.delete('users')
    return {"message": f"User {user_id} deleted successfully"}


# Update a user by ID
@router.put('/user/{user_id}', response_model=UserResponse)
def update_user(user_id: int, user_data: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"error": "User not found"}
    user.name = user_data.name
    user.email = user_data.email
    db.commit()
    db.refresh(user)
    r.delete('users')
    return user


