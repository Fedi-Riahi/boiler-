from fastapi import FastAPI, Depends
from app.database import get_db 
from app.schemas.schema import UserCreate,UserResponse, ProductCreate, ProductResponse
from sqlalchemy.orm import Session
from app.models.models import User, Product
from app.redis_cache import r
from fastapi.encoders import jsonable_encoder
import json
app = FastAPI()

# Root Endpoint
@app.get('/')
def root():
    return {"message": "Working"}

# Create a new user
@app.post('/add-user', response_model=UserResponse)
def add_test(test: UserCreate, db: Session = Depends(get_db)):
    new_test = User(id=test.id, name=test.name, email=test.email)
    db.add(new_test)
    db.commit()
    db.refresh(new_test)
    r.delete('users')
    return new_test

# Create a new product
@app.post('/add-product', response_model=ProductResponse)
def add_product(product: ProductCreate, db: Session = Depends(get_db)):
    new_product = Product(id=product.id,user_id=product.user_id, name=product.name, description=product.description, price=product.price)
    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    r.delete('products')
    return new_product

# Get all users
@app.get('/users', response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    cache= r.get('users')
    # Check if users are cached
    if cache:
        print('Serving from cache')
        return json.loads(cache)
    # If not cached, fetch from database
    print('Serving from database')
    users = db.query(User).all()
    cached_users = jsonable_encoder(users)
    r.set('users', json.dumps(cached_users), ex=60)  # Cache for 10 seconds
    return users

# Get all products
@app.get('/products', response_model=list[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    cache = r.get('products')

    # Check if products are cached
    if cache:
        print("Serving from cache")
        return json.loads(cache)
    # If not cached, fetch from database
    print("Serving from database")
    products = db.query(Product).all()
    cached_products = jsonable_encoder(products)
    r.set('products', json.dumps(cached_products), ex=60)
    return products
