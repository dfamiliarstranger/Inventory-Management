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
        path('production_record/', views.production_record, name="record"),

        #Sales
        path('sales_form/', views.sales_form, name="sales_form"),
        path('sales_record/', views.sales_record, name="sales_record"),

        #Notification
        path('notify/', views.show_notification, name="notify"),
        path('clear-notifications/', views.clear_notifications, name='clear_notifications'),

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
        # URL for rendering the form
        path('ticket/', views.ticket_form, name='ticket_form'),

        # URL for handling form submission and updating the stock record
        path('ticket/<int:stock_id>/', views.ticket_update, name='ticket_update'),

        
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)