from django.core.cache import cache
import re
from typing import Tuple
from django.conf import settings
from .dtos.response.response_dataclass import UserProfileData, OTPData, LoginResponseData
from .dtos.request.request_dataclass import UserUpdateData
from .exceptions import InvalidPhoneNumberError, OTPValidationError, UserNotFoundError
import random
from .models import User
from datetime import datetime
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .exceptions import EmailAlreadyExistsError, InvalidDateFormatError
from rest_framework.authtoken.models import Token

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
