from django.urls import path
from . import views

urlpatterns = [ 
        path('', views.user_login, name="user_login"),
        path('user_logout', views.user_logout, name="user_logout"),
        path('home', views.home, name="home"),

        # Cap Product URLS
        path('cap/', views.cap, name="cap"),
        path('cap/add/', views.create_cap, name="create_cap"),

        

        # Preform Product URLS
        path('preform/', views.preform, name="preform"),
        path('preform/add', views.create_preform, name="create_preform"),
        path('preform_type', views.preform_type, name="preform_type"),

        # Supplier Client URLS
        path('supplier/', views.supplier, name="supplier"),
        path('supplier/add', views.create_supplier, name="create_supplier"),

        # Customer Client URLS
        path('customer/', views.customer, name="customer"),
        path('customer/add', views.create_customer, name="create_customer"),

        # Add Stock Items

        path('add_stock/', views.add_stock_item, name="add_stock"),
        path('stock/', views.purchase_history, name="stock"),
        path('stock_list/', views.stock_detail, name="stock_list"),

        # Production
        path('production/', views.production, name="production"),
        path('production_record/', views.production_record, name="record")
]