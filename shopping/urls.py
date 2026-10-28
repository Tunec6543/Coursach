from django.urls import path

from . import views

app_name = 'shopping'

urlpatterns = [
    path('', views.shopping_list, name='list'),
    path('pantry/', views.pantry, name='pantry'),
    path('pantry/<int:pk>/delete/', views.pantry_delete, name='pantry_delete'),
]
