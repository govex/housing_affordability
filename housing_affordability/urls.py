from django.urls import path, include
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path('', views.home, name='housing_home'),
    path('select/', views.affordability_select, name='housing_select'),
    path('comp/', views.affordability_comp_select, name='housing_comp_select'),
    path('comp/<int:comp_option>', views.affordability_comp, name='housing_comp'),
    path('overview/<int:gov_id>/', views.affordability_overview, name='housing_overview'),
    path('index/<int:gov_id>/', views.affordability_index, name='housing_affordability'),
    path('about/', views.about, name='housing_about')

]
