from fastapi import APIRouter
from fastapi import Depends
from app.database import get_db
from app.schemas.schema import ProductCreate,ProductResponse
from sqlalchemy.orm import Session
from app.models.models import Product
from app.redis_cache import r
from app.search.es_client import es
from typing import Optional
from fastapi.encoders import jsonable_encoder
import json

router = APIRouter(prefix="/products", tags=["Products"])



from fastapi import HTTPException

@router.post('/add-product', response_model=ProductResponse)
def add_product(product: ProductCreate, db: Session = Depends(get_db)):
    try:
        new_product = Product(
            id=product.id,
            user_id=product.user_id,
            name=product.name,
            description=product.description,
            price=product.price
        )
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
    except Exception as db_err:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(db_err)}")

    # Clear Redis cache if needed
    try:
        r.delete('products')
    except Exception as redis_err:
        print(f"Redis error: {redis_err}")  # Optional: log it, don't fail the whole request

    # Index the product in Elasticsearch
    try:
        es.index(index='products', id=new_product.id, document={
            'name': new_product.name,
            'description': new_product.description,
            'price': float(new_product.price),  # ensure it's serializable
            'user_id': new_product.user_id
        })
    except Exception as es_err:
        print(f"Elasticsearch error: {es_err}")  # Optional: log it, don't fail the whole request

    return ProductResponse.from_orm(new_product)



# Get all products with filtering 
@router.get('/products', response_model=list[ProductResponse])
def get_products(
    name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    cache_key = f'products'
    cache = r.get(cache_key)

    if cache:
        print("Serving products from cache")
        return json.loads(cache)

    query = db.query(Product)
    if name:
        es_response = es.search(index='products', body={"query": {"match": {"name": name}}})
        hits = es_response['hits']['hits']
        products = []
        for hit in hits:
            source = hit['_source']
            products.append({
                'id': hit['_id'],
                'name': source['name'],
                'description': source['description'],
                'price': source['price'],
                'user_id': source['user_id']
            })
        print("Products fetched from Elasticsearch")
        return products
    print("Servig products from database")
    products = query.all()
    result = jsonable_encoder(products)
    r.set(cache_key, json.dumps(result), ex=60)
    return products

# Get a product by ID
@router.get('/product/{product_id}', response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return {"error": "Product not found"}
    return product


@router.delete('/product/{product_id}', response_model=dict)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return {"error": "Product not found"}
    db.delete(product)
    db.commit()
    r.delete('products')
    return {"message": f"Product {product_id} deleted successfully"}


@router.put('/product/{product_id}', response_model=ProductResponse)
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