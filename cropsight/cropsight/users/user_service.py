import os
from django.core.cache import cache
import re
from typing import Tuple
from django.conf import settings
from requests import Request
from .dtos.response.response_dataclass import CartItemData, HomeScreenData, ProductDetailResponse, ProductListingResponse, UserProfileData, OTPData, LoginResponseData
from .dtos.request.request_dataclass import UserUpdateData
from .exceptions import InvalidPhoneNumberError, OTPValidationError, ProductNotFoundError, UserNotFoundError
import random
from .models import Cart, CartItem, Products, User, UserProfile
from datetime import datetime
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .exceptions import EmailAlreadyExistsError, InvalidDateFormatError
from rest_framework.authtoken.models import Token
from .prediction_service import PredictionService
from django.conf import settings

class UserService:
    @staticmethod
    def validate_phone_number(phone_number: str) -> bool:
        pattern = r'^\+?1?\d{9,15}$'
        if not re.match(pattern, phone_number):
            raise InvalidPhoneNumberError("Invalid phone number format")
        return True

    @staticmethod
    def generate_otp() -> str:
        return "123456"
        # return str(random.randint(100000, 999999))

    @staticmethod
    def send_sms(phone_number: str, message: str) -> bool:
        # Integrate with your SMS service here
        # For development, just print
        print(f"SMS to {phone_number}: {message}")
        return True

    def initiate_login(self, phone_number: str) -> Tuple[UserProfileData, str]:
        self.validate_phone_number(phone_number)
        
        otp = self.generate_otp()
        # cache_key = f"login_otp_{phone_number}"
        # cache.set(cache_key, otp, timeout=300)  # 5 minutes expiry
        
        self.send_sms(phone_number, f"Your OTP is: {otp}")
        
        user, created = User.objects.get_or_create(
            phone_number=phone_number,
            defaults={'is_active': True}
        )
        user.otp = otp
        user.save()
        
        return UserProfileData(
            id=user.id,
            phone_number=user.phone_number
        ), otp

    def verify_otp(self, otp_data: OTPData) -> UserProfileData:
        user = User.objects.filter(phone_number=otp_data.phone_number).first()
        if not user:
            raise UserNotFoundError("User not found")
        user_otp = user.otp
        
        
        if not user_otp or user_otp != otp_data.otp:
            raise OTPValidationError("Invalid OTP")
        user.otp = None
        user.is_phone_verified = True
        user.save()
        user_resp =  UserProfileData.genete_response(user)
        token, created = Token.objects.get_or_create(user=user)
        return LoginResponseData(user=user_resp, token=token.key)

    def get_profile(self, user_id: int) -> UserProfileData:
        try:
            user = User.objects.get(id=user_id)
            return UserProfileData.genete_response(user)
        except User.DoesNotExist:
            raise UserNotFoundError("User not found")
        

    def validate_email(self, email: str, user_id: int) -> bool:
        """Validate email format and check for duplicates"""
        try:
            validate_email(email)
            # Check if email exists for other users
            if User.objects.exclude(id=user_id).filter(email=email).exists():
                raise EmailAlreadyExistsError("This email is already registered")
            return True
        except ValidationError:
            return False

    def validate_date_format(self, date_string: str):
        """Validate and convert date string to date object"""
        try:
            return datetime.strptime(date_string, '%Y-%m-%d').date()
        except ValueError:
            raise InvalidDateFormatError("Invalid date format. Use YYYY-MM-DD")

    def update_profile(self, user_id: int, update_data: UserUpdateData) -> UserProfileData:
        """Update user profile with provided data"""
        try:
            user = User.objects.get(id=user_id)
            
            # Update first name if provided
            if update_data.first_name is not None or update_data.last_name is not None:
                # Concatenate first and last name, ensuring that both are stripped of extra spaces
                user.name = f"{update_data.first_name.strip() if update_data.first_name else ''} {update_data.last_name.strip() if update_data.last_name else ''}".strip()
            

            if update_data.email is not None:
                email = update_data.email.strip().lower()
                if email:  # Only validate if email is not empty
                    self.validate_email(email, user_id)
                user.email = email
            
            # Update date of birth if provided
            if update_data.date_of_birth is not None:
                user.date_of_birth = update_data.date_of_birth
            
            user.save()
            
            return UserProfileData.genete_response(user)
            
        except User.DoesNotExist:
            raise UserNotFoundError("User not found")


    def predict_disease(self, request: Request):
        image = request.FILES.get('image')
        model_path = os.path.join(settings.BASE_DIR, "comb_cnn_model_state_dict.pth")
        service = PredictionService(model_path=model_path, class_names=['Early_Blight', 'Healthy', 'Late_Blight'])
        result = service.predict(image)
        return result
    

    def get_home_data(self, request: Request):
        user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
        crops = user_profile.list_of_crops
        products = Products.objects.order_by('?')[:10]

        return HomeScreenData.generate_response(products, crops)
    

    def get_product_listing_data(self, request: Request):
        #apply filters based on search, and also on categories
        search = request.GET.get('search')
        category = request.GET.get('category')
        
        products = Products.objects.all()
        if search:
            products = products.filter(name__icontains=search)

        if category:
            products = products.filter(category__name__icontains=category)

        data = ProductListingResponse.generate_response(products)
        return data
        

    def add_to_cart(self, user, product_id):
        cart, _= Cart.objects.get_or_create(user=user)
        product = Products.objects.get(id=product_id)
        cart_item, created = cart.items.get_or_create(product=product)
        if not created:
            cart_item.quantity += 1
            cart_item.save()

        cart.total_price += product.price
        cart.quantity += 1
        cart.save()
        #get all cart item

        all_cart_items = cart.items.all()
        cart_item_data = CartItemData.generate_response(all_cart_items)
        # CartItemData.generate_response(cart_item)

        return cart_item_data
    
    def remove_from_cart(self, user, product_id):
        cart, _ = Cart.objects.get_or_create(user=user)
        product = Products.objects.get(id=product_id)

        try:
            cart_item = cart.items.get(product=product)

            if cart_item.quantity > 1:
                # Decrease quantity if more than 1
                cart_item.quantity -= 1
                cart_item.save()
                cart.total_price -= product.price
                cart.quantity -= 1
            else:
                # Remove the item if quantity is 1 (after decrement, it would be 0)
                cart.total_price -= product.price
                cart.quantity -= 1
                cart_item.delete()

            cart.save()

        except CartItem.DoesNotExist:
            pass  # Item is not in cart, nothing to remove

        # Return updated cart items
        all_cart_items = cart.items.all()
        cart_item_data = CartItemData.generate_response(all_cart_items)
        return cart_item_data
    
    def get_cart(self, user):
        cart,_ = Cart.objects.get_or_create(user=user)
        return CartItemData.generate_response(cart.items.all())
    
    def clear_cart(self, user):
        cart, _ = Cart.objects.get_or_create(user=user)
        cart.items.all().delete()
        cart.total_price = 0
        cart.quantity = 0
        cart.save()
        return CartItemData.generate_response(cart.items.all())
    

    def get_product_detail(self, request, product_id):
        product = Products.objects.filter(id=product_id).first()
        if not product:
            raise ProductNotFoundError("Product not found")
        return ProductDetailResponse.generate_response(product)