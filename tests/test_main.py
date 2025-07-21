from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == {"message": "Working"}

def test_get_users():
    response = client.get('/users')
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_products():
    response = client.get('/products')
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_add_user():
    user_data = {
        "id": 136,
        "name": "Test User",
        "email": "testuser@example.com"
    }
    response = client.post('/add-user', json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == "Test User"
    assert data['email'] == "testuser@example.com"

def test_add_product():
    product_data = {
        "id": 136,
        "user_id": 29,
        "name": "Test Product",
        "description": "This is a test product",
        "price": 100
    }
    response = client.post('/add-product', json=product_data)
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == "Test Product"
    assert data['price'] == 100

def test_search_users():
    response = client.get('/users?name=Test')
    assert response.status_code == 200
    users = response.json()
    assert all('Test' in user['name'] for user in users)

def test_search_products():
    response = client.get('/products?min_price=50&max_price=150')
    assert response.status_code == 200
    products = response.json()
    assert all(50 <= product['price'] <= 150 for product in products)

def test_get_user_by_id():
    response = client.get('/user/11')
    assert response.status_code == 200
    assert response.json()['id'] == 29

def test_get_user_not_found():
    response = client.get('/user/8000')
    assert response.status_code == 200
    assert "error" in response.json()

def test_delete_user():
    response = client.delete('/user/11')
    assert response.status_code == 200
    assert "deleted successfully" in response.json()['message']

def test_delete_user_not_found():
    response = client.delete('/user/9999')
    assert response.status_code == 200
    assert "error" in response.json()

def test_update_user():
    # Add user first
    user_data = {"id": 39, "name": "Original Name", "email": "orig@example.com"}
    client.post('/add-user', json=user_data)

    updated_data = {"id": 39, "name": "Updated Name", "email": "updated@example.com"}
    response = client.put('/user/30', json=updated_data)
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == "Updated Name"
    assert data['email'] == "updated@example.com"

def test_update_user_not_found():
    updated_data = {"id": 8000, "name": "No User", "email": "nouser@example.com"}
    response = client.put('/user/9999', json=updated_data)
    assert response.status_code == 200
    assert "error" in response.json()
