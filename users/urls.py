from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, LoginView, LogoutView, UserDetailView, ManagedArtistViewSet

router = DefaultRouter()
router.register(r'managed-artists', ManagedArtistViewSet, basename='managed-artist')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('me/', UserDetailView.as_view(), name='me'),
    path('', include(router.urls)),
]
