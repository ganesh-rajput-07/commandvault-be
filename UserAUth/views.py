from rest_framework import generics
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import RegisterSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .google_auth import verify_google_token, get_or_create_google_user


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer



class GoogleLoginView(APIView):
    def post(self, request):
        token = request.data.get('token')

        if not token:
            return Response({'error': 'Token required'}, status=400)

        idinfo = verify_google_token(token)
        if not idinfo:
            return Response({'error': 'Invalid Google token'}, status=400)

        user = get_or_create_google_user(idinfo)
        refresh = RefreshToken.for_user(user)

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        })
