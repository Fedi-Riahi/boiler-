from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)

def test_root():
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == {"message": "Working"}

def test_tests  ():
    response = client.get('/users')
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_products():
    response = client.get('/products')
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_add_user():
    user_data = {
        "id": 88,
        "name": "Test User",
        "email": ""
    }
    response = client.post('/add-user', json=user_data)
    assert response.status_code == 200
    assert response.json()['name'] == "Test User"

def test_add_product():
    product_data = {
        "id": 28,
        "user_id": 1,
        "name": "Test Product",
        "description": "This is a test product",
        "price": 100
    }
    response = client.post('/add-product', json=product_data)
    assert response.status_code == 200
    assert response.json()['name'] == "Test Product"
