from django.urls import path, include
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path('', views.affordability, name='affordability'),
    path('select/', views.affordability_select, name='affordability_select'),
    path('wwc/', views.affordability_wwc, name='affordability_wwc'),
    path('overview/<int:gov_id>/', views.affordability_overview, name='affordability_overview'),
    path('index/<int:gov_id>/', views.affordability_index, name='affordability_index'),

]
