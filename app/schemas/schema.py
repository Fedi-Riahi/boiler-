from pydantic import BaseModel


# User schemas for request and response models
class UserCreate(BaseModel):
    id: int
    name: str
    email: str
    class ConfigDict:
        from_attributes = True

class UserResponse(UserCreate):
    id: int
# Product schemas for request and response models

class ProductCreate(BaseModel):
    id: int
    name: str
    description: str
    price: int
    user_id: int

    class ConfigDict:
        from_attributes = True

class ProductResponse(ProductCreate):
    id: int
    user_id: int

class ErrorResponse(BaseModel):
    error: str
