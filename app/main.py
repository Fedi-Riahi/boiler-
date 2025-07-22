from fastapi import FastAPI, Depends
from app.database import get_db
from app.schemas.schema import UserCreate,UserResponse, ProductCreate, ProductResponse
from sqlalchemy.orm import Session
from app.models.models import User, Product
from app.redis_cache import r
from fastapi.encoders import jsonable_encoder
from typing import Optional
from app.search.es_client import es
from typing import Optional
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

    # Index the product in Elasticsearch
    es.index(index='products', id=new_product.id, document={
        'name': new_product.name,
        'description': new_product.description,
        'price': new_product.price,
        'user_id': new_product.user_id
    })
    return new_product



@app.get('/users', response_model=list[UserResponse])
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
        ilike(f'%{name}%'))  # case-insensitive
    if email:
        query = query.filter(User.email.ilike(f'%{email}%'))

    users = query.all()
    result = jsonable_encoder(users)
    r.set(cache_key, json.dumps(result), ex=60)
    return users


# Get all products with filtering 
@app.get('/products', response_model=list[ProductResponse])
def get_products(
    name: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    db: Session = Depends(get_db)
):
    cache_key = f'products:{name}:{min_price}:{max_price}'
    cache = r.get(cache_key)

    if cache:
        print("Serving filtered products from cache")
        return json.loads(cache)

    print("Serving filtered products from database")
    query = db.query(Product)

    if name:
        query = query.filter(Product.name.ilike(f'%{name}%'))
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    products = query.all()
    result = jsonable_encoder(products)
    r.set(cache_key, json.dumps(result), ex=60)
    return products



@app.get('/user/{user_id}', response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"error": "User not found"}
    return user


@app.get('/product/{product_id}', response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return {"error": "Product not found"}
    return product



@app.delete('/user/{user_id}', response_model=dict)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"error": "User not found"}
    db.delete(user)
    db.commit()
    r.delete('users')
    return {"message": f"User {user_id} deleted successfully"}


@app.delete('/product/{product_id}', response_model=dict)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return {"error": "Product not found"}
    db.delete(product)
    db.commit()
    r.delete('products')
    return {"message": f"Product {product_id} deleted successfully"}



@app.put('/user/{user_id}', response_model=UserResponse)
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


@app.put('/product/{product_id}', response_model=ProductResponse)
def update_product(product_id: int, product_data: ProductCreate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return {"error": "Product not found"}
    product.name = product_data.name
    product.description = product_data.description
    product.price = product_data.price
    product.user_id = product_data.user_id
    db.commit()
    db.refresh(product)
    r.delete('products')
    return product
