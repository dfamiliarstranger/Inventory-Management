from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [ 
        path('', views.user_login, name="user_login"),
        path('user_logout', views.user_logout, name="user_logout"),
        path('home', views.home, name="home"),

        # Cap Product URLS
        path('cap/', views.cap, name="cap"),
        path('cap/add/', views.create_cap, name="create_cap"),

        # Preform Product URLS
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
        path('production_record/', views.production_record, name="record"),

        #Sales
        path('sales_form/', views.sales_form, name="sales_form"),
        path('sales_record/', views.sales_record, name="sales_record"),

        #Notification
        path('notify/', views.show_notification, name="notify"),
        path('clear-notifications/', views.clear_notifications, name='clear_notifications'),
        path('delete-notification/<int:notification_id>/', views.delete_notification, name='delete_notification'),

        #Invoice
        path('invoice/', views.invoice, name="invoice"),
        path('print_invoice/', views.print_invoice, name='print_invoice'),

        #Settings
        path('settings/', views.settings, name="settings"),

        #Color
        path('color/', views.color, name="color"),

        #Product
        path('product/', views.products, name="product"),

        #ticket
        path('ticket/', views.ticket_form, name='ticket_form'),
        path('ticket/<int:stock_id>/', views.ticket_update, name='ticket_update'),

        path('error/', views.error_page, name='error_page'),

        path('report/', views.search_view, name='report'),
        path('production_report/', views.production_report, name='production_report'),
        path('sales_report/', views.sales_report, name='sales_report'),
        path('purchase_report/', views.purchase_report, name='purchase_report'),
        path('ticket_report/', views.ticket_report, name='ticket_report'),

        path('bottle/', views.add_bottle, name='add_bottle'),
        path('remove-stock/<int:item_id>/', views.remove_stock_item, name='remove_stock'),
        path('reverse_sale/<int:sale_id>/', views.reverse_sale, name='reverse_sale'),
        path('production/reverse/<int:production_id>/', views.reverse_production, name='reverse_production'),

        path('update_stock/<int:pk>/', views.update_stock_item, name='update_stock'),
        path('delete_stock/<int:pk>/', views.delete_stock_item, name='delete_stock'),


        path('update_supplier/<int:pk>/', views.update_supplier, name='update_supplier'),
        path('delete_supplier/<int:pk>/', views.delete_supplier, name='delete_supplier'),


        path('update_customer/<int:pk>/', views.update_customer, name='update_customer'),
        path('delete_customer/<int:pk>/', views.delete_customer, name='delete_customer'),

        path('cap_name/delete/<int:pk>/', views.delete_cap_name, name='delete_cap_name'),

        path('cap/delete/<int:pk>/', views.delete_cap, name='delete_cap'),
        path('preform_type/delete/<int:pk>/', views.delete_preform_type, name='delete_preform_type'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)