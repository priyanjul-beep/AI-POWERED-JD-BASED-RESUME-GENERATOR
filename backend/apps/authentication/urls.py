from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, LoginView, LogoutView, CurrentUserView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('login/', LoginView.as_view(), name='auth_login'),
    path('logout/', LogoutView.as_view(), name='auth_logout'),
    path('me/', CurrentUserView.as_view(), name='auth_me'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
