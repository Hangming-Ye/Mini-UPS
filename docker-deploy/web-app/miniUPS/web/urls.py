from django.urls import path

from . import views
appname='web'
urlpatterns = [
    path('index/', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('query/', views.query, name='query'),
    path('modifypwd/', views.changeProfile, name='change-profile'),
    path('profile/', views.profile, name='profile'),
    path('package/<int:package_id>/detail', views.detail, name='package-detail'),
    path('package/<int:package_id>/changelocation', views.changeLoc, name='package-changelocation'),
]