from django.urls import path
from .views import (
    CustomLoginView, 
    CustomLogoutView, 
    RegisterView, 
    profile_view, 
    edit_profile_view,
    order_history_view
)

app_name = 'accounts'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', profile_view, name='profile'),
    path('profile/edit/', edit_profile_view, name='edit_profile'),
    path('orders/', order_history_view, name='order_history'),
]
