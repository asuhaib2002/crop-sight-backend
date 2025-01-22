from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from typing import ClassVar

class CustomUserManager(UserManager):
    """Custom manager for User model with phone_number as the unique identifier."""
    def _create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("Phone number must be set")
        user = self.model(phone_number=phone_number, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(phone_number, password, **extra_fields)

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self._create_user(phone_number, password, **extra_fields)


class User(AbstractUser):
    """
    Custom user model for cropsight-backend with phone_number as primary identifier.
    """
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in format: '+999999999'. Up to 15 digits allowed."
    )

    # Remove unused fields
    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]
    username = None  # type: ignore[assignment]

    # Custom fields
    name = models.CharField(_("Name of User"), blank=True, max_length=255)
    phone_number = models.CharField(
        _("Phone Number"),
        max_length=15,
        validators=[phone_regex],
        unique=True,
        help_text=_("Required. Format: +999999999")
    )
    email = models.EmailField(_("Email Address"), null=True)
    date_of_birth = models.DateField(_("Date of Birth"), null=True)
    is_phone_verified = models.BooleanField(_("Phone Verified"), default=False)
    otp = models.CharField(_("OTP"), max_length=6, null=True)
    profile_picture = models.ImageField(_("Profile Picture"), upload_to="profile_pictures/", null=True)

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    objects: ClassVar[UserManager] = CustomUserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"pk": self.id})

    def __str__(self):
        return self.phone_number