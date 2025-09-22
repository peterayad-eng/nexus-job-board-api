from django.shortcuts import render
from rest_framework import status, permissions, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from .models import User
from .serializers import (
    UserSerializer, UserAdminSerializer, UserRegistrationSerializer, 
    UserLoginSerializer, UserProfileUpdateSerializer, UserPasswordUpdateSerializer,
    UserSummarySerializer
)
from .permissions import IsAdminUserRole, IsOwnerOrAdmin, IsUserOwnerOrAdmin

# Create your views here.
class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Use AdminSerializer for admin users, regular serializer for others
        if request.user.is_admin_user():
            serializer = UserAdminSerializer(request.user)
        else:
            serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserProfileUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            # Return appropriate serializer based on user type
            if request.user.is_admin_user():
                return Response(UserAdminSerializer(request.user).data)
            return Response(UserSerializer(request.user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserPasswordUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        serializer = UserPasswordUpdateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.save()
            update_session_auth_hash(request, user)
            return Response({'message': 'Password updated successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RefreshTokenView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            access_token = str(token.access_token)
            return Response({'access': access_token})
        except Exception as e:
            return Response({'error': 'Invalid refresh token'}, status=status.HTTP_400_BAD_REQUEST)

# Admin-only endpoints
class UserListView(generics.ListAPIView):
    serializer_class = UserAdminSerializer
    permission_classes = [IsAdminUserRole]
    queryset = User.objects.all()

    def get_queryset(self):
        return User.objects.annotate(
            application_count=Count('applications', distinct=True),
            posted_job_count=Count('posted_jobs', distinct=True)
        ).select_related('company').prefetch_related('managed_companies')

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsUserOwnerOrAdmin]
    queryset = User.objects.all()

    def get_serializer_class(self):
        # Admins see full details, users see basic info about themselves
        if self.request.user.is_admin_user():
            return UserAdminSerializer
        return UserSerializer

    def get_queryset(self):
        return User.objects.annotate(
            application_count=Count('applications', distinct=True),
            posted_job_count=Count('posted_jobs', distinct=True)
        ).select_related('company').prefetch_related('managed_companies')

class UserSearchView(generics.ListAPIView):
    serializer_class = UserSummarySerializer
    permission_classes = [IsAdminUserRole]

    def get_queryset(self):
        search_term = self.request.query_params.get('search', '')
        return User.objects.filter(
            Q(username__icontains=search_term) |
            Q(email__icontains=search_term) |
            Q(first_name__icontains=search_term) |
            Q(last_name__icontains=search_term)
        )

class UserStatsView(APIView):
    permission_classes = [IsAdminUserRole]

    def get(self, request):
        stats = {
            'total_users': User.objects.count(),
            'job_seekers': User.objects.filter(user_type='job_seeker').count(),
            'employers': User.objects.filter(user_type='employer').count(),
            'admins': User.objects.filter(user_type='admin').count(),
            'active_users': User.objects.filter(is_active=True).count(),
        }
        return Response(stats)

# User management by admin
class UserActivationView(APIView):
    permission_classes = [IsAdminUserRole]

    def patch(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.is_active = not user.is_active
        user.save()
        action = "activated" if user.is_active else "deactivated"
        return Response({
            'message': f'User {user.username} has been {action}',
            'is_active': user.is_active
        })

