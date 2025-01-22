from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from datetime import date
from django.core.files.uploadedfile import InMemoryUploadedFile


@dataclass
class PredictionRequestData:
    image: InMemoryUploadedFile
    user_id: int


@dataclass
class UserUpdateData:
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    date_of_birth: Optional[date] = None
