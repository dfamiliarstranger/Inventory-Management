from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [ 
   path('raw-material-entry/', views.raw_material_entry, name='raw_material_entry'),
   path('raw-material-history/', views.raw_material_history, name='raw_material_history'),   
   path('inventory_list/', views.inventory_list, name='inventory_list'),   
   path('third-party-production_form/', views.create_production, name='third_party_production_form'),   
   path('tp_dashboard/', views.td_dashboard, name='third_party'),   
]

