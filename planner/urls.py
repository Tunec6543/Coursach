from django.urls import path

from . import views

app_name = 'planner'

urlpatterns = [
    path('', views.home, name='home'),
    path('plan/', views.plan_detail, name='plan'),
    path('plan/create/', views.plan_create, name='plan_create'),
]
