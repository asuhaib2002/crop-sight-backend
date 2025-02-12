from django.urls import path
from .views import AddToCartApiView, CartApiView, ClearCartApiView, HomeApiView, LoginView, PredictionApiView, ProductListApiView, ProductdetailApiView, RemoveFromCartApiView, UpdateProfileView, VerifyOTPView, UserProfileView

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('user/profile/', UserProfileView.as_view(), name='user-profile'),
    path('user/profile/update/', UpdateProfileView.as_view(), name='update-user-profile'),
    path('predict/', PredictionApiView.as_view(), name='predict'),
    path('home/', HomeApiView.as_view(), name='home'),
    path('products/list/', ProductListApiView.as_view(), name='product-list'),
    path('products/details/', ProductdetailApiView.as_view(), name='add-to-cart'),
    path('products/add-to-cart/', AddToCartApiView.as_view(), name='add-to-cart'),
    path('products/remove-from-cart/', RemoveFromCartApiView.as_view(), name='remove-from-cart'),
    path('cart/', CartApiView.as_view(), name='cart'),    
    path('cart/clear/', ClearCartApiView.as_view(), name='remove-from-cart')
]