from django.urls import path
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login_user, name='login'),
    path('logout', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('home', views.home, name='home'),
    path('repeat_play2_outcome', views.repeat_play2_outcome, name='repeat_play2_outcome')
]

urlpatterns += router.urls

