from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [ 
        path('', views.user_login, name="user_login"),
        path('user_logout', views.user_logout, name="user_logout"),
        path('home', views.home, name="home"),

      



     

        #Invoice
        path('invoice/', views.invoice, name="invoice"),
        path('print_invoice/', views.print_invoice, name='print_invoice'),

        #Settings
        path('settings/', views.settings, name="settings"),

      

        #ticket
        path('ticket/', views.ticket_form, name='ticket_form'),
        path('ticket/<int:stock_id>/', views.ticket_update, name='ticket_update'),

      

        path('report/', views.search_view, name='report'),
        path('production_report/', views.production_report, name='production_report'),
        path('sales_report/', views.sales_report, name='sales_report'),
        path('purchase_report/', views.purchase_report, name='purchase_report'),
        path('ticket_report/', views.ticket_report, name='ticket_report'),

      
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)