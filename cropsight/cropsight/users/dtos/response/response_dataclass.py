from dataclasses import dataclass
from datetime import datetime
from itertools import product
from typing import Optional
from django.core.files.uploadedfile import InMemoryUploadedFile

@dataclass
class UserProfileData:
    phone_number: str
    id: Optional[int] = None
    name: Optional[str] = None
    email: Optional[str] = None
    created_at: Optional[datetime] = None
    profile_picture: Optional[str] = None

    def genete_response(user):
        return {
            'id': user.id,
            'phone_number': user.phone_number,
            'name': user.name,
            'email': user.email,
            'created_at': user.date_joined.strftime('%Y-%m-%d %H:%M:%S') if user.date_joined else None,
            'profile_picture': user.profile_picture.url if user.profile_picture else None,
            'date_of_birth': user.date_of_birth.strftime('%Y-%m-%d') if user.date_of_birth else None
        }

@dataclass
class OTPData:
    phone_number: str
    otp: str

@dataclass
class PredictionResponseData:
    disease_class: str
    confidence: float
    additional_info: Optional[dict] = None


@dataclass
class LoginResponseData:
    token: str
    user: UserProfileData


@dataclass
class ProductData:
    name: str
    price: float
    description: str
    image: str
    category: str

    def generate_response(product):
        return ProductData(name=product.name, price=product.price, description=product.description, image=product.image.url, category=product.category.name)


@dataclass
class UserCropData:
    crop_name: str

@dataclass
class HomeScreenData:
    products: list[ProductData]
    user_crops: list[UserCropData]

    def generate_response(products: product, user_crops):
        print(user_crops)
        products = [ProductData(name=product.name, price=product.price, description=product.description, image=product.image.url) for product in products]
        user_crops = [UserCropData(crop_name=crop.crop_name) for crop in user_crops] if user_crops else []
        return HomeScreenData(products=products, user_crops=user_crops)
        


@dataclass
class ProductListingResponse:
    products: list[ProductData]

    def generate_response(products):
        products = [ProductData.generate_response(product) for product in products]
        return ProductListingResponse(products=products)
    
@dataclass
class ProductDetailResponse:
    id: int
    name: str
    price: float
    description: str
    image: str
    category: str

    def generate_response(product):
        return ProductDetailResponse(id=product.id, name=product.name, price=product.price, description=product.description, image=product.image.url, category=product.category.name)


@dataclass
class CartItemData:
    product: ProductData
    quantity: int

    @staticmethod
    def generate_response(cart_items):
        return [
            CartItemData(
                product=ProductData.generate_response(cart_item.product),
                quantity=cart_item.quantity
            )
            for cart_item in cart_items
        ]