from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [ 
        path('create_product/', views.product_list_create, name="create_product"),
        path('<int:product_id>/update/', views.product_update, name='update_product'),
        path('<int:pk>/delete/', views.product_delete, name='product_delete'),
        path('product-list/', views.product_list, name='product_list'),
]

