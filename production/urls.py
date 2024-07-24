from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [ 
        path('production_form/', views.create_production, name="production_form"),
        path('production_list/', views.production_list, name="production_list"),  
        path('production/delete/<int:pk>/', views.production_delete, name='production_delete')    
]

