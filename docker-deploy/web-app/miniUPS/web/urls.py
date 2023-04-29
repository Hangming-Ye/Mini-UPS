from django.urls import path

from . import views
appname='web'
urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('query/', views.query, name='query'),
    path('modifypwd/', views.changeProfile, name='change-profile'),
    path('profile/', views.profile, name='profile'),
    path('detail/<int:package_id>/', views.detail, name='package-detail'),
    path('changeLocation/<int:package_id>/', views.changeLoc, name='package-changelocation'),
    path('form/<int:package_id>', views.getSatisfaction, name='user form'),
]