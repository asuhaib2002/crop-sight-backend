from dataclasses import dataclass
from datetime import datetime
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
