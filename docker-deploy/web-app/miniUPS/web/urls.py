from django.urls import path

from . import views

urlpatterns = [
    path('index/', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('query/', views.query, name='query'),
    path('change-profile/', views.changeProfile, name='change-profile'),
    path('change-profile/done/', views.changedone, name='change-profile-done'),
    path('package/', views.packlist, name='package-list'),
    path('package/<int:package_id>/detail', views.detail, name='package-detail'),
    path('package/<int:package_id>/changelocation', views.changeLoc, name='package-changelocation'),
]