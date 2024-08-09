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
        
        path('report/', views.search_view, name='report'),

        path('create-ticket/', views.inventory_ticket_create_view, name='inventory_ticket_form'),
      
        
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)