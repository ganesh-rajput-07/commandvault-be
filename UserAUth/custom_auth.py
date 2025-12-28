from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.hashers import check_password
from .serializers import RegisterSerializer, UserProfileSerializer

User = get_user_model()


class CustomLoginView(APIView):
    """
    Custom login view with detailed error messages and email verification check.
    """
    
    def post(self, request):
        email = request.data.get('email', '').strip()
        password = request.data.get('password', '')
        
        # Validate required fields
        if not email or not password:
            return Response({
                'error': 'Email and password are required',
                'field': 'general'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                'error': 'No account found with this email address. Please check your email or register for a new account.',
                'field': 'email'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if account is active
        if not user.is_active:
            return Response({
                'error': 'This account has been deactivated. Please contact support for assistance.',
                'field': 'general'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Check if email is verified (only for non-Google accounts)
        if not user.is_google_account and not user.is_email_verified:
            return Response({
                'error': 'Please verify your email before logging in. Check your inbox for the verification link.',
                'field': 'email',
                'code': 'EMAIL_NOT_VERIFIED',
                'email': user.email
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Verify password
        if not check_password(password, user.password):
            return Response({
                'error': 'Incorrect password. Please try again or use "Forgot Password" to reset it.',
                'field': 'password'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserProfileSerializer(user, context={'request': request}).data,
            'message': 'Login successful'
        }, status=status.HTTP_200_OK)


class CustomRegisterView(APIView):
    """
    Custom registration view with detailed validation error messages.
    """
    
    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '')
        
        errors = {}
        
        # Validate email
        if not email:
            errors['email'] = 'Email is required'
        elif User.objects.filter(email=email).exists():
            errors['email'] = 'An account with this email already exists. Try logging in instead.'
        elif '@' not in email or '.' not in email.split('@')[-1]:
            errors['email'] = 'Please enter a valid email address'
        
        # Validate username
        if not username:
            errors['username'] = 'Username is required'
        elif len(username) < 3:
            errors['username'] = 'Username must be at least 3 characters long'
        elif len(username) > 20:
            errors['username'] = 'Username must be less than 20 characters'
        elif User.objects.filter(username=username).exists():
            errors['username'] = 'This username is already taken. Please choose another one.'
        elif not username.replace('-', '').replace('_', '').isalnum():
            errors['username'] = 'Username can only contain letters, numbers, hyphens, and underscores'
        
        # Validate password
        if not password:
            errors['password'] = 'Password is required'
        elif len(password) < 8:
            errors['password'] = 'Password must be at least 8 characters long'
        
        # Return errors if any
        if errors:
            return Response({
                'errors': errors,
                'message': 'Please fix the errors below'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Use the serializer to create the user
        serializer = RegisterSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            return Response({
                'message': 'Registration successful! Please check your email to verify your account.',
                'email': user.email,
                'username': user.username,
                'email_verification_required': not user.is_google_account
            }, status=status.HTTP_201_CREATED)
        else:
            # This shouldn't happen if our validation above is correct
            return Response({
                'errors': serializer.errors,
                'message': 'Registration failed'
            }, status=status.HTTP_400_BAD_REQUEST)
