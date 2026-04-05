from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.dashboard, name='profile'),
    path('family/', views.family_list, name='family_list'),
    path('family/<int:pk>/', views.family_detail, name='family_detail'),
    path('add-member/', views.add_member, name='add_member'),
    path('tree/', views.visual_tree, name='visual_tree'),
    path('api/tree/', views.family_tree_json, name='family_tree_json'),
    path('family/<int:pk>/edit/', views.edit_member, name='edit_member'),
]