from django.urls import path
from .views import LoginView, UpdateProfileView, VerifyOTPView, UserProfileView

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('user/profile/', UserProfileView.as_view(), name='user-profile'),
    path('user/profile/update/', UpdateProfileView.as_view(), name='update-user-profile'),
    # path('predict/', PredictionView.as_view(), name='predict'),
]