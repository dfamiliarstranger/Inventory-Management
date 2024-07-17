from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [ 
    path('form/', views.old_stock_create_view, name='old_stock'),
    path('update/<slug:oid>/', views.update_old_stock, name='update_old_stock'),
    path('delete/<int:pk>/', views.delete_old_stock, name='delete_old_stock'),
    path('list/', views.old_stock, name='stock_list'),
]

