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
        path('ticket-record/', views.inventory_ticket_list, name='inventory_ticket_record'),
      
        path('expense/', views.expense_list, name='expense_list'),
        path('expense/create/', views.create_expense, name='create_expense'),
        path('update/<int:expense_id>/', views.update_expense, name='update_expense'),
        path('delete/<int:expense_id>/', views.delete_expense, name='delete_expense'),
        ]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)