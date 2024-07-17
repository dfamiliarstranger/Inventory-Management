from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [ 
    path('form/', views.purchase_create_view, name='purchase_form'),
    path('update/<int:pk>/', views.update_purchase, name='update_purchase'),
    path('<int:pk>/delete/', views.purchase_delete, name='purchase_delete'),
    path('list/', views.purchase_list, name='purchase_list'),

    path('stock/', views.inventory_list, name='inventory_list'),
]

