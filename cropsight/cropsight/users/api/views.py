from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.mixins import UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.views import APIView
from rest_framework import status
from django.conf import settings
from ..dtos.response.response_dataclass import UserProfileData, OTPData
from ..dtos.response.cs_response import CSResponse
from ..dtos.request.request_dataclass import UserUpdateData
from ..user_service import UserService
# from ..services.ml_service import MLService
from ..exceptions import EmailAlreadyExistsError, InvalidDateFormatError, InvalidPhoneNumberError, OTPValidationError, UserNotFoundError, ImageProcessingError
from datetime import datetime
from typing import Tuple

from cropsight.users.models import User

from .serializers import UserSerializer


class UserViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = "pk"

    def get_queryset(self, *args, **kwargs):
        assert isinstance(self.request.user.id, int)
        return self.queryset.filter(id=self.request.user.id)

    @action(detail=False)
    def me(self, request):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)



class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def __init__(self):
        self.user_service = UserService()

    def post(self, request):
        try:
            phone_number = request.data.get('phone_number')
            user_data, _ = self.user_service.initiate_login(phone_number)
            return CSResponse.send_response(success=True, data=user_data, message='OTP sent successfully', status=status.HTTP_200_OK)
        except InvalidPhoneNumberError as e:
            return CSResponse.send_response(success=False, error=str(e), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return CSResponse.send_response(success=False, error=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VerifyOTPView(APIView):
    authentication_classes = []
    permission_classes = []
    def __init__(self):
        self.user_service = UserService()

    def post(self, request):
        try:
            otp_data = OTPData(
                phone_number=request.data.get('phone_number'),
                otp=request.data.get('otp')
            )
            user_data = self.user_service.verify_otp(otp_data)
            return CSResponse.send_response(success=True, data=user_data, message='OTP verified successfully', status=status.HTTP_200_OK)
        except OTPValidationError as e:
            return CSResponse.send_response(success=False, error=str(e), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return CSResponse.send_response(success=False, error=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserProfileView(APIView):
    def __init__(self):
        self.user_service = UserService()

    def get(self, request):
        try:
            user_data = self.user_service.get_profile(request.user.id)
            return Response({'user': user_data})
        except UserNotFoundError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def put(self, request):
        try:
            user_data = self.user_service.update_profile(request.user.id, request.data)
            return Response({'user': user_data})
        except UserNotFoundError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateProfileView(APIView):
    def __init__(self):
        self.user_service = UserService()

    def patch(self, request):
        try:
            # Extract optional fields from request
            update_data = UserUpdateData(
                first_name=request.data.get('first_name'),
                last_name=request.data.get('last_name'),
                email=request.data.get('email'),
                date_of_birth=datetime.strptime(request.data['date_of_birth'], '%Y-%m-%d').date() 
                    if request.data.get('date_of_birth') else None
            )
            
            # Update profile
            updated_profile = self.user_service.update_profile(
                user_id=request.user.id,
                update_data=update_data
            )
            
            return Response({
                'message': 'Profile updated successfully',
                'user': updated_profile
            })

        except EmailAlreadyExistsError as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except InvalidDateFormatError as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except UserNotFoundError as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        


class PotatoPredictionApiView(APIView):
    authentication_classes = []
    permission_classes = []

    def __init__(self):
        self.user_service = UserService()


    def post(self, request):
        try:
            prediction_result = self.user_service.predict_disease(request, 'potato')
            return CSResponse.send_response(success=True, data=prediction_result, message='Prediction successful', status=status.HTTP_200_OK)
        except Exception as e:
            return CSResponse.send_response(success=False, error=str(e), status=status.HTTP_400_BAD_REQUEST)

class CottonPredictionApiView(APIView):
    authentication_classes = []
    permission_classes = []

    def __init__(self):
        self.user_service = UserService()


    def post(self, request):
        try:
            prediction_result = self.user_service.predict_disease(request, 'cotton')
            return CSResponse.send_response(success=True, data=prediction_result, message='Prediction successful', status=status.HTTP_200_OK)
        
        except Exception as e:
            return CSResponse.send_response(success=False, error=str(e), status=status.HTTP_400_BAD_REQUEST)
    
class WheatPredictionApiView(APIView):
    authentication_classes = []
    permission_classes = []

    def __init__(self):
        self.user_service = UserService()


    def post(self, request):
        try:
            prediction_result = self.user_service.predict_disease(request, 'wheat')
            return CSResponse.send_response(success=True, data=prediction_result, message='Prediction successful', status=status.HTTP_200_OK)
        except Exception as e:
            return CSResponse.send_response(success=False, error=str(e), status=status.HTTP_400_BAD_REQUEST)
    

class HomeApiView(APIView):

    def __init__(self):
        self.user_service = UserService()

    def get(self, request):
        home_response = self.user_service.get_home_data(request=request)
        return CSResponse.send_response(success=True, message='Home data fetched', data=home_response, status=status.HTTP_200_OK)
    

class ProductListApiView(APIView):

    def __init__(self):
        self.user_service = UserService()

    def get(self, request):
        product_response = self.user_service.get_product_listing_data(request=request)
        return CSResponse.send_response(success=True, message='Home data fetched', status=status.HTTP_200_OK, data=product_response)
    


class ProductdetailApiView(APIView):
    
    def __init__(self):
        self.user_service = UserService()

    def get(self, request):
        product_id = request.GET.get('product_id')
        product_response = self.user_service.get_product_detail(request=request, product_id=product_id)
        return CSResponse.send_response(success=True, message='Product detail fetched', status=status.HTTP_200_OK, data=product_response)


class AddToCartApiView(APIView):


    def __init__(self):
        self.user_service = UserService()

    def post(self, request):
        try:
            product_id = request.data.get('product_id')
            print(product_id)
            data = self.user_service.add_to_cart(request.user, product_id)
            return CSResponse.send_response(success=True, message='Product added to cart', status=status.HTTP_200_OK, data=data)
        except Exception as e:
            return CSResponse.send_response(success=False, error=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class RemoveFromCartApiView(APIView):
    
    def __init__(self):
        self.user_service = UserService()

    def post(self, request):
        try:
            product_id = request.data.get('product_id')
            data = self.user_service.remove_from_cart(request.user, product_id)
            return CSResponse.send_response(success=True, message='Product removed from cart', status=status.HTTP_200_OK, data=data)
        except Exception as e:
            return CSResponse.send_response(success=False, error=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class CartApiView(APIView):
    
    def __init__(self):
        self.user_service = UserService()

    def get(self, request):
        cart_response = self.user_service.get_cart(request.user)
        return CSResponse.send_response(success=True, message='Cart data fetched', status=status.HTTP_200_OK, data=cart_response)
    

class ClearCartApiView(APIView):
    
    def __init__(self):
        self.user_service = UserService()

    def post(self, request):
        try:
            data = self.user_service.clear_cart(request.user)
            return CSResponse.send_response(success=True, message='Cart cleared', status=status.HTTP_200_OK, data=data)
        except Exception as e:
            return CSResponse.send_response(success=False, error=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)