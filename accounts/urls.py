from django.urls import path

from .views import LoginView, MeView, RegisterView, SetUserRolesView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('me/', MeView.as_view(), name='me'),
    path('users/<int:user_id>/roles/', SetUserRolesView.as_view(), name='set-user-roles'),
]
