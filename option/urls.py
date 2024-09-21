from django.urls import path
from . import views

urlpatterns = [
    #product type
    path('product_types/', views.product_type_list, name='product_type_list'),
    path('product_types/create/', views.product_type_create, name='product_type_create'),
    path('product_types/<int:id>/update/', views.product_type_update, name='product_type_update'),
    path('product_types/<int:id>/delete/', views.product_type_delete, name='product_type_delete'),

    # colors
    path('color/', views.color_list, name='color_list'),
    path('color/create/', views.color_create, name='color_create'),
    path('color/<int:id>/update/', views.color_update, name='color_update'),
    path('color/<int:id>/delete/', views.color_delete, name='color_delete'),

    #Supplier
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/create/', views.supplier_create, name='supplier_create'),
    path('suppliers/<int:id>/update/', views.supplier_update, name='supplier_update'),
    path('suppliers/<int:id>/delete/', views.supplier_delete, name='supplier_delete'),

    #Supplier
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/create/', views.customer_create, name='customer_create'),
    path('customers/<int:id>/update/', views.customer_update, name='customer_update'),
    path('customers/<int:id>/delete/', views.customer_delete, name='customer_delete'),


    #Staff
    path('staff_create/', views.staff_creation_view, name='staff_creation'),
    path('staff_list/', views.staff_list_view, name='staff_list'),
    # path('staff_reveal/<str:username>/', views.reveal_password_view, name='reveal_password'),
     path('delete_user/<int:pk>/', views.delete_user, name='delete_user'),
]
