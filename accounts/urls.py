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
    path('grandparent/<str:name>/', views.grandparent_detail, name='grandparent_detail'),
    path('parent/<str:name>/', views.parent_detail, name='parent_detail'),
    path('address/<str:address>/', views.address_detail, name='address_detail'),
    path('add-member/', views.add_member, name='add_member'),
    path('member/<str:name>/', views.member_search, name='member_search'),
    path('tree/', views.visual_tree, name='visual_tree'),
]